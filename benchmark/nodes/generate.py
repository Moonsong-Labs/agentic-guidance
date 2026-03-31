"""
GenerateTasks node — loads or generates the task set.
"""

from __future__ import annotations

import json
import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Union

from pydantic_graph import BaseNode, End, GraphRunContext

from ..models import Task

logger = logging.getLogger(__name__)

# Use TYPE_CHECKING to avoid circular imports at runtime
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..graph import PipelineDeps, PipelineState
    from .run_variants import RunVariants


@dataclass
class GenerateTasks(BaseNode["PipelineState", "PipelineDeps", None]):
    """Load tasks from file or from built-in task data."""

    async def run(
        self, ctx: GraphRunContext["PipelineState", "PipelineDeps"]
    ) -> Union["RunVariants", End[None]]:
        from .run_variants import RunVariants

        state = ctx.state
        config = state.config

        if config.tasks_file:
            path = Path(config.tasks_file)
            logger.info("Loading tasks from %s", path)
            raw = json.loads(path.read_text())
            if isinstance(raw, dict) and "tasks" in raw:
                raw = raw["tasks"]
            state.tasks = [Task.model_validate(t) for t in raw]
        else:
            logger.info("Loading built-in tasks")
            from ..tasks import load_builtin_tasks

            state.tasks = load_builtin_tasks()

        logger.info("Loaded %d tasks across %d tiers", len(state.tasks), len({t.tier for t in state.tasks}))

        # Validate tier distribution
        tier_counts = {}
        for t in state.tasks:
            tier_counts[t.tier] = tier_counts.get(t.tier, 0) + 1
        for tier, count in sorted(tier_counts.items()):
            logger.info("  Tier %d: %d tasks", tier, count)

        return RunVariants()
