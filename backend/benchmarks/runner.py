import asyncio
import csv
import json
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Dict, Any, Optional

from config import BENCHMARK_RESULTS_DIR
from database.db import DatabaseManager
from router.feature_extractor import FeatureExtractor
from router.classifier import MLClassifier
from router.router import Router
from models.small import SmallModelProvider
from models.medium import MediumModelProvider
from models.large import LargeModelProvider
from .dataset import BenchmarkDataset, BENCHMARK_VERSION
from .evaluator import BenchmarkEvaluator
from .metrics import aggregate_benchmark_results

class BenchmarkRunner:
    """
    Headless batch runner for controlled, paired empirical evaluation.
    Evaluates:
      - Policy A: ALWAYS_LARGE
      - Policy B: ADAPTIVE_ML
      - Policy C: RULE_BASED
    Across all benchmark prompts under identical generation parameters.
    Fully resumable without duplicate records.
    """
    def __init__(
        self,
        db: Optional[DatabaseManager] = None,
        dataset: Optional[BenchmarkDataset] = None,
        evaluator: Optional[BenchmarkEvaluator] = None,
        providers: Optional[Dict[str, Any]] = None,
        router: Optional[Router] = None,
        feature_extractor: Optional[FeatureExtractor] = None
    ):
        self.db = db or DatabaseManager()
        self.dataset = dataset or BenchmarkDataset()
        self.evaluator = evaluator or BenchmarkEvaluator()
        self.fe = feature_extractor or FeatureExtractor()
        
        if router is None:
            clf = MLClassifier()
            self.router = Router(clf, self.fe)
        else:
            self.router = router

        self.providers = providers or {
            'SMALL': SmallModelProvider(),
            'MEDIUM': MediumModelProvider(),
            'LARGE': LargeModelProvider()
        }
        self.results_dir = BENCHMARK_RESULTS_DIR
        self.results_dir.mkdir(parents=True, exist_ok=True)

    def route_by_policy(self, query: str, policy: str) -> Dict[str, Any]:
        """Determine model tier based on evaluation policy."""
        if policy == "ALWAYS_LARGE":
            return {
                "selected_model": "LARGE",
                "complexity": "HIGH",
                "confidence": 1.0,
                "reasoning": "Policy A: Baseline always routes to Large model."
            }
        elif policy == "ADAPTIVE_ML":
            decision = self.router.route(query)
            return decision
        elif policy == "RULE_BASED":
            feats = self.fe.extract(query)
            comp = feats["estimated_complexity"]
            mapping = {"LOW": "SMALL", "MODERATE": "MEDIUM", "HIGH": "LARGE"}
            selected = mapping.get(comp, "MEDIUM")
            return {
                "selected_model": selected,
                "complexity": comp,
                "confidence": 0.8,
                "reasoning": f"Policy C: Heuristic rule mapped complexity {comp} to {selected}."
            }
        else:
            raise ValueError(f"Unknown policy: {policy}")

    async def run(
        self,
        execution_mode: str = "demo",
        policies: Optional[List[str]] = None,
        run_id: Optional[str] = None,
        temperature: float = 0.0,
        max_tokens: int = 512,
        limit_items: Optional[int] = None,
        on_progress: Optional[callable] = None
    ) -> Dict[str, Any]:
        """
        Execute the benchmark run across specified policies.
        """
        if policies is None:
            policies = ["ALWAYS_LARGE", "ADAPTIVE_ML", "RULE_BASED"]

        run_id = run_id or f"bench_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        items = self.dataset.items
        if limit_items is not None and limit_items > 0:
            items = items[:limit_items]

        # Register run in database
        self.db.save_benchmark_run({
            "run_id": run_id,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "execution_mode": execution_mode,
            "dataset_version": BENCHMARK_VERSION,
            "total_prompts": len(items),
            "policies": policies,
            "status": "running"
        })

        # Fetch completed items for resumability
        completed_keys = self.db.get_completed_benchmark_keys(run_id)

        all_results = []
        total_evals = len(items) * len(policies)
        eval_count = len(completed_keys)

        print(f"\n[BenchmarkRunner] Starting Run ID: {run_id}")
        print(f"  Execution Mode : {execution_mode.upper()}")
        print(f"  Dataset Items  : {len(items)} prompts")
        print(f"  Policies       : {policies}")
        print(f"  Already Done   : {len(completed_keys)} / {total_evals} evaluations (resuming)")

        # Execute evaluations
        for item in items:
            p_id = item["id"]
            prompt = item["prompt"]
            cat = item["category"]

            for pol in policies:
                if (p_id, pol) in completed_keys:
                    continue

                # 1. Routing Decision
                routing = self.route_by_policy(prompt, pol)
                tier = routing["selected_model"]
                provider = self.providers[tier]

                # 2. Generation
                demo_flag = (execution_mode == "demo")
                gen_result = await provider.generate(
                    query=prompt,
                    demo_mode=demo_flag,
                    execution_mode=execution_mode,
                    temperature=temperature,
                    max_tokens=max_tokens
                )

                # 3. Quality Evaluation
                response_text = gen_result.get("response", "")
                eval_result = self.evaluator.evaluate(item, response_text)

                record = {
                    "run_id": run_id,
                    "prompt_id": p_id,
                    "category": cat,
                    "policy": pol,
                    "selected_model": tier,
                    "model_id": gen_result.get("model_id", "unknown"),
                    "latency": gen_result.get("latency", 0.0),
                    "prompt_tokens": gen_result.get("token_usage", {}).get("prompt_tokens", 0),
                    "completion_tokens": gen_result.get("token_usage", {}).get("completion_tokens", 0),
                    "cost": gen_result.get("estimated_cost", 0.0),
                    "quality_score": eval_result.get("overall_score", 0.0),
                    "eval_details": eval_result.get("details", ""),
                    "response": response_text[:500],  # Truncate response for DB storage
                    "error": gen_result.get("error")
                }

                # Save record immediately for crash resilience and resumability
                self.db.save_benchmark_result(record)
                completed_keys.add((p_id, pol))
                eval_count += 1

                if on_progress:
                    on_progress(eval_count, total_evals, record)

        # Retrieve all run results from DB (including previously completed ones)
        run_records = self.db.get_benchmark_results_for_run(run_id)

        # Aggregate metrics
        aggregated = aggregate_benchmark_results(run_records)

        final_report = {
            "run_id": run_id,
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "execution_mode": execution_mode,
            "dataset_version": BENCHMARK_VERSION,
            "dataset_manifest": self.dataset.manifest,
            "total_prompts": len(items),
            "policies_evaluated": policies,
            "generation_settings": {
                "temperature": temperature,
                "max_tokens": max_tokens
            },
            "summary_metrics": aggregated["policies"],
            "comparisons_vs_always_large": aggregated["comparisons"],
            "category_breakdown": aggregated["by_category"]
        }

        # Save to database
        self.db.update_benchmark_run_status(run_id, "completed", final_report)

        # Export JSON and CSV files
        self._export_files(run_id, final_report, run_records)

        return final_report

    def _export_files(self, run_id: str, report: dict, records: list):
        """Export report JSON and raw measurements CSV."""
        # JSON Report
        report_path = self.results_dir / f"{run_id}_report.json"
        latest_path = self.results_dir / "latest_report.json"
        with open(report_path, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2)
        with open(latest_path, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2)

        # CSV Export
        csv_path = self.results_dir / f"{run_id}_results.csv"
        latest_csv_path = self.results_dir / "latest_results.csv"
        fieldnames = [
            "run_id", "prompt_id", "category", "policy", "selected_model",
            "model_id", "latency", "prompt_tokens", "completion_tokens", "cost",
            "quality_score", "eval_details", "error"
        ]
        for p in [csv_path, latest_csv_path]:
            with open(p, "w", newline="", encoding="utf-8") as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
                writer.writeheader()
                for r in records:
                    writer.writerow(r)

        print(f"\n[BenchmarkRunner] Results successfully saved:")
        print(f"  Report JSON: {report_path}")
        print(f"  Results CSV: {csv_path}")
