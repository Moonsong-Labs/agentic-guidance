"""
Helpers for resumable benchmark checkpoints.
"""

from __future__ import annotations

import json
from pathlib import Path

from .models import JudgeScore, VariantResponse


def checkpoint_root(output_dir: str, checkpoint_dir: str, config_hash: str) -> Path:
    return Path(output_dir) / checkpoint_dir / config_hash


def responses_path(output_dir: str, checkpoint_dir: str, config_hash: str) -> Path:
    return checkpoint_root(output_dir, checkpoint_dir, config_hash) / "responses.json"


def judgments_path(output_dir: str, checkpoint_dir: str, config_hash: str) -> Path:
    return checkpoint_root(output_dir, checkpoint_dir, config_hash) / "judge_scores.json"


def ensure_checkpoint_dir(output_dir: str, checkpoint_dir: str, config_hash: str) -> Path:
    root = checkpoint_root(output_dir, checkpoint_dir, config_hash)
    root.mkdir(parents=True, exist_ok=True)
    return root


def load_responses(output_dir: str, checkpoint_dir: str, config_hash: str) -> list[VariantResponse]:
    path = responses_path(output_dir, checkpoint_dir, config_hash)
    if not path.exists():
        return []
    raw = json.loads(path.read_text())
    return [VariantResponse.model_validate(item) for item in raw]


def save_responses(
    output_dir: str,
    checkpoint_dir: str,
    config_hash: str,
    responses: list[VariantResponse],
) -> Path:
    ensure_checkpoint_dir(output_dir, checkpoint_dir, config_hash)
    path = responses_path(output_dir, checkpoint_dir, config_hash)
    path.write_text(json.dumps([response.model_dump(mode="json") for response in responses], indent=2))
    return path


def load_judge_scores(output_dir: str, checkpoint_dir: str, config_hash: str) -> list[JudgeScore]:
    path = judgments_path(output_dir, checkpoint_dir, config_hash)
    if not path.exists():
        return []
    raw = json.loads(path.read_text())
    return [JudgeScore.model_validate(item) for item in raw]


def save_judge_scores(
    output_dir: str,
    checkpoint_dir: str,
    config_hash: str,
    judge_scores: list[JudgeScore],
) -> Path:
    ensure_checkpoint_dir(output_dir, checkpoint_dir, config_hash)
    path = judgments_path(output_dir, checkpoint_dir, config_hash)
    path.write_text(json.dumps([score.model_dump(mode="json") for score in judge_scores], indent=2))
    return path
