"""
Graph pipeline definition and shared state.

The pipeline:
  GenerateTasks → RunVariants → JudgeResponses → DecodeMapping → AnalyzeResults → End
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field

from pydantic_graph import Graph

from .config import BenchConfig
from .models import (
    ABMapping,
    DecodedTaskResult,
    JudgeScore,
    RunResult,
    Task,
    VariantResponse,
)
from .nodes import (
    AnalyzeResults,
    DecodeMapping,
    GenerateTasks,
    JudgeResponses,
    RunVariants,
)


# ---------------------------------------------------------------------------
# Pipeline state — flows through GraphRunContext.state
# ---------------------------------------------------------------------------


@dataclass
class PipelineState:
    """Mutable state that accumulates data as nodes execute."""

    config: BenchConfig
    tasks: list[Task] = field(default_factory=list)
    responses: list[VariantResponse] = field(default_factory=list)
    ab_mappings: list[ABMapping] = field(default_factory=list)
    judge_scores: list[JudgeScore] = field(default_factory=list)
    decoded_results: list[DecodedTaskResult] = field(default_factory=list)
    run_result: RunResult | None = None

    # Counters
    total_response_calls: int = 0
    total_judge_calls: int = 0
    start_time: float = field(default_factory=time.time)


# ---------------------------------------------------------------------------
# Pipeline deps — immutable dependencies (prompt texts, etc.)
# ---------------------------------------------------------------------------


@dataclass
class PipelineDeps:
    """Immutable dependencies for the pipeline."""

    variant_texts: dict[str, str]  # variant_name → system prompt text


# ---------------------------------------------------------------------------
# The graph
# ---------------------------------------------------------------------------

bench_graph = Graph(
    nodes=[
        GenerateTasks,
        RunVariants,
        JudgeResponses,
        DecodeMapping,
        AnalyzeResults,
    ],
    name="BenchmarkPipeline",
)
