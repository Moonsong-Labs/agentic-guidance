"""
JudgeResponses node — blind AB judging of response pairs.

For each task, randomly assigns A/B labels to variants, then asks the judge
to score both using the full rubric. The judge never sees variant names.
"""

from __future__ import annotations

import asyncio
import itertools
import logging
import random
from dataclasses import dataclass
from typing import Union

from pydantic_ai import Agent
from pydantic_graph import BaseNode, End, GraphRunContext

from ..checkpointing import load_judge_scores, save_judge_scores
from ..config import DIMENSION_LABELS
from ..models import ABMapping, DimensionScore, JudgeScore
from ..rubric import build_judge_system_prompt

logger = logging.getLogger(__name__)

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..graph import PipelineDeps, PipelineState
    from .decode import DecodeMapping


# ---------------------------------------------------------------------------
# Judge output model (structured output from pydantic-ai)
# ---------------------------------------------------------------------------


class JudgeOutput(JudgeScore):
    """The model the judge agent returns as structured output."""

    pass


@dataclass
class JudgeResponses(BaseNode["PipelineState", "PipelineDeps", None]):
    """Score each task's response pair via blind AB judging."""

    async def run(
        self, ctx: GraphRunContext["PipelineState", "PipelineDeps"]
    ) -> Union["DecodeMapping", End[None]]:
        from .decode import DecodeMapping

        state = ctx.state
        config = state.config
        sem = asyncio.Semaphore(config.max_concurrent_judgments)
        config_hash = config.config_hash()

        # Group responses by task_id and variant
        responses_by_task: dict[int, dict[str, str]] = {}
        for r in state.responses:
            if r.task_id not in responses_by_task:
                responses_by_task[r.task_id] = {}
            # For multiple runs, take the first (could average later)
            if r.variant_name not in responses_by_task[r.task_id]:
                responses_by_task[r.task_id][r.variant_name] = r.response_text

        if config.enable_checkpointing and not state.judge_scores:
            state.judge_scores = load_judge_scores(
                config.output_dir,
                config.checkpoint_dir,
                config_hash,
            )
            if state.judge_scores:
                logger.info("Loaded %d checkpointed judge scores", len(state.judge_scores))

        # Create AB mappings with deterministic seed
        rng = random.Random(config.seed)
        state.ab_mappings = []

        for task in state.tasks:
            available_variants = sorted(responses_by_task.get(task.id, {}).keys())
            if len(available_variants) < 2:
                continue
            for left_variant, right_variant in itertools.combinations(available_variants, 2):
                shuffled = [left_variant, right_variant]
                rng.shuffle(shuffled)
                pair_id = f"{task.id}:{min(left_variant, right_variant)}:{max(left_variant, right_variant)}"
                state.ab_mappings.append(
                    ABMapping(
                        task_id=task.id,
                        pair_id=pair_id,
                        a_variant=shuffled[0],
                        b_variant=shuffled[1],
                    )
                )

        completed_pair_ids = {score.pair_id for score in state.judge_scores if score.pair_id}
        pending_mappings = [
            mapping for mapping in state.ab_mappings if mapping.pair_id not in completed_pair_ids
        ]

        logger.info(
            "Judging %d variant pairs (%d pending) with blind AB randomization (seed=%d)",
            len(state.ab_mappings),
            len(pending_mappings),
            config.seed,
        )

        judge_system_prompt = build_judge_system_prompt()
        judge_agent = Agent(
            config.judge_model,
            system_prompt=judge_system_prompt,
            output_type=JudgeOutput,
        )

        async def judge_one(mapping: ABMapping) -> JudgeScore | None:
            async with sem:
                task = next((t for t in state.tasks if t.id == mapping.task_id), None)
                if task is None:
                    return None

                task_responses = responses_by_task.get(task.id, {})
                response_a = task_responses.get(mapping.a_variant, "")
                response_b = task_responses.get(mapping.b_variant, "")

                if not response_a or not response_b:
                    logger.warning("Missing response for task %d, skipping", task.id)
                    return None

                user_prompt = _build_judge_prompt(task, response_a, response_b)

                try:
                    result = await judge_agent.run(user_prompt)
                    state.total_judge_calls += 1

                    if state.total_judge_calls % 10 == 0:
                        logger.info(
                            "  Progress: %d/%d variant pairs judged",
                            state.total_judge_calls,
                            len(state.ab_mappings),
                        )

                    return result.output.model_copy(
                        update={
                            "task_id": mapping.task_id,
                            "pair_id": mapping.pair_id,
                        }
                    )
                except Exception as e:
                    logger.error("Judge failed for task %d: %s", task.id, e)
                    return None

        # Execute judging
        coros = [judge_one(mapping) for mapping in pending_mappings]
        for coro in asyncio.as_completed(coros):
            score = await coro
            if score is None:
                continue
            state.judge_scores.append(score)
            completed_pair_ids.add(score.pair_id)
            if config.enable_checkpointing:
                save_judge_scores(
                    config.output_dir,
                    config.checkpoint_dir,
                    config_hash,
                    state.judge_scores,
                )

        logger.info(
            "Judged %d/%d variant pairs successfully",
            len(state.judge_scores),
            len(state.ab_mappings),
        )

        return DecodeMapping()


def _build_judge_prompt(task, response_a: str, response_b: str) -> str:
    """Build the user prompt for the judge, with no variant names visible."""
    return f"""## Task {task.id} (Tier {task.tier})
**Primary Principle:** {task.principle}
**Context:** {task.context}
**User Prompt:** {task.prompt}

---

### Response A:
{response_a}

---

### Response B:
{response_b}

---

Score both responses on ALL 7 dimensions (0–10 each). Use the full range.
Return your scores as structured output with reasoning for each dimension.
Declare the overall winner (A, B, or Tie) and provide 1–3 sentences of overall reasoning."""
