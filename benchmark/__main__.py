"""
CLI entrypoint: python -m bench

Usage:
    python -m bench --config bench_config.json    # Full pipeline run
    python -m bench tasks --output tasks.json     # Export tasks for review
    python -m bench judge --responses resp.json   # Judge existing responses
    python -m bench analyze --results results.json # Analyze existing results
"""

from __future__ import annotations

import argparse
import asyncio
import json
import logging
import sys
from pathlib import Path

from .config import BenchConfig


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="bench",
        description="AI Agent System Prompt Benchmark Framework",
    )
    parser.add_argument(
        "-v", "--verbose", action="store_true", help="Enable debug logging"
    )

    subparsers = parser.add_subparsers(dest="command")

    # --- run (default) ---
    run_parser = subparsers.add_parser("run", help="Full pipeline run")
    run_parser.add_argument("--config", type=str, help="Path to bench_config.json")
    run_parser.add_argument(
        "--response-model", type=str, help="Override response model"
    )
    run_parser.add_argument("--judge-model", type=str, help="Override judge model")
    run_parser.add_argument("--seed", type=int, help="Override seed")
    run_parser.add_argument("--output-dir", type=str, help="Override output directory")

    # --- tasks ---
    tasks_parser = subparsers.add_parser("tasks", help="Export tasks for review")
    tasks_parser.add_argument(
        "--output", type=str, default="tasks.json", help="Output file"
    )
    tasks_parser.add_argument(
        "--format",
        choices=["json", "markdown"],
        default="json",
        help="Output format",
    )

    # --- judge ---
    judge_parser = subparsers.add_parser("judge", help="Judge existing responses")
    judge_parser.add_argument(
        "--responses", type=str, required=True, help="Path to responses JSON"
    )
    judge_parser.add_argument("--config", type=str, help="Path to bench_config.json")

    # --- analyze ---
    analyze_parser = subparsers.add_parser("analyze", help="Analyze existing results")
    analyze_parser.add_argument(
        "--results", type=str, required=True, help="Path to results JSON"
    )
    analyze_parser.add_argument(
        "--output-dir", type=str, default="results", help="Output directory for charts/report"
    )

    args = parser.parse_args()

    # Setup logging
    level = logging.DEBUG if args.verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%H:%M:%S",
    )

    if args.command is None or args.command == "run":
        _cmd_run(args)
    elif args.command == "tasks":
        _cmd_tasks(args)
    elif args.command == "judge":
        _cmd_judge(args)
    elif args.command == "analyze":
        _cmd_analyze(args)
    else:
        parser.print_help()


# ---------------------------------------------------------------------------
# Commands
# ---------------------------------------------------------------------------


def _cmd_run(args: argparse.Namespace) -> None:
    """Run the full pipeline."""
    from .graph import PipelineDeps, PipelineState, bench_graph
    from .nodes import GenerateTasks

    # Load or create config
    config_path = getattr(args, "config", None)
    if config_path:
        config = BenchConfig.from_file(config_path)
    else:
        config = BenchConfig()

    # Apply CLI overrides
    if getattr(args, "response_model", None):
        config.response_model = args.response_model
    if getattr(args, "judge_model", None):
        config.judge_model = args.judge_model
    if getattr(args, "seed", None) is not None:
        config.seed = args.seed
    if getattr(args, "output_dir", None):
        config.output_dir = args.output_dir

    logger = logging.getLogger("bench")
    logger.info("Starting benchmark run")
    logger.info("  Response model: %s", config.response_model)
    logger.info("  Judge model: %s", config.judge_model)
    logger.info("  Seed: %d", config.seed)
    logger.info("  Config hash: %s", config.config_hash())

    # Load variant prompt texts
    variant_texts = {}
    for v in config.variants:
        try:
            variant_texts[v.name] = v.load_text()
            logger.info("  Loaded variant '%s' from %s", v.name, v.path)
        except FileNotFoundError:
            logger.error("Variant file not found: %s", v.path)
            sys.exit(1)

    state = PipelineState(config=config)
    deps = PipelineDeps(variant_texts=variant_texts)

    result = asyncio.run(bench_graph.run(GenerateTasks(), state=state, deps=deps))
    logger.info("Pipeline complete.")

    if state.run_result:
        logger.info("Run ID: %s", state.run_result.run_id)
        logger.info("Results in: %s/", config.output_dir)

        # Print summary
        print("\n" + "=" * 60)
        print("BENCHMARK COMPLETE")
        print("=" * 60)
        for agg in state.run_result.variant_aggregates:
            print(
                f"  {agg.variant_name}: {agg.mean_score_per_task:.2f}/70 avg "
                f"(W:{agg.wins} L:{agg.losses} T:{agg.ties})"
            )
        print(f"\nFull results: {config.output_dir}/{state.run_result.run_id}.json")


def _cmd_tasks(args: argparse.Namespace) -> None:
    """Export tasks for review."""
    from .tasks import load_builtin_tasks

    tasks = load_builtin_tasks()

    if args.format == "json":
        output = {"tasks": [t.model_dump() for t in tasks]}
        Path(args.output).write_text(json.dumps(output, indent=2))
        print(f"Exported {len(tasks)} tasks to {args.output}")
    else:
        lines = [f"# Benchmark Tasks ({len(tasks)} tasks)\n"]
        for t in tasks:
            lines.append(f"## Task {t.id} (Tier {t.tier})")
            lines.append(f"**Principle:** {t.principle}")
            if t.tensions:
                lines.append(f"**Tensions:** {', '.join(t.tensions)}")
            lines.append(f"**Context:** {t.context}")
            lines.append(f"**Prompt:** {t.prompt}")
            if t.adversarial_notes:
                lines.append(f"**Notes:** {t.adversarial_notes}")
            lines.append("")
        Path(args.output).write_text("\n".join(lines))
        print(f"Exported {len(tasks)} tasks to {args.output}")


def _cmd_judge(args: argparse.Namespace) -> None:
    """Judge existing responses."""
    from .graph import PipelineDeps, PipelineState, bench_graph
    from .models import VariantResponse
    from .nodes import JudgeResponses
    from .tasks import load_builtin_tasks

    config_path = getattr(args, "config", None)
    config = BenchConfig.from_file(config_path) if config_path else BenchConfig()

    # Load responses
    raw = json.loads(Path(args.responses).read_text())
    if isinstance(raw, dict) and "responses" in raw:
        raw = raw["responses"]
    responses = [VariantResponse.model_validate(r) for r in raw]

    variant_texts = {}
    for v in config.variants:
        try:
            variant_texts[v.name] = v.load_text()
        except FileNotFoundError:
            variant_texts[v.name] = ""

    state = PipelineState(config=config)
    state.tasks = load_builtin_tasks()
    state.responses = responses

    deps = PipelineDeps(variant_texts=variant_texts)

    # Start from JudgeResponses node
    result = asyncio.run(bench_graph.run(JudgeResponses(), state=state, deps=deps))

    if state.run_result:
        print(f"Judging complete. Results: {config.output_dir}/{state.run_result.run_id}.json")


def _cmd_analyze(args: argparse.Namespace) -> None:
    """Analyze existing results."""
    from .analysis.charts import generate_all_charts
    from .models import RunResult

    raw = json.loads(Path(args.results).read_text())
    result = RunResult.model_validate(raw)

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    # Generate charts
    generate_all_charts(result, output_dir / "charts")
    print(f"Charts written to {output_dir}/charts/")

    # Generate report
    from .nodes.analyze import AnalyzeResults

    report = AnalyzeResults._generate_report(result)
    report_path = output_dir / f"{result.run_id}-report.md"
    report_path.write_text(report)
    print(f"Report written to {report_path}")


if __name__ == "__main__":
    main()
