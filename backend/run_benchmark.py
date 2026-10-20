"""
run_benchmark.py — Standalone CLI runner for empirical LLM benchmark evaluation.

Executes paired controlled experiments across:
  - Policy A: ALWAYS_LARGE (Baseline)
  - Policy B: ADAPTIVE_ML (Intelligent Router)
  - Policy C: RULE_BASED (Heuristic Complexity)

Usage:
    python run_benchmark.py --mode demo --limit 10   # Quick dry-run (10 prompts)
    python run_benchmark.py --mode demo              # Full 50-prompt demo run
    python run_benchmark.py --mode real              # Real API evaluation (requires LLM_API_KEY)
    python run_benchmark.py --resume <run_id>        # Resume an existing run without duplicate rows
"""

import sys
import os
import argparse
import asyncio
from pathlib import Path

# Ensure backend directory is in path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from benchmarks.runner import BenchmarkRunner

async def main():
    parser = argparse.ArgumentParser(description="Headless Empirical LLM Router Benchmark Runner")
    parser.add_argument("--mode", choices=["demo", "real"], default="demo",
                        help="Execution mode: 'demo' (simulated) or 'real' (live API calls). Default: demo")
    parser.add_argument("--limit", type=int, default=None,
                        help="Limit number of prompts to evaluate (useful for quick smoke tests).")
    parser.add_argument("--run-id", type=str, default=None,
                        help="Custom run ID or existing run ID to resume.")
    parser.add_argument("--temperature", type=float, default=0.0,
                        help="Generation temperature (default: 0.0 for deterministic sampling).")
    parser.add_argument("--max-tokens", type=int, default=512,
                        help="Max tokens per response (default: 512).")
    args = parser.parse_args()

    runner = BenchmarkRunner()

    def print_progress(current, total, record):
        pct = (current / total) * 100
        pol = record['policy']
        pid = record['prompt_id']
        tier = record['selected_model']
        score = record['quality_score']
        print(f"[{pct:5.1f}%] [{current:3d}/{total:3d}] {pol:12s} | {pid:10s} -> {tier:6s} | Score: {score:4.1f}/10")

    print(f"\n{'='*70}")
    print(f"  Adaptive LLM Router — Empirical Benchmark Runner")
    print(f"{'='*70}")

    report = await runner.run(
        execution_mode=args.mode,
        run_id=args.run_id,
        limit_items=args.limit,
        temperature=args.temperature,
        max_tokens=args.max_tokens,
        on_progress=print_progress
    )

    print(f"\n{'='*70}")
    print(f"  BENCHMARK SUMMARY RESULTS (Run ID: {report['run_id']})")
    print(f"{'='*70}\n")

    metrics = report["summary_metrics"]
    for pol, data in metrics.items():
        print(f"Policy: {pol:14s}")
        print(f"  Success / Failed   : {data['successful_requests']} / {data['failed_requests']} (Fail Rate: {data['failure_rate_pct']}%)")
        print(f"  Mean Quality Score : {data['mean_quality_score']:.2f} / 10.0 (std: {data['std_quality_score']:.2f})")
        print(f"  Mean Latency       : {data['mean_latency_s']:.4f}s (Median: {data['median_latency_s']:.4f}s, P95: {data['p95_latency_s']:.4f}s)")
        print(f"  Mean Cost / Total  : ${data['mean_cost_usd']:.6f} / ${data['total_cost_usd']:.5f}")
        print(f"  Tier Distribution  : {data['model_distribution_pct']}")
        print()

    comparisons = report.get("comparisons_vs_always_large", {})
    if comparisons:
        print(f"{'-'*70}")
        print("  COMPARISONS RELATIVE TO ALWAYS_LARGE BASELINE")
        print(f"{'-'*70}")
        for pol, comp in comparisons.items():
            print(f"Policy: {pol}")
            print(f"  Quality Retention : {comp['quality_retention_pct']:.1f}%")
            print(f"  Cost Reduction    : {comp['cost_reduction_pct']:.1f}%")
            print(f"  Latency Reduction : {comp['latency_reduction_pct']:.1f}%")
            ci_lat = comp['latency_diff_ci_95']
            ci_cost = comp['cost_diff_ci_95']
            print(f"  Latency Diff 95% CI: [{ci_lat['ci_lower']:.4f}s, {ci_lat['ci_upper']:.4f}s] (mean diff: {ci_lat['mean_diff']:.4f}s)")
            print(f"  Cost Diff 95% CI   : [${ci_cost['ci_lower']:.6f}, ${ci_cost['ci_upper']:.6f}] (mean diff: ${ci_cost['mean_diff']:.6f})")
            print()

    print(f"{'='*70}\n")

if __name__ == "__main__":
    asyncio.run(main())
