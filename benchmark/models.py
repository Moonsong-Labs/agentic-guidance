"""
Core data models for the benchmark pipeline.

All models are Pydantic v2 BaseModels, serializable to/from JSON.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Literal

from pydantic import BaseModel, Field

from .config import DIMENSIONS, MAX_SCORE_PER_DIMENSION


# ---------------------------------------------------------------------------
# Task
# ---------------------------------------------------------------------------


class Task(BaseModel):
    """A single benchmark task."""

    id: int
    tier: Literal[1, 2, 3, 4]
    principle: str = Field(description="Primary principle being tested")
    tensions: list[str] = Field(
        default_factory=list,
        description="Dimensions that are in tension for this task",
    )
    context: str = Field(description="Situational context for the task")
    prompt: str = Field(description="The user prompt to send to the agent")
    adversarial_notes: str | None = Field(
        default=None,
        description="What makes this task hard (hidden from judge)",
    )


# ---------------------------------------------------------------------------
# Response
# ---------------------------------------------------------------------------


class VariantResponse(BaseModel):
    """A single response from one prompt variant for one task."""

    task_id: int
    variant_name: str
    run_index: int = Field(default=0, description="Run index when runs_per_variant > 1")
    response_text: str
    model: str
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    latency_ms: float | None = None


# ---------------------------------------------------------------------------
# AB Mapping
# ---------------------------------------------------------------------------


class ABMapping(BaseModel):
    """Maps blinded labels (A/B) to actual variant names for one task."""

    task_id: int
    a_variant: str = Field(description="Variant name assigned to label A")
    b_variant: str = Field(description="Variant name assigned to label B")


# ---------------------------------------------------------------------------
# Judge scores
# ---------------------------------------------------------------------------


class DimensionScore(BaseModel):
    """Score for a single dimension on a single response."""

    dimension: str
    score: int = Field(ge=0, le=MAX_SCORE_PER_DIMENSION)
    reasoning: str = Field(description="Brief justification for this score")


class JudgeScore(BaseModel):
    """Complete judge output for one task's AB pair."""

    task_id: int
    scores_a: list[DimensionScore] = Field(description="Scores for response A")
    scores_b: list[DimensionScore] = Field(description="Scores for response B")
    total_a: int = Field(description="Sum of all dimension scores for A")
    total_b: int = Field(description="Sum of all dimension scores for B")
    winner: Literal["A", "B", "Tie"]
    overall_reasoning: str = Field(description="1-3 sentence summary of key differences")


# ---------------------------------------------------------------------------
# Decoded result (after unmasking)
# ---------------------------------------------------------------------------


class DecodedTaskResult(BaseModel):
    """Decoded result for a single task — variant names revealed."""

    task_id: int
    tier: int
    principle: str
    tensions: list[str]
    scores: dict[str, list[DimensionScore]] = Field(
        description="variant_name → list of DimensionScore"
    )
    totals: dict[str, int] = Field(description="variant_name → total score")
    winner: str = Field(description="Winning variant name or 'Tie'")
    reasoning: str


# ---------------------------------------------------------------------------
# Aggregate results
# ---------------------------------------------------------------------------


class VariantAggregate(BaseModel):
    """Aggregate statistics for one variant."""

    variant_name: str
    total_score: float
    mean_score_per_task: float
    dimension_means: dict[str, float]
    tier_means: dict[int, float]
    wins: int
    losses: int
    ties: int


class BootstrapCI(BaseModel):
    """Bootstrap confidence interval for a score difference."""

    metric: str
    mean_diff: float
    ci_lower: float
    ci_upper: float
    p_value: float
    significant: bool


class RunResult(BaseModel):
    """Complete result of a benchmark run — the final artifact."""

    # Provenance
    run_id: str
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    config_hash: str
    response_model: str
    judge_model: str

    # Raw data
    tasks_count: int
    decoded_results: list[DecodedTaskResult]

    # Aggregates
    variant_aggregates: list[VariantAggregate]
    bootstrap_cis: list[BootstrapCI]

    # Metadata
    total_response_calls: int = 0
    total_judge_calls: int = 0
    total_duration_seconds: float = 0.0
