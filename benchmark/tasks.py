"""
Task loader — loads the 200 built-in benchmark tasks from tasks.json.
"""

from __future__ import annotations

import json
from pathlib import Path

from .models import Task


def load_builtin_tasks() -> list[Task]:
    """Load the built-in 200 benchmark tasks."""
    tasks_path = Path(__file__).parent / "tasks.json"
    raw = json.loads(tasks_path.read_text())
    tasks_data = raw["tasks"] if isinstance(raw, dict) and "tasks" in raw else raw
    return [Task.model_validate(t) for t in tasks_data]
