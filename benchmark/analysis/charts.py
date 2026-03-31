"""
Chart generation for benchmark results.

Produces radar charts, bar charts, and tier breakdowns using matplotlib.
"""

from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")  # Non-interactive backend
import matplotlib.pyplot as plt
import numpy as np

from ..config import DIMENSIONS, DIMENSION_LABELS, TIERS
from ..models import RunResult


# Color palette
COLORS = ["#2563eb", "#dc2626", "#16a34a", "#d97706", "#7c3aed", "#0891b2"]


def generate_all_charts(result: RunResult, output_dir: Path) -> None:
    """Generate all charts and save to output_dir."""
    output_dir.mkdir(parents=True, exist_ok=True)

    _radar_chart(result, output_dir / "radar.png")
    _dimension_bar_chart(result, output_dir / "dimensions.png")
    _tier_bar_chart(result, output_dir / "tiers.png")
    _wins_pie_chart(result, output_dir / "wins.png")
    _score_distribution(result, output_dir / "distribution.png")


def _radar_chart(result: RunResult, path: Path) -> None:
    """Radar/spider chart comparing variants across all dimensions."""
    labels = [DIMENSION_LABELS[d] for d in DIMENSIONS]
    num_dims = len(labels)
    angles = np.linspace(0, 2 * np.pi, num_dims, endpoint=False).tolist()
    angles += angles[:1]  # close the polygon

    fig, ax = plt.subplots(figsize=(10, 10), subplot_kw=dict(polar=True))

    for i, agg in enumerate(result.variant_aggregates):
        values = [agg.dimension_means.get(d, 0) for d in DIMENSIONS]
        values += values[:1]
        ax.plot(angles, values, "o-", linewidth=2, label=agg.variant_name, color=COLORS[i % len(COLORS)])
        ax.fill(angles, values, alpha=0.15, color=COLORS[i % len(COLORS)])

    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(labels, size=9, wrap=True)
    ax.set_ylim(0, 10)
    ax.set_yticks(range(0, 11, 2))
    ax.legend(loc="upper right", bbox_to_anchor=(1.3, 1.1))
    ax.set_title("Dimension Comparison (0–10 scale)", size=14, fontweight="bold", pad=20)

    plt.tight_layout()
    fig.savefig(path, dpi=150, bbox_inches="tight")
    plt.close(fig)


def _dimension_bar_chart(result: RunResult, path: Path) -> None:
    """Grouped bar chart of mean scores per dimension."""
    labels = [DIMENSION_LABELS[d] for d in DIMENSIONS]
    x = np.arange(len(labels))
    width = 0.8 / len(result.variant_aggregates)

    fig, ax = plt.subplots(figsize=(14, 6))

    for i, agg in enumerate(result.variant_aggregates):
        values = [agg.dimension_means.get(d, 0) for d in DIMENSIONS]
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
    ax.set_ylim(0, 10.5)
    ax.legend()
    ax.grid(axis="y", alpha=0.3)

    plt.tight_layout()
    fig.savefig(path, dpi=150, bbox_inches="tight")
    plt.close(fig)


def _tier_bar_chart(result: RunResult, path: Path) -> None:
    """Grouped bar chart of mean total scores per tier."""
    tier_labels = [f"Tier {t}: {name}" for t, name in sorted(TIERS.items())]
    tier_keys = sorted(TIERS.keys())
    x = np.arange(len(tier_labels))
    width = 0.8 / len(result.variant_aggregates)

    fig, ax = plt.subplots(figsize=(10, 6))

    for i, agg in enumerate(result.variant_aggregates):
        values = [agg.tier_means.get(t, 0) for t in tier_keys]
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
    ax.set_ylim(0, 75)
    ax.legend()
    ax.grid(axis="y", alpha=0.3)

    plt.tight_layout()
    fig.savefig(path, dpi=150, bbox_inches="tight")
    plt.close(fig)


def _wins_pie_chart(result: RunResult, path: Path) -> None:
    """Pie chart showing win/loss/tie distribution."""
    if len(result.variant_aggregates) != 2:
        return

    a, b = result.variant_aggregates
    sizes = [a.wins, b.wins, a.ties]
    labels = [f"{a.variant_name} wins", f"{b.variant_name} wins", "Ties"]
    colors = [COLORS[0], COLORS[1], "#9ca3af"]
    # Remove zero slices
    filtered = [(s, l, c) for s, l, c in zip(sizes, labels, colors) if s > 0]
    if not filtered:
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
