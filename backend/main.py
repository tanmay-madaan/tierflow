from fastapi import FastAPI, BackgroundTasks, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import asyncio
import json
from pathlib import Path

from config import DEMO_MODE, MODEL_TIERS, BENCHMARK_RESULTS_DIR, API_KEY
from database.db import DatabaseManager
from router.feature_extractor import FeatureExtractor
from router.classifier import MLClassifier
from router.router import Router
from models.small import SmallModelProvider
from models.medium import MediumModelProvider
from models.large import LargeModelProvider
from evaluation.evaluator import QualityEvaluator
from benchmarks.dataset import BenchmarkDataset
from benchmarks.runner import BenchmarkRunner

app = FastAPI(title="Adaptive LLM Router API", version="2.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

db = DatabaseManager()
fe = FeatureExtractor()
classifier = MLClassifier()
router = Router(classifier, fe)
evaluator = QualityEvaluator()

providers = {
    'SMALL': SmallModelProvider(),
    'MEDIUM': MediumModelProvider(),
    'LARGE': LargeModelProvider()
}

class QueryRequest(BaseModel):
    query: str
    demo_mode: bool = True
    execution_mode: Optional[str] = None  # Explicit 'demo' or 'real'

class BenchmarkRunRequest(BaseModel):
    execution_mode: str = "demo"
    limit: Optional[int] = None
    run_id: Optional[str] = None

@app.get("/health")
def health():
    from config import get_active_api_key, LLM_BASE_URL, MODEL_TIERS
    import os
    active_key = get_active_api_key()
    provider_name = "Google Gemini" if ("generativelanguage" in LLM_BASE_URL or bool(os.getenv('GEMINI_API_KEY'))) else "OpenAI"
    return {
        "status": "ok",
        "demo_mode": not bool(active_key),
        "has_api_key": bool(active_key),
        "provider": provider_name,
        "model_trained": classifier.model is not None,
        "model_tiers": {
            t: {"name": cfg["name"], "model_id": cfg["model_id"]}
            for t, cfg in MODEL_TIERS.items()
        }
    }

@app.post("/route")
def route_query(req: QueryRequest):
    return router.route(req.query)

@app.post("/query")
async def process_query(req: QueryRequest):
    routing = router.route(req.query)
    tier = routing['selected_model']
    
    # Determine explicit execution mode
    active_mode = req.execution_mode if req.execution_mode else ("demo" if req.demo_mode else "real")
    is_demo = (active_mode == "demo")

    provider = providers[tier]
    result = await provider.generate(req.query, demo_mode=is_demo, execution_mode=active_mode)

    # If the provider returned an error (e.g. missing API key, rate limit, provider error)
    if result.get('error'):
        # Persist failure telemetry to SQLite before returning
        err_data = {
            "query": req.query,
            "category": "unknown",
            "complexity": routing.get('complexity', 'unknown'),
            "selected_model": tier,
            "confidence": routing.get('confidence'),
            "response": "",
            "latency": result.get('latency', 0.0),
            "estimated_cost": 0.0,
            "quality_score": None,
            "baseline_latency": None,
            "baseline_cost": None,
            "baseline_quality": None,
            "demo_mode": is_demo,
            "execution_mode": active_mode,
            "model_id": result.get('model_id'),
            "prompt_tokens": result.get('token_usage', {}).get('prompt_tokens', 0),
            "completion_tokens": result.get('token_usage', {}).get('completion_tokens', 0),
            "error": result.get('error')
        }
        try:
            db.save_experiment(err_data)
        except Exception as db_err:
            print(f"[Warning] Failed to log experiment failure to database: {db_err}")

        return {
            "routing": routing,
            "response": "",
            "execution_mode": active_mode,
            "model_id": result.get('model_id'),
            "token_usage": result.get('token_usage', {}),
            "error": result.get('error'),
            "metrics": {
                "latency": result.get('latency', 0.0),
                "estimated_cost": 0.0,
                "quality_score": None
            },
            "baseline": None,
            "comparison": None,
            "demo_mode": is_demo
        }

    # Evaluate response quality
    eval_res = evaluator.evaluate(req.query, result.get('response', ''), tier, is_demo)
    cur_lat = result.get('latency', 0.0)
    cur_cost = result.get('estimated_cost', 0.0)
    cur_qual = eval_res.get('overall_score')

    # Baseline (always-large) handling:
    large_provider = providers['LARGE']
    if is_demo:
        # In demo mode, simulate baseline
        baseline_result = await large_provider.generate(req.query, demo_mode=True, execution_mode="demo")
        baseline_eval = evaluator.evaluate(req.query, baseline_result.get('response', ''), 'LARGE', True)
        base_lat = baseline_result.get('latency', 0.0)
        base_cost = baseline_result.get('estimated_cost', 0.0)
        base_qual = baseline_eval.get('overall_score', 0.0)
        base_model_id = baseline_result.get('model_id')
        lat_red = round((base_lat - cur_lat) / base_lat * 100, 2) if base_lat else 0.0
        cost_red = round((base_cost - cur_cost) / base_cost * 100, 2) if base_cost else 0.0
        qual_ret = round(cur_qual / base_qual * 100, 2) if base_qual else 0.0
    else:
        # In real mode: do not fabricate Always-Large baseline latency multipliers (cur_lat * 2.5)
        # or copy query quality into baseline quality to force 100% retention.
        if tier == 'LARGE':
            base_lat = cur_lat
            base_cost = cur_cost
            base_qual = None
            base_model_id = result.get('model_id')
            lat_red = 0.0
            cost_red = 0.0
            qual_ret = None
        else:
            # Counterfactual Always-Large was NOT executed
            base_lat = None
            base_qual = None
            lat_red = None
            qual_ret = None
            base_model_id = large_provider.model_id

            p_tok = result.get('token_usage', {}).get('prompt_tokens', 0)
            c_tok = result.get('token_usage', {}).get('completion_tokens', 0)
            if p_tok > 0 or c_tok > 0:
                base_cost = large_provider.calculate_cost(p_tok, c_tok)
                cost_red = round((base_cost - cur_cost) / base_cost * 100, 2) if base_cost else 0.0
            else:
                base_cost = None
                cost_red = None

    data = {
        "query": req.query,
        "category": "unknown",
        "complexity": routing.get('complexity', 'unknown'),
        "selected_model": tier,
        "confidence": routing.get('confidence'),
        "response": result.get('response', ''),
        "latency": cur_lat,
        "estimated_cost": cur_cost,
        "quality_score": cur_qual,
        "baseline_latency": base_lat,
        "baseline_cost": base_cost,
        "baseline_quality": base_qual,
        "demo_mode": is_demo,
        "execution_mode": active_mode,
        "model_id": result.get('model_id'),
        "prompt_tokens": result.get('token_usage', {}).get('prompt_tokens', 0),
        "completion_tokens": result.get('token_usage', {}).get('completion_tokens', 0),
        "error": result.get('error')
    }
    try:
        db.save_experiment(data)
    except Exception as db_err:
        print(f"[Warning] Failed to log experiment to database: {db_err}")

    return {
        "routing": routing,
        "response": result.get('response', ''),
        "execution_mode": active_mode,
        "model_id": result.get('model_id'),
        "token_usage": result.get('token_usage', {}),
        "error": result.get('error'),
        "metrics": {
            "latency": cur_lat,
            "estimated_cost": cur_cost,
            "quality_score": cur_qual
        },
        "baseline": {
            "latency": base_lat,
            "estimated_cost": base_cost,
            "quality_score": base_qual,
            "model_id": base_model_id
        },
        "comparison": {
            "latency_reduction": lat_red,
            "cost_reduction": cost_red,
            "quality_retention": qual_ret
        },
        "demo_mode": is_demo
    }

@app.get("/metrics")
def get_metrics():
    return db.get_metrics()

@app.get("/experiments")
def get_experiments(limit: int = 100):
    return db.get_experiments(limit)

@app.get("/model-distribution")
def get_model_distribution():
    return db.get_model_distribution()

@app.get("/classifier-metrics")
def get_classifier_metrics():
    return classifier.get_metrics()

# ── Benchmark Endpoints ───────────────────────────────────────────────────────

@app.get("/benchmark/manifest")
def get_benchmark_manifest():
    ds = BenchmarkDataset()
    return ds.manifest

@app.get("/benchmark/latest")
def get_latest_benchmark():
    report = db.get_latest_benchmark_report()
    if not report:
        latest_file = BENCHMARK_RESULTS_DIR / "latest_report.json"
        if latest_file.exists():
            with open(latest_file, "r", encoding="utf-8") as f:
                return json.load(f)
        return {"status": "no_runs", "message": "No benchmark runs completed yet."}
    return report

@app.post("/benchmark/run")
async def trigger_benchmark_run(req: BenchmarkRunRequest):
    runner = BenchmarkRunner(
        db=db,
        providers=providers,
        router=router,
        feature_extractor=fe
    )
    report = await runner.run(
        execution_mode=req.execution_mode,
        limit_items=req.limit,
        run_id=req.run_id
    )
    return report
