"""
train.py — Train the Adaptive LLM Router classifier and run evaluation.

This script:
  1. Generates queries.csv if missing.
  2. Runs the research-grade evaluation pipeline (evaluate.py):
     - Reproducible 70/15/15 stratified split (seed=42)
     - Fits TF-IDF + scaler on train split only
     - Reports in-sample train, validation, and held-out test metrics
     - Reports rule-based and most-frequent-class baselines
  3. Saves production model artifacts (model.pkl, vectorizer.pkl,
     scaler.pkl, metrics.json) with held-out TEST metrics — NOT training metrics.
  4. Saves eval_report.json with the full evaluation breakdown.

Usage:
    python train.py              # standard run
    python train.py --seed 99    # custom seed
"""

import sys
import os
import argparse
from pathlib import Path

# Ensure backend root is importable
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config import DATA_DIR, MODEL_DIR
from evaluate import run_evaluation


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Train the LLM routing classifier with research-grade evaluation."
    )
    parser.add_argument(
        "--seed", type=int, default=42,
        help="Random seed for reproducible splits (default: 42)."
    )
    args = parser.parse_args()

    data_path = DATA_DIR / "queries.csv"

    # Generate dataset if missing
    if not data_path.exists():
        print("queries.csv not found — generating...")
        gen_script = DATA_DIR / "generate_queries.py"
        if gen_script.exists():
            import subprocess
            subprocess.run(
                [sys.executable, str(gen_script)],
                cwd=str(DATA_DIR),
                check=True,
            )
        else:
            print(f"ERROR: {data_path} missing and no generator script found.")
            sys.exit(1)

    # Run full evaluation and save production artifacts
    print(f"\nRunning research-grade evaluation on: {data_path}")
    print(f"Seed: {args.seed}\n")

    run_evaluation(
        csv_path=data_path,
        seed=args.seed,
        save_model=True,   # overwrite production artifacts with held-out metrics
    )

    print(f"\n[OK] Production artifacts saved in: {MODEL_DIR}/")
    print(f"     metrics.json now contains HELD-OUT TEST metrics, not training accuracy.")
    print(f"     Full report: {MODEL_DIR}/eval_report.json\n")
