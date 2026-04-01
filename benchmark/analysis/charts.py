"""
Chart generation for benchmark results.

Produces radar charts, bar charts, and tier breakdowns using matplotlib.
"""

from __future__ import annotations

import math
from pathlib import Path

import matplotlib

matplotlib.use("Agg")  # Non-interactive backend
import matplotlib.pyplot as plt
import numpy as np

from ..config import DIMENSIONS, DIMENSION_LABELS, MAX_SCORE_PER_DIMENSION, TIERS
from ..models import RunResult


# Color palette
COLORS = ["#2563eb", "#dc2626", "#16a34a", "#d97706", "#7c3aed", "#0891b2"]
DIMENSION_LABEL_TO_KEY = {label: key for key, label in DIMENSION_LABELS.items()}


def generate_all_charts(result: RunResult, output_dir: Path) -> None:
    """Generate all charts and save to output_dir."""
    output_dir.mkdir(parents=True, exist_ok=True)

    _radar_chart(result, output_dir / "radar.png")
    _dimension_bar_chart(result, output_dir / "dimensions.png")
    _tier_bar_chart(result, output_dir / "tiers.png")
    _wins_pie_chart(result, output_dir / "wins.png")
    _score_distribution(result, output_dir / "distribution.png")


def _radar_chart(result: RunResult, path: Path) -> None:
    """Radar/spider chart comparing normalized dimension scores."""
    labels = [DIMENSION_LABELS[d] for d in DIMENSIONS]
    num_dims = len(labels)
    angles = np.linspace(0, 2 * np.pi, num_dims, endpoint=False).tolist()
    angles += angles[:1]  # close the polygon

    fig, ax = plt.subplots(figsize=(10, 10), subplot_kw=dict(polar=True))
    dimension_means = _compute_dimension_means(result)
    all_values: list[float] = []

    for i, agg in enumerate(result.variant_aggregates):
        raw_values = dimension_means.get(agg.variant_name, {})
        values = [
            raw_values.get(d, 0.0) / MAX_SCORE_PER_DIMENSION for d in DIMENSIONS
        ]
        all_values.extend(values)
        values += values[:1]
        ax.plot(angles, values, "o-", linewidth=2, label=agg.variant_name, color=COLORS[i % len(COLORS)])
        ax.fill(angles, values, alpha=0.15, color=COLORS[i % len(COLORS)])

    y_min, y_max = _padded_axis_limits(
        all_values,
        padding=0.03,
        lower_bound=0.0,
        upper_bound=1.0,
        step=0.05,
    )
    tick_count = 5
    tick_values = np.linspace(y_min, y_max, tick_count)

    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(labels, size=9, wrap=True)
    ax.set_ylim(y_min, y_max)
    ax.set_yticks(tick_values)
    ax.set_yticklabels([f"{round(v * 100):.0f}%" for v in tick_values])
    ax.legend(loc="upper right", bbox_to_anchor=(1.3, 1.1))
    ax.set_title(
        "Dimension Comparison (normalized to 10-point max)",
        size=14,
        fontweight="bold",
        pad=20,
    )

    plt.tight_layout()
    fig.savefig(path, dpi=150, bbox_inches="tight")
    plt.close(fig)


def _dimension_bar_chart(result: RunResult, path: Path) -> None:
    """Grouped bar chart of mean scores per dimension."""
    labels = [DIMENSION_LABELS[d] for d in DIMENSIONS]
    x = np.arange(len(labels))
    width = 0.8 / len(result.variant_aggregates)
    dimension_means = _compute_dimension_means(result)

    fig, ax = plt.subplots(figsize=(14, 6))
    all_values: list[float] = []

    for i, agg in enumerate(result.variant_aggregates):
        values = [dimension_means.get(agg.variant_name, {}).get(d, 0.0) for d in DIMENSIONS]
        all_values.extend(values)
        offset = (i - len(result.variant_aggregates) / 2 + 0.5) * width
        bars = ax.bar(x + offset, values, width, label=agg.variant_name, color=COLORS[i % len(COLORS)])
        # Add value labels on bars
        for bar, val in zip(bars, values):
            ax.text(
                bar.get_x() + bar.get_width() / 2,
                bar.get_height() + 0.1,
                f"{val:.1f}",
                ha="center",
                va="bottom",
                fontsize=8,
            )

    ax.set_ylabel("Mean Score (0–10)")
    ax.set_title("Per-Dimension Mean Scores", fontweight="bold")
    ax.set_xticks(x)
    ax.set_xticklabels(labels, rotation=30, ha="right", fontsize=9)
    ax.set_ylim(
        *_padded_axis_limits(
            all_values,
            padding=0.25,
            lower_bound=0.0,
            upper_bound=10.5,
            step=0.5,
        )
    )
    ax.legend()
    ax.grid(axis="y", alpha=0.3)

    plt.tight_layout()
    fig.savefig(path, dpi=150, bbox_inches="tight")
    plt.close(fig)


def _compute_dimension_means(result: RunResult) -> dict[str, dict[str, float]]:
    """Recompute per-dimension means from decoded results to tolerate older bad aggregates."""
    dimension_scores: dict[str, dict[str, list[float]]] = {
        agg.variant_name: {dimension: [] for dimension in DIMENSIONS}
        for agg in result.variant_aggregates
    }

    for decoded in result.decoded_results:
        for variant_name, scores in decoded.scores.items():
            if variant_name not in dimension_scores:
                continue
            for score in scores:
                dim_key = DIMENSION_LABEL_TO_KEY.get(score.dimension, score.dimension)
                if dim_key in dimension_scores[variant_name]:
                    dimension_scores[variant_name][dim_key].append(score.score)

    return {
        variant_name: {
            dimension: (
                float(np.mean(values)) if values else agg.dimension_means.get(dimension, 0.0)
            )
            for dimension, values in per_dimension.items()
        }
        for agg in result.variant_aggregates
        for variant_name, per_dimension in [(agg.variant_name, dimension_scores[agg.variant_name])]
    }


def _padded_axis_limits(
    values: list[float],
    *,
    padding: float,
    lower_bound: float,
    upper_bound: float,
    step: float,
) -> tuple[float, float]:
    """Choose a tighter axis range with a little padding around the data."""
    if not values:
        return lower_bound, upper_bound

    low = min(values)
    high = max(values)

    if math.isclose(low, high):
        low -= padding
        high += padding

    y_min = max(lower_bound, math.floor((low - padding) / step) * step)
    y_max = min(upper_bound, math.ceil((high + padding) / step) * step)

    if math.isclose(y_min, y_max):
        y_max = min(upper_bound, y_min + step)

    return y_min, y_max


def _tier_bar_chart(result: RunResult, path: Path) -> None:
    """Grouped bar chart of mean total scores per tier."""
    tier_labels = [f"Tier {t}: {name}" for t, name in sorted(TIERS.items())]
    tier_keys = sorted(TIERS.keys())
    x = np.arange(len(tier_labels))
    width = 0.8 / len(result.variant_aggregates)

    fig, ax = plt.subplots(figsize=(10, 6))
    all_values: list[float] = []

    for i, agg in enumerate(result.variant_aggregates):
        values = [agg.tier_means.get(t, 0) for t in tier_keys]
        all_values.extend(values)
        offset = (i - len(result.variant_aggregates) / 2 + 0.5) * width
        bars = ax.bar(x + offset, values, width, label=agg.variant_name, color=COLORS[i % len(COLORS)])
        for bar, val in zip(bars, values):
            ax.text(
                bar.get_x() + bar.get_width() / 2,
                bar.get_height() + 0.3,
                f"{val:.1f}",
                ha="center",
                va="bottom",
                fontsize=9,
            )

    ax.set_ylabel("Mean Total Score (0–70)")
    ax.set_title("Per-Tier Mean Total Scores", fontweight="bold")
    ax.set_xticks(x)
    ax.set_xticklabels(tier_labels, fontsize=10)
    ax.set_ylim(
        *_padded_axis_limits(
            all_values,
            padding=2.0,
            lower_bound=0.0,
            upper_bound=75.0,
            step=5.0,
        )
    )
    ax.legend()
    ax.grid(axis="y", alpha=0.3)

    plt.tight_layout()
    fig.savefig(path, dpi=150, bbox_inches="tight")
    plt.close(fig)


def _wins_pie_chart(result: RunResult, path: Path) -> None:
    """Pie chart showing win/loss/tie distribution."""
    if len(result.variant_aggregates) != 2:
        if path.exists():
            path.unlink()
        return

    a, b = result.variant_aggregates
    sizes = [a.wins, b.wins, a.ties]
    labels = [f"{a.variant_name} wins", f"{b.variant_name} wins", "Ties"]
    colors = [COLORS[0], COLORS[1], "#9ca3af"]
    # Remove zero slices
    filtered = [(s, l, c) for s, l, c in zip(sizes, labels, colors) if s > 0]
    if not filtered:
        if path.exists():
            path.unlink()
        return

    sizes, labels, colors = zip(*filtered)

    fig, ax = plt.subplots(figsize=(8, 8))
    wedges, texts, autotexts = ax.pie(
        sizes,
        labels=labels,
        colors=colors,
        autopct="%1.1f%%",
        startangle=90,
        textprops={"fontsize": 11},
    )
    ax.set_title("Win Distribution", fontweight="bold", fontsize=14)

    plt.tight_layout()
    fig.savefig(path, dpi=150, bbox_inches="tight")
    plt.close(fig)


def generate_combined_radar(
    result_paths: list[Path],
    output_path: Path,
    title: str = "Rules vs Values vs No Guidelines",
) -> None:
    """Combine per-dimension means from multiple RunResult JSONs into one radar chart.

    Each RunResult can have one or more variants. All variants across all files
    are plotted on the same radar. Duplicate variant names are suffixed.
    """
    import json

    labels = [DIMENSION_LABELS[d] for d in DIMENSIONS]
    num_dims = len(labels)
    angles = np.linspace(0, 2 * np.pi, num_dims, endpoint=False).tolist()
    angles += angles[:1]

    fig, ax = plt.subplots(figsize=(10, 10), subplot_kw=dict(polar=True))
    all_values: list[float] = []
    color_idx = 0
    seen_names: set[str] = set()

    for result_path in result_paths:
        raw = json.loads(result_path.read_text())
        result = RunResult.model_validate(raw)
        dimension_means = _compute_dimension_means(result)

        for agg in result.variant_aggregates:
            name = agg.variant_name
            if name in seen_names:
                name = f"{name} ({result_path.stem[:12]})"
            seen_names.add(name)

            raw_values = dimension_means.get(agg.variant_name, {})
            values = [raw_values.get(d, 0.0) / MAX_SCORE_PER_DIMENSION for d in DIMENSIONS]
            all_values.extend(values)
            values += values[:1]
            color = COLORS[color_idx % len(COLORS)]
            ax.plot(angles, values, "o-", linewidth=2, label=name, color=color)
            ax.fill(angles, values, alpha=0.12, color=color)
            color_idx += 1

    y_min, y_max = _padded_axis_limits(
        all_values, padding=0.03, lower_bound=0.0, upper_bound=1.0, step=0.05,
    )
    tick_values = np.linspace(y_min, y_max, 5)

    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(labels, size=9, wrap=True)
    ax.set_ylim(y_min, y_max)
    ax.set_yticks(tick_values)
    ax.set_yticklabels([f"{round(v * 100):.0f}%" for v in tick_values])
    ax.legend(loc="upper right", bbox_to_anchor=(1.3, 1.1))
    ax.set_title(title, size=14, fontweight="bold", pad=20)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    plt.tight_layout()
    fig.savefig(output_path, dpi=150, bbox_inches="tight")
    plt.close(fig)


def generate_combined_dimensions_bar(
    result_paths: list[Path],
    output_path: Path,
    title: str = "Per-Dimension Mean Scores — Rules vs Values vs No Guidelines",
) -> None:
    """Combine per-dimension means from multiple RunResult JSONs into one grouped bar chart."""
    import json

    labels = [DIMENSION_LABELS[d] for d in DIMENSIONS]
    x = np.arange(len(labels))

    all_variants: list[tuple[str, dict[str, float]]] = []

    for result_path in result_paths:
        raw = json.loads(result_path.read_text())
        result = RunResult.model_validate(raw)
        dimension_means = _compute_dimension_means(result)
        for agg in result.variant_aggregates:
            all_variants.append((agg.variant_name, dimension_means.get(agg.variant_name, {})))

    width = 0.8 / len(all_variants)
    fig, ax = plt.subplots(figsize=(14, 6))
    all_values: list[float] = []

    for i, (name, dim_means) in enumerate(all_variants):
        values = [dim_means.get(d, 0.0) for d in DIMENSIONS]
        all_values.extend(values)
        offset = (i - len(all_variants) / 2 + 0.5) * width
        bars = ax.bar(x + offset, values, width, label=name, color=COLORS[i % len(COLORS)])
        for bar, val in zip(bars, values):
            ax.text(
                bar.get_x() + bar.get_width() / 2,
                bar.get_height() + 0.1,
                f"{val:.1f}",
                ha="center", va="bottom", fontsize=7,
            )

    ax.set_ylabel("Mean Score (0–10)")
    ax.set_title(title, fontweight="bold")
    ax.set_xticks(x)
    ax.set_xticklabels(labels, rotation=30, ha="right", fontsize=9)
    ax.set_ylim(
        *_padded_axis_limits(all_values, padding=0.25, lower_bound=0.0, upper_bound=10.5, step=0.5)
    )
    ax.legend()
    ax.grid(axis="y", alpha=0.3)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    plt.tight_layout()
    fig.savefig(output_path, dpi=150, bbox_inches="tight")
    plt.close(fig)


def _score_distribution(result: RunResult, path: Path) -> None:
    """Histogram of total scores per task for each variant."""
    if len(result.variant_aggregates) < 2:
        return

    variant_names = [a.variant_name for a in result.variant_aggregates]
    fig, axes = plt.subplots(1, len(variant_names), figsize=(7 * len(variant_names), 5), sharey=True)
    if len(variant_names) == 1:
        axes = [axes]

    for i, vname in enumerate(variant_names):
        totals = [r.totals.get(vname, 0) for r in result.decoded_results]
        axes[i].hist(totals, bins=range(0, 72, 5), color=COLORS[i % len(COLORS)], alpha=0.8, edgecolor="white")
        axes[i].set_title(f"{vname} — Score Distribution", fontweight="bold")
        axes[i].set_xlabel("Total Score (0–70)")
        axes[i].set_ylabel("Count" if i == 0 else "")
        axes[i].set_xlim(0, 70)
        mean_val = np.mean(totals) if totals else 0
        axes[i].axvline(mean_val, color="red", linestyle="--", label=f"Mean: {mean_val:.1f}")
        axes[i].legend()

    plt.tight_layout()
    fig.savefig(path, dpi=150, bbox_inches="tight")
    plt.close(fig)
