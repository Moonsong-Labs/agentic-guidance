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

from ..checkpointing import load_responses, save_responses
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
        config_hash = config.config_hash()

        if config.enable_checkpointing and not state.responses:
            state.responses = load_responses(
                config.output_dir,
                config.checkpoint_dir,
                config_hash,
            )
            if state.responses:
                logger.info("Loaded %d checkpointed responses", len(state.responses))

        total_calls = len(state.tasks) * len(config.variants) * config.runs_per_variant
        existing_keys = {
            (response.task_id, response.variant_name, response.run_index)
            for response in state.responses
        }
        pending_calls = total_calls - len(existing_keys)
        logger.info(
            "Generating %d responses (%d tasks × %d variants × %d runs, %d pending)",
            total_calls,
            len(state.tasks),
            len(config.variants),
            config.runs_per_variant,
            pending_calls,
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
                    response_key = (task.id, variant.name, run_idx)
                    if response_key in existing_keys:
                        continue
                    coros.append(
                        generate_one(
                            task.id,
                            task.prompt,
                            task.context,
                            variant.name,
                            run_idx,
                        )
                    )

        failures = 0
        for coro in asyncio.as_completed(coros):
            try:
                response = await coro
            except Exception as exc:
                failures += 1
                logger.error("Response generation failed: %s", exc)
                continue

            state.responses.append(response)
            existing_keys.add((response.task_id, response.variant_name, response.run_index))
            if config.enable_checkpointing:
                save_responses(
                    config.output_dir,
                    config.checkpoint_dir,
                    config_hash,
                    state.responses,
                )

        logger.info(
            "Generated %d responses (%d failures)",
            len(state.responses),
            failures,
        )

        return JudgeResponses()
