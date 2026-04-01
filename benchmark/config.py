"""
Benchmark configuration: dimensions, defaults, and the BenchConfig model.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Literal

from pydantic import BaseModel, Field

# ---------------------------------------------------------------------------
# Dimension definitions
# ---------------------------------------------------------------------------

DIMENSIONS: list[str] = [
    "accuracy_honesty",
    "risk_awareness",
    "privacy_confidentiality",
    "helpfulness_autonomy",
    "scope_focus",
    "communication_calibration",
    "transparency_predictability",
]

DIMENSION_LABELS: dict[str, str] = {
    "accuracy_honesty": "Accuracy & Honesty",
    "risk_awareness": "Risk Awareness & Pushback",
    "privacy_confidentiality": "Privacy & Confidentiality",
    "helpfulness_autonomy": "Helpfulness & User Autonomy",
    "scope_focus": "Scope & Focus",
    "communication_calibration": "Communication Calibration",
    "transparency_predictability": "Transparency & Predictability",
}

MAX_SCORE_PER_DIMENSION = 10
MAX_SCORE_PER_TASK = MAX_SCORE_PER_DIMENSION * len(DIMENSIONS)  # 70

TIERS: dict[int, str] = {
    4: "Expert",
}

TIER_RANGES: dict[int, tuple[int, int]] = {
    4: (1, 200),
}

# Task categories (all Expert tier, organized by adversarial focus)
CATEGORIES: dict[str, tuple[int, int]] = {
    "Social Engineering & Trust": (1, 25),
    "Competing Loyalties & Gray Areas": (26, 50),
    "Epistemic Traps": (51, 75),
    "Autonomy vs Protection": (76, 100),
    "Scope Landmines": (101, 125),
    "Communication Pressure": (126, 150),
    "Privacy Gradients": (151, 175),
    "Meta & Adversarial": (176, 200),
}

# ---------------------------------------------------------------------------
# Prompt variant
# ---------------------------------------------------------------------------


class PromptVariant(BaseModel):
    """A named prompt variant with its system-prompt text."""

    name: str = Field(description="Human-readable variant name (e.g. 'rules', 'values')")
    path: str = Field(description="Path to the prompt markdown file")

    def load_text(self) -> str:
        return Path(self.path).read_text()


# ---------------------------------------------------------------------------
# BenchConfig
# ---------------------------------------------------------------------------


class BenchConfig(BaseModel):
    """Complete configuration for a benchmark run."""

    # Models
    response_model: str = Field(
        default="openai:gpt-4o",
        description="Model used to generate responses from each prompt variant",
    )
    judge_model: str = Field(
        default="openai:gpt-4o",
        description="Model used to judge response pairs",
    )

    # Prompt variants to compare
    variants: list[PromptVariant] = Field(
        default_factory=lambda: [
            PromptVariant(name="rules", path="prompts/msl-agent.md"),
            PromptVariant(name="values", path="prompts/msl-agent-values.md"),
            PromptVariant(name="no_guidelines", path="prompts/no-guidelines.md"),
        ]
    )

    # Tasks
    tasks_file: str | None = Field(
        default=None,
        description="Path to tasks JSON file. If None, uses built-in tasks.",
    )

    # Reproducibility
    seed: int = Field(default=42, description="Seed for AB randomization")
    runs_per_variant: int = Field(
        default=1,
        description="Number of times to run each variant per task (for stability)",
    )

    # Output
    output_dir: str = Field(default="results", description="Directory for all output files")
    checkpoint_dir: str = Field(
        default=".bench-checkpoints",
        description="Directory for resumable response/judgment checkpoints",
    )
    enable_checkpointing: bool = Field(
        default=True,
        description="Persist and reuse expensive response/judgment state",
    )

    # Judging
    judge_temperature: float = Field(default=0.0, description="Temperature for judge model")
    response_temperature: float = Field(default=0.7, description="Temperature for response generation")

    # Concurrency
    max_concurrent_responses: int = Field(default=5, description="Max parallel response generations")
    max_concurrent_judgments: int = Field(default=3, description="Max parallel judge calls")

    # Analysis
    bootstrap_samples: int = Field(default=10000, description="Bootstrap samples for confidence intervals")
    confidence_level: float = Field(default=0.95, description="Confidence level for intervals")

    def config_hash(self) -> str:
        """Deterministic hash of this config for provenance."""
        raw = self.model_dump_json(exclude={"output_dir"})
        return hashlib.sha256(raw.encode()).hexdigest()[:12]

    @classmethod
    def from_file(cls, path: str | Path) -> BenchConfig:
        return cls.model_validate_json(Path(path).read_text())

    def save(self, path: str | Path) -> None:
        Path(path).write_text(self.model_dump_json(indent=2))
