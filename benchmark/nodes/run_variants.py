"""
RunVariants node — runs each task against each prompt variant.

Generates responses using pydantic-ai Agent with each variant's system prompt.
"""

from __future__ import annotations

import asyncio
import logging
import time
from dataclasses import dataclass
from typing import Union

from pydantic_ai import Agent

from pydantic_graph import BaseNode, End, GraphRunContext

from ..models import VariantResponse

logger = logging.getLogger(__name__)

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..graph import PipelineDeps, PipelineState
    from .judge import JudgeResponses


@dataclass
class RunVariants(BaseNode["PipelineState", "PipelineDeps", None]):
    """Run each task against each prompt variant to collect responses."""

    async def run(
        self, ctx: GraphRunContext["PipelineState", "PipelineDeps"]
    ) -> Union["JudgeResponses", End[None]]:
        from .judge import JudgeResponses

        state = ctx.state
        deps = ctx.deps
        config = state.config
        sem = asyncio.Semaphore(config.max_concurrent_responses)

        total_calls = len(state.tasks) * len(config.variants) * config.runs_per_variant
        logger.info(
            "Generating %d responses (%d tasks × %d variants × %d runs)",
            total_calls,
            len(state.tasks),
            len(config.variants),
            config.runs_per_variant,
        )

        async def generate_one(
            task_id: int,
            task_prompt: str,
            task_context: str,
            variant_name: str,
            run_idx: int,
        ) -> VariantResponse:
            async with sem:
                system_text = deps.variant_texts[variant_name]
                agent = Agent(
                    config.response_model,
                    system_prompt=system_text,
                )

                user_message = f"Context: {task_context}\n\n{task_prompt}"

                t0 = time.monotonic()
                result = await agent.run(user_message)
                elapsed = (time.monotonic() - t0) * 1000

                state.total_response_calls += 1
                if state.total_response_calls % 20 == 0:
                    logger.info(
                        "  Progress: %d/%d responses generated",
                        state.total_response_calls,
                        total_calls,
                    )

                return VariantResponse(
                    task_id=task_id,
                    variant_name=variant_name,
                    run_index=run_idx,
                    response_text=result.output,
                    model=config.response_model,
                    latency_ms=elapsed,
                )

        # Build all coroutines
        coros = []
        for task in state.tasks:
            for variant in config.variants:
                for run_idx in range(config.runs_per_variant):
                    coros.append(
                        generate_one(
                            task.id,
                            task.prompt,
                            task.context,
                            variant.name,
                            run_idx,
                        )
                    )

        # Execute all
        results = await asyncio.gather(*coros, return_exceptions=True)

        for r in results:
            if isinstance(r, Exception):
                logger.error("Response generation failed: %s", r)
            else:
                state.responses.append(r)

        logger.info(
            "Generated %d responses (%d failures)",
            len(state.responses),
            sum(1 for r in results if isinstance(r, Exception)),
        )

        return JudgeResponses()
