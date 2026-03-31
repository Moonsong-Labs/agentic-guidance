"""
AnalyzeResults node — compute aggregates, bootstrap CIs, generate charts and report.
"""

from __future__ import annotations

import json
import logging
import time
import uuid
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Union

import numpy as np

from pydantic_graph import BaseNode, End, GraphRunContext

from ..config import DIMENSIONS, DIMENSION_LABELS, TIERS
from ..models import (
    BootstrapCI,
    RunResult,
    VariantAggregate,
)

logger = logging.getLogger(__name__)

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..graph import PipelineDeps, PipelineState


@dataclass
class AnalyzeResults(BaseNode["PipelineState", "PipelineDeps", None]):
    """Compute statistics, generate charts, and write all outputs."""

    async def run(
        self, ctx: GraphRunContext["PipelineState", "PipelineDeps"]
    ) -> End[None]:
        state = ctx.state
        config = state.config
        results = state.decoded_results

        if not results:
            logger.error("No decoded results to analyze")
            return End(None)

        variant_names = [v.name for v in config.variants]
        output_dir = Path(config.output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

        # ------------------------------------------------------------------
        # Per-variant aggregates
        # ------------------------------------------------------------------
        aggregates: dict[str, VariantAggregate] = {}

        for vname in variant_names:
            totals = []
            dim_scores: dict[str, list[float]] = {d: [] for d in DIMENSIONS}
            tier_scores: dict[int, list[float]] = {t: [] for t in TIERS}
            wins = losses = ties = 0

            for r in results:
                if vname in r.totals:
                    totals.append(r.totals[vname])
                    tier_scores[r.tier].append(r.totals[vname])

                    if vname in r.scores:
                        for ds in r.scores[vname]:
                            if ds.dimension in dim_scores:
                                dim_scores[ds.dimension].append(ds.score)

                    if r.winner == vname:
                        wins += 1
                    elif r.winner == "Tie":
                        ties += 1
                    else:
                        losses += 1

            aggregates[vname] = VariantAggregate(
                variant_name=vname,
                total_score=sum(totals),
                mean_score_per_task=np.mean(totals).item() if totals else 0.0,
                dimension_means={
                    d: np.mean(scores).item() if scores else 0.0
                    for d, scores in dim_scores.items()
                },
                tier_means={
                    t: np.mean(scores).item() if scores else 0.0
                    for t, scores in tier_scores.items()
                },
                wins=wins,
                losses=losses,
                ties=ties,
            )

        # ------------------------------------------------------------------
        # Bootstrap confidence intervals
        # ------------------------------------------------------------------
        bootstrap_cis = self._compute_bootstrap_cis(
            results, variant_names, config.bootstrap_samples, config.confidence_level
        )

        # ------------------------------------------------------------------
        # Build RunResult
        # ------------------------------------------------------------------
        elapsed = time.time() - state.start_time
        run_id = f"bench-{datetime.now(timezone.utc).strftime('%Y%m%d-%H%M%S')}-{uuid.uuid4().hex[:8]}"

        run_result = RunResult(
            run_id=run_id,
            config_hash=config.config_hash(),
            response_model=config.response_model,
            judge_model=config.judge_model,
            tasks_count=len(state.tasks),
            decoded_results=results,
            variant_aggregates=list(aggregates.values()),
            bootstrap_cis=bootstrap_cis,
            total_response_calls=state.total_response_calls,
            total_judge_calls=state.total_judge_calls,
            total_duration_seconds=elapsed,
        )
        state.run_result = run_result

        # ------------------------------------------------------------------
        # Write outputs
        # ------------------------------------------------------------------
        # 1. Full JSON result
        result_path = output_dir / f"{run_id}.json"
        result_path.write_text(run_result.model_dump_json(indent=2))
        logger.info("Results written to %s", result_path)

        # 2. Charts
        try:
            from ..analysis.charts import generate_all_charts

            generate_all_charts(run_result, output_dir / "charts")
            logger.info("Charts written to %s/charts/", output_dir)
        except Exception as e:
            logger.warning("Chart generation failed: %s", e)

        # 3. Markdown report
        report_path = output_dir / f"{run_id}-report.md"
        report_path.write_text(self._generate_report(run_result))
        logger.info("Report written to %s", report_path)

        # 4. Config snapshot
        config_path = output_dir / f"{run_id}-config.json"
        config_path.write_text(config.model_dump_json(indent=2))

        return End(None)

    def _compute_bootstrap_cis(
        self,
        results: list,
        variant_names: list[str],
        n_bootstrap: int,
        confidence: float,
    ) -> list[BootstrapCI]:
        """Compute bootstrap confidence intervals for score differences."""
        if len(variant_names) != 2:
            return []

        v1, v2 = variant_names
        rng = np.random.default_rng(42)

        cis = []

        # Overall total score difference
        diffs_total = []
        for r in results:
            if v1 in r.totals and v2 in r.totals:
                diffs_total.append(r.totals[v1] - r.totals[v2])

        if diffs_total:
            cis.append(self._bootstrap_one("total_score", diffs_total, rng, n_bootstrap, confidence))

        # Per-dimension
        for dim in DIMENSIONS:
            diffs = []
            for r in results:
                s1 = next((s.score for s in r.scores.get(v1, []) if s.dimension == dim), None)
                s2 = next((s.score for s in r.scores.get(v2, []) if s.dimension == dim), None)
                if s1 is not None and s2 is not None:
                    diffs.append(s1 - s2)
            if diffs:
                cis.append(self._bootstrap_one(dim, diffs, rng, n_bootstrap, confidence))

        # Per-tier
        for tier in TIERS:
            diffs = []
            for r in results:
                if r.tier == tier and v1 in r.totals and v2 in r.totals:
                    diffs.append(r.totals[v1] - r.totals[v2])
            if diffs:
                cis.append(self._bootstrap_one(f"tier_{tier}", diffs, rng, n_bootstrap, confidence))

        return cis

    @staticmethod
    def _bootstrap_one(
        metric: str,
        diffs: list[float],
        rng: np.random.Generator,
        n_bootstrap: int,
        confidence: float,
    ) -> BootstrapCI:
        arr = np.array(diffs)
        n = len(arr)
        boot_means = np.array(
            [rng.choice(arr, size=n, replace=True).mean() for _ in range(n_bootstrap)]
        )
        alpha = (1 - confidence) / 2
        ci_lower = float(np.percentile(boot_means, alpha * 100))
        ci_upper = float(np.percentile(boot_means, (1 - alpha) * 100))
        mean_diff = float(arr.mean())

        # Two-sided p-value: proportion of bootstrap samples on opposite side of 0
        if mean_diff >= 0:
            p_value = float((boot_means < 0).mean()) * 2
        else:
            p_value = float((boot_means > 0).mean()) * 2
        p_value = min(p_value, 1.0)

        return BootstrapCI(
            metric=metric,
            mean_diff=mean_diff,
            ci_lower=ci_lower,
            ci_upper=ci_upper,
            p_value=p_value,
            significant=(p_value < (1 - confidence)),
        )

    @staticmethod
    def _generate_report(result: RunResult) -> str:
        """Generate a Markdown summary report."""
        lines = [
            f"# Benchmark Report: {result.run_id}",
            "",
            f"**Date:** {result.timestamp.strftime('%Y-%m-%d %H:%M UTC')}",
            f"**Response Model:** {result.response_model}",
            f"**Judge Model:** {result.judge_model}",
            f"**Tasks:** {result.tasks_count}",
            f"**Config Hash:** {result.config_hash}",
            f"**Duration:** {result.total_duration_seconds:.1f}s",
            f"**API Calls:** {result.total_response_calls} responses + {result.total_judge_calls} judgments",
            "",
            "---",
            "",
            "## Overall Results",
            "",
            "| Variant | Total Score | Mean/Task | Wins | Losses | Ties |",
            "|---------|------------|-----------|------|--------|------|",
        ]

        for agg in result.variant_aggregates:
            lines.append(
                f"| {agg.variant_name} | {agg.total_score:.0f} | "
                f"{agg.mean_score_per_task:.2f} | {agg.wins} | {agg.losses} | {agg.ties} |"
            )

        lines.extend(["", "## Per-Dimension Breakdown", ""])
        dim_header = "| Dimension |"
        dim_sep = "|-----------|"
        for agg in result.variant_aggregates:
            dim_header += f" {agg.variant_name} |"
            dim_sep += "--------|"
        lines.append(dim_header)
        lines.append(dim_sep)

        for dim in DIMENSIONS:
            label = DIMENSION_LABELS.get(dim, dim)
            row = f"| {label} |"
            for agg in result.variant_aggregates:
                score = agg.dimension_means.get(dim, 0.0)
                row += f" {score:.2f} |"
            lines.append(row)

        lines.extend(["", "## Per-Tier Breakdown", ""])
        tier_header = "| Tier |"
        tier_sep = "|------|"
        for agg in result.variant_aggregates:
            tier_header += f" {agg.variant_name} |"
            tier_sep += "--------|"
        lines.append(tier_header)
        lines.append(tier_sep)

        for tier_num, tier_name in sorted(TIERS.items()):
            row = f"| {tier_num} ({tier_name}) |"
            for agg in result.variant_aggregates:
                score = agg.tier_means.get(tier_num, 0.0)
                row += f" {score:.2f} |"
            lines.append(row)

        # Statistical significance
        lines.extend(["", "## Statistical Significance (Bootstrap CIs)", ""])
        lines.append("| Metric | Mean Diff | 95% CI | p-value | Significant |")
        lines.append("|--------|-----------|--------|---------|-------------|")

        for ci in result.bootstrap_cis:
            label = DIMENSION_LABELS.get(ci.metric, ci.metric)
            sig = "✅" if ci.significant else "❌"
            lines.append(
                f"| {label} | {ci.mean_diff:+.3f} | "
                f"[{ci.ci_lower:+.3f}, {ci.ci_upper:+.3f}] | "
                f"{ci.p_value:.4f} | {sig} |"
            )

        lines.extend(["", "---", "", "*Generated by bench framework*"])
        return "\n".join(lines)
