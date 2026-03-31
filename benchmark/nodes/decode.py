"""
DecodeMapping node — unmask the AB assignments to reveal variant names.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Union

from pydantic_graph import BaseNode, End, GraphRunContext

from ..models import DecodedTaskResult

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

        # Build lookup from task_id → ABMapping
        mapping_by_task = {m.task_id: m for m in state.ab_mappings}
        task_by_id = {t.id: t for t in state.tasks}

        for score in state.judge_scores:
            mapping = mapping_by_task.get(score.task_id)
            task = task_by_id.get(score.task_id)
            if not mapping or not task:
                logger.warning("No mapping/task for task_id %d", score.task_id)
                continue

            # Decode: A → variant name, B → variant name
            a_name = mapping.a_variant
            b_name = mapping.b_variant

            scores_decoded = {
                a_name: score.scores_a,
                b_name: score.scores_b,
            }
            totals_decoded = {
                a_name: score.total_a,
                b_name: score.total_b,
            }

            # Decode winner
            if score.winner == "A":
                winner_decoded = a_name
            elif score.winner == "B":
                winner_decoded = b_name
            else:
                winner_decoded = "Tie"

            state.decoded_results.append(
                DecodedTaskResult(
                    task_id=score.task_id,
                    tier=task.tier,
                    principle=task.principle,
                    tensions=task.tensions,
                    scores=scores_decoded,
                    totals=totals_decoded,
                    winner=winner_decoded,
                    reasoning=score.overall_reasoning,
                )
            )

        logger.info("Decoded %d task results", len(state.decoded_results))
        return AnalyzeResults()
