"""
DecodeMapping node — unmask the AB assignments to reveal variant names.
"""

from __future__ import annotations

from collections import defaultdict
import logging
from dataclasses import dataclass
from typing import Union

from pydantic_graph import BaseNode, End, GraphRunContext

from ..models import DecodedTaskResult, DimensionScore

logger = logging.getLogger(__name__)

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..graph import PipelineDeps, PipelineState
    from .analyze import AnalyzeResults


@dataclass
class DecodeMapping(BaseNode["PipelineState", "PipelineDeps", None]):
    """Unmask AB labels to reveal actual variant names."""

    async def run(
        self, ctx: GraphRunContext["PipelineState", "PipelineDeps"]
    ) -> Union["AnalyzeResults", End[None]]:
        from .analyze import AnalyzeResults

        state = ctx.state

        # Build lookup from pair_id → ABMapping
        mapping_by_pair = {m.pair_id: m for m in state.ab_mappings}
        task_by_id = {t.id: t for t in state.tasks}
        task_scores = defaultdict(lambda: defaultdict(lambda: defaultdict(list)))
        task_totals = defaultdict(lambda: defaultdict(list))
        task_reasonings = defaultdict(list)

        for score in state.judge_scores:
            mapping = mapping_by_pair.get(score.pair_id)
            task = task_by_id.get(score.task_id)
            if not mapping or not task:
                logger.warning("No mapping/task for pair_id %s", score.pair_id)
                continue

            decoded = {
                mapping.a_variant: (score.scores_a, score.total_a),
                mapping.b_variant: (score.scores_b, score.total_b),
            }
            for variant_name, (dimension_scores, total_score) in decoded.items():
                task_totals[score.task_id][variant_name].append(total_score)
                for dimension_score in dimension_scores:
                    task_scores[score.task_id][variant_name][dimension_score.dimension].append(
                        dimension_score.score
                    )

            if score.winner == "A":
                winner_decoded = mapping.a_variant
            elif score.winner == "B":
                winner_decoded = mapping.b_variant
            else:
                winner_decoded = "Tie"

            task_reasonings[score.task_id].append(
                f"{mapping.a_variant} vs {mapping.b_variant}: {winner_decoded}. {score.overall_reasoning}"
            )

        state.decoded_results = []
        for task_id, totals_by_variant in sorted(task_totals.items()):
            task = task_by_id.get(task_id)
            if not task:
                continue

            averaged_scores = {}
            averaged_totals = {}
            for variant_name, dimension_lists in task_scores[task_id].items():
                averaged_scores[variant_name] = [
                    DimensionScore(
                        dimension=dimension,
                        score=sum(values) / len(values),
                        reasoning=(
                            f"Average of {len(values)} pairwise judgment(s) for "
                            f"{variant_name} on this task."
                        ),
                    )
                    for dimension, values in dimension_lists.items()
                ]
                averaged_totals[variant_name] = sum(totals_by_variant[variant_name]) / len(
                    totals_by_variant[variant_name]
                )

            max_total = max(averaged_totals.values()) if averaged_totals else 0.0
            winners = [
                variant_name
                for variant_name, total in averaged_totals.items()
                if abs(total - max_total) < 1e-9
            ]
            winner = winners[0] if len(winners) == 1 else "Tie"

            state.decoded_results.append(
                DecodedTaskResult(
                    task_id=task_id,
                    tier=task.tier,
                    principle=task.principle,
                    tensions=task.tensions,
                    scores=averaged_scores,
                    totals=averaged_totals,
                    winner=winner,
                    reasoning=" | ".join(task_reasonings[task_id]),
                )
            )

        logger.info("Decoded %d task results", len(state.decoded_results))
        return AnalyzeResults()
