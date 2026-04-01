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
    run_parser.add_argument("--checkpoint-dir", type=str, help="Override checkpoint directory")
    run_parser.add_argument(
        "--no-checkpoint",
        action="store_true",
        help="Disable checkpoint loading and saving",
    )

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

    # --- rate ---
    rate_parser = subparsers.add_parser(
        "rate", help="Generate + rate a single variant (no pairwise comparison)"
    )
    rate_parser.add_argument("--config", type=str, help="Path to bench_config.json")
    rate_parser.add_argument("--variant", type=str, required=True, help="Variant name to rate")
    rate_parser.add_argument("--response-model", type=str, help="Override response model")
    rate_parser.add_argument("--judge-model", type=str, help="Override judge model")
    rate_parser.add_argument("--output-dir", type=str, help="Override output directory")

    # --- combine ---
    combine_parser = subparsers.add_parser(
        "combine", help="Combine multiple result JSONs into one radar + bar chart"
    )
    combine_parser.add_argument(
        "--results", type=str, nargs="+", required=True,
        help="Paths to result JSON files to overlay",
    )
    combine_parser.add_argument(
        "--output-dir", type=str, default="results-combined",
        help="Output directory for combined charts",
    )

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
    elif args.command == "rate":
        _cmd_rate(args)
    elif args.command == "combine":
        _cmd_combine(args)
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
    if getattr(args, "checkpoint_dir", None):
        config.checkpoint_dir = args.checkpoint_dir
    if getattr(args, "no_checkpoint", False):
        config.enable_checkpointing = False

    logger = logging.getLogger("bench")
    logger.info("Starting benchmark run")
    logger.info("  Response model: %s", config.response_model)
    logger.info("  Judge model: %s", config.judge_model)
    logger.info("  Seed: %d", config.seed)
    logger.info("  Config hash: %s", config.config_hash())
    logger.info("  Checkpointing: %s", "enabled" if config.enable_checkpointing else "disabled")

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


def _cmd_rate(args: argparse.Namespace) -> None:
    """Generate responses for a single variant and rate each one individually."""
    import time
    import uuid
    from datetime import datetime, timezone

    import numpy as np
    from pydantic_ai import Agent

    from .config import DIMENSIONS, DIMENSION_LABELS, TIERS
    from .models import (
        DecodedTaskResult,
        DimensionScore,
        RunResult,
        SingleJudgeScore,
        VariantAggregate,
        VariantResponse,
    )
    from .rubric import build_single_judge_system_prompt
    from .tasks import load_builtin_tasks

    config_path = getattr(args, "config", None)
    config = BenchConfig.from_file(config_path) if config_path else BenchConfig()

    if getattr(args, "response_model", None):
        config.response_model = args.response_model
    if getattr(args, "judge_model", None):
        config.judge_model = args.judge_model
    if getattr(args, "output_dir", None):
        config.output_dir = args.output_dir

    variant_name = args.variant
    variant = next((v for v in config.variants if v.name == variant_name), None)
    if variant is None:
        logging.getLogger("bench").error(
            "Variant '%s' not found in config. Available: %s",
            variant_name,
            [v.name for v in config.variants],
        )
        sys.exit(1)

    try:
        variant_text = variant.load_text()
    except FileNotFoundError:
        variant_text = ""

    logger = logging.getLogger("bench")
    logger.info("Single-variant rating mode")
    logger.info("  Variant: %s", variant_name)
    logger.info("  Response model: %s", config.response_model)
    logger.info("  Judge model: %s", config.judge_model)

    tasks = load_builtin_tasks()
    logger.info("  Tasks: %d", len(tasks))

    output_dir = Path(config.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    start_time = time.time()

    async def _run() -> RunResult:
        sem_resp = asyncio.Semaphore(config.max_concurrent_responses)
        sem_judge = asyncio.Semaphore(config.max_concurrent_judgments)

        response_agent = Agent(config.response_model, system_prompt=variant_text) if variant_text else Agent(config.response_model)

        async def generate_one(task):
            async with sem_resp:
                user_message = f"Context: {task.context}\n\n{task.prompt}"
                t0 = time.monotonic()
                result = await response_agent.run(user_message)
                elapsed = (time.monotonic() - t0) * 1000
                return VariantResponse(
                    task_id=task.id,
                    variant_name=variant_name,
                    run_index=0,
                    response_text=result.output,
                    model=config.response_model,
                    latency_ms=elapsed,
                )

        logger.info("Generating %d responses...", len(tasks))
        response_coros = [generate_one(t) for t in tasks]
        responses: list[VariantResponse] = []
        response_count = 0
        for coro in asyncio.as_completed(response_coros):
            try:
                resp = await coro
                responses.append(resp)
                response_count += 1
                if response_count % 20 == 0:
                    logger.info("  Progress: %d/%d responses", response_count, len(tasks))
            except Exception as e:
                logger.error("Response generation failed: %s", e)
        logger.info("Generated %d responses", len(responses))

        judge_system = build_single_judge_system_prompt()
        judge_agent = Agent(
            config.judge_model,
            system_prompt=judge_system,
            output_type=SingleJudgeScore,
        )

        response_by_task = {r.task_id: r for r in responses}

        async def judge_one(task) -> SingleJudgeScore | None:
            async with sem_judge:
                resp = response_by_task.get(task.id)
                if not resp:
                    return None
                user_prompt = (
                    f"## Task {task.id} (Tier {task.tier})\n"
                    f"**Primary Principle:** {task.principle}\n"
                    f"**Context:** {task.context}\n"
                    f"**User Prompt:** {task.prompt}\n\n---\n\n"
                    f"### Response:\n{resp.response_text}\n\n---\n\n"
                    f"Score this response on ALL 7 dimensions (0–10 each). Use the full range.\n"
                    f"Return your scores as structured output with reasoning for each dimension."
                )
                try:
                    result = await judge_agent.run(user_prompt)
                    return result.output.model_copy(update={"task_id": task.id})
                except Exception as e:
                    logger.error("Judge failed for task %d: %s", task.id, e)
                    return None

        logger.info("Judging %d responses...", len(responses))
        judge_coros = [judge_one(t) for t in tasks]
        scores: list[SingleJudgeScore] = []
        judge_count = 0
        for coro in asyncio.as_completed(judge_coros):
            score = await coro
            if score is not None:
                scores.append(score)
                judge_count += 1
                if judge_count % 20 == 0:
                    logger.info("  Progress: %d/%d judged", judge_count, len(tasks))
        logger.info("Judged %d/%d tasks", len(scores), len(tasks))

        task_by_id = {t.id: t for t in tasks}
        decoded = []
        totals_list = []
        dim_scores: dict[str, list[float]] = {d: [] for d in DIMENSIONS}
        tier_scores: dict[int, list[float]] = {t: [] for t in TIERS}
        from .nodes.analyze import DIMENSION_LABEL_TO_KEY

        for s in scores:
            task = task_by_id.get(s.task_id)
            if not task:
                continue
            decoded.append(
                DecodedTaskResult(
                    task_id=s.task_id,
                    tier=task.tier,
                    principle=task.principle,
                    tensions=task.tensions,
                    scores={variant_name: s.scores},
                    totals={variant_name: s.total},
                    winner=variant_name,
                    reasoning=s.overall_reasoning,
                )
            )
            totals_list.append(s.total)
            tier_scores[task.tier].append(s.total)
            for ds in s.scores:
                dim_key = DIMENSION_LABEL_TO_KEY.get(ds.dimension, ds.dimension)
                if dim_key in dim_scores:
                    dim_scores[dim_key].append(ds.score)

        agg = VariantAggregate(
            variant_name=variant_name,
            total_score=sum(totals_list),
            mean_score_per_task=float(np.mean(totals_list)) if totals_list else 0.0,
            dimension_means={
                d: float(np.mean(vals)) if vals else 0.0
                for d, vals in dim_scores.items()
            },
            tier_means={
                t: float(np.mean(vals)) if vals else 0.0
                for t, vals in tier_scores.items()
            },
            wins=len(scores),
            losses=0,
            ties=0,
        )

        elapsed = time.time() - start_time
        run_id = f"rate-{variant_name}-{datetime.now(timezone.utc).strftime('%Y%m%d-%H%M%S')}-{uuid.uuid4().hex[:8]}"

        return RunResult(
            run_id=run_id,
            config_hash=config.config_hash(),
            response_model=config.response_model,
            judge_model=config.judge_model,
            tasks_count=len(tasks),
            decoded_results=decoded,
            variant_aggregates=[agg],
            bootstrap_cis=[],
            total_response_calls=len(responses),
            total_judge_calls=len(scores),
            total_duration_seconds=elapsed,
        )

    run_result = asyncio.run(_run())

    result_path = output_dir / f"{run_result.run_id}.json"
    result_path.write_text(run_result.model_dump_json(indent=2))
    logger.info("Results written to %s", result_path)

    try:
        from .analysis.charts import generate_all_charts
        generate_all_charts(run_result, output_dir / "charts")
        logger.info("Charts written to %s/charts/", output_dir)
    except Exception as e:
        logger.warning("Chart generation failed: %s", e)

    from .nodes.analyze import AnalyzeResults
    report = AnalyzeResults._generate_report(run_result)
    report_path = output_dir / f"{run_result.run_id}-report.md"
    report_path.write_text(report)
    logger.info("Report written to %s", report_path)

    config_out = output_dir / f"{run_result.run_id}-config.json"
    config_out.write_text(config.model_dump_json(indent=2))

    print("\n" + "=" * 60)
    print(f"RATING COMPLETE — {variant_name}")
    print("=" * 60)
    agg = run_result.variant_aggregates[0]
    print(f"  Mean score: {agg.mean_score_per_task:.2f}/70")
    print(f"  Tasks rated: {run_result.tasks_count}")
    print(f"\nFull results: {result_path}")


def _cmd_combine(args: argparse.Namespace) -> None:
    """Combine multiple result JSONs into a single radar + bar chart."""
    from .analysis.charts import generate_combined_dimensions_bar, generate_combined_radar

    result_paths = [Path(p) for p in args.results]
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    generate_combined_radar(result_paths, output_dir / "radar-combined.png")
    print(f"Combined radar written to {output_dir}/radar-combined.png")

    generate_combined_dimensions_bar(result_paths, output_dir / "dimensions-combined.png")
    print(f"Combined dimensions bar written to {output_dir}/dimensions-combined.png")


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
