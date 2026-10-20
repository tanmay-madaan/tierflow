"""
evaluate_robustness.py — Offline robustness evaluation harness for TIERFLOW.

Evaluates the current ML classifier and production router against the
separate robustness dataset (backend/data/robustness_queries.csv).

Key principles:
1. Zero provider/API calls (fully offline).
2. Strict separation: classification accuracy/F1 computed ONLY on cases with
   defensible ground-truth tiers (has_defensible_ground_truth == True).
3. Non-defensible inputs (empty, nonsense, ambiguous) evaluated on routing safety,
   fallback behavior, and escalation frequency.
4. Distinguishes raw classifier predictions from final router decisions.
5. Generates trained_models/robustness_report.json artifact.
"""

import sys
import os
import json
import argparse
from pathlib import Path
from datetime import datetime, timezone
from typing import Dict, Any, List

import numpy as np
import pandas as pd
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, confusion_matrix

BACKEND_DIR = Path(__file__).parent
sys.path.insert(0, str(BACKEND_DIR))

from router.feature_extractor import FeatureExtractor
from router.classifier import MLClassifier
from router.router import Router

DEFAULT_DATASET = BACKEND_DIR / "data" / "robustness_queries.csv"
DEFAULT_OUTPUT = BACKEND_DIR / "trained_models" / "robustness_report.json"

TIER_CLASSES = ["LARGE", "MEDIUM", "SMALL"]


def load_robustness_dataset(filepath: Path) -> pd.DataFrame:
    if not filepath.exists():
        raise FileNotFoundError(f"Robustness dataset not found at: {filepath}")
    df = pd.read_csv(filepath)
    # Ensure boolean conversion
    df["has_defensible_ground_truth"] = df["has_defensible_ground_truth"].astype(str).str.lower() == "true"
    # Replace NaN query with empty string for empty input cases
    df["query"] = df["query"].fillna("")
    return df


def evaluate_model_performance(y_true: List[str], y_pred: List[str], prefix: str = "") -> Dict[str, Any]:
    acc = float(accuracy_score(y_true, y_pred))
    macro_p = float(precision_score(y_true, y_pred, average="macro", zero_division=0))
    macro_r = float(recall_score(y_true, y_pred, average="macro", zero_division=0))
    macro_f1 = float(f1_score(y_true, y_pred, average="macro", zero_division=0))

    cm = confusion_matrix(y_true, y_pred, labels=TIER_CLASSES).tolist()
    
    per_class = {}
    for cls in TIER_CLASSES:
        # binary mask for per-class metrics
        y_true_binary = [1 if y == cls else 0 for y in y_true]
        y_pred_binary = [1 if y == cls else 0 for y in y_pred]
        p = float(precision_score(y_true_binary, y_pred_binary, zero_division=0))
        r = float(recall_score(y_true_binary, y_pred_binary, zero_division=0))
        f = float(f1_score(y_true_binary, y_pred_binary, zero_division=0))
        support = sum(y_true_binary)
        per_class[cls] = {
            "precision": round(p, 4),
            "recall": round(r, 4),
            "f1": round(f, 4),
            "support": support
        }

    return {
        f"{prefix}accuracy": round(acc, 4),
        f"{prefix}macro_precision": round(macro_p, 4),
        f"{prefix}macro_recall": round(macro_r, 4),
        f"{prefix}macro_f1": round(macro_f1, 4),
        f"{prefix}per_class": per_class,
        f"{prefix}confusion_matrix": cm,
        f"{prefix}confusion_matrix_labels": TIER_CLASSES
    }


def run_robustness_evaluation(data_path: Path = DEFAULT_DATASET, output_path: Path = DEFAULT_OUTPUT) -> Dict[str, Any]:
    print("\n" + "="*70)
    print("  TIERFLOW — Milestone 2B: Offline Robustness Evaluation")
    print("="*70)
    print(f"Loading robustness dataset: {data_path}")

    df = load_robustness_dataset(data_path)
    print(f"Total dataset entries: {len(df)}")
    print(f"  Defensible ground-truth cases: {df['has_defensible_ground_truth'].sum()}")
    print(f"  Non-defensible / Fallback cases: {(~df['has_defensible_ground_truth']).sum()}")

    # Initialize components
    fe = FeatureExtractor()
    classifier = MLClassifier()
    router_ca = Router(classifier, fe, policy="confidence_aware", threshold_small=0.60, threshold_medium=0.40)
    router_legacy = Router(classifier, fe, policy="legacy_threshold", legacy_threshold=0.50)

    records = []
    for _, row in df.iterrows():
        q = row["query"]
        case_type = row["case_type"]
        gt_tier = row["ground_truth_tier"]
        exp_tier = row["expected_routing_tier"]
        has_gt = row["has_defensible_ground_truth"]

        # 1. Raw classifier prediction (handle empty safely if classifier doesn't guard)
        if not q or not q.strip():
            # Linear model feature vector for empty string
            clf_res = classifier.predict(q or "")
        else:
            clf_res = classifier.predict(q)

        clf_tier = clf_res["selected_model"]
        clf_conf = float(clf_res["confidence"])
        clf_probs = {k: float(v) for k, v in clf_res.get("probabilities", {}).items()}

        # 2. Production Confidence-Aware Router
        res_ca = router_ca.route(q)
        # 3. Legacy flat-0.50 Router
        res_leg = router_legacy.route(q)

        records.append({
            "id": row["id"],
            "query": q,
            "case_type": case_type,
            "ground_truth_tier": gt_tier,
            "expected_routing_tier": exp_tier,
            "has_defensible_ground_truth": has_gt,
            "clf_pred": clf_tier,
            "clf_conf": clf_conf,
            "clf_probs": clf_probs,
            "router_selected": res_ca["selected_model"],
            "router_initial": res_ca["initial_model"],
            "router_conf": res_ca["confidence"],
            "router_escalated": res_ca["was_escalated"],
            "router_escalation_reason": res_ca["escalation_reason"],
            "router_complexity": res_ca["complexity"],
            "legacy_selected": res_leg["selected_model"],
            "legacy_escalated": res_leg["was_escalated"],
            "legacy_escalation_reason": res_leg["escalation_reason"],
            "query_length": len(q),
            "word_count": len(q.split())
        })

    eval_df = pd.DataFrame(records)

    # ── 1. Defensible Ground-Truth Performance (N=65) ─────────────────────────
    gt_df = eval_df[eval_df["has_defensible_ground_truth"]].copy()
    y_true = gt_df["ground_truth_tier"].tolist()
    y_clf = gt_df["clf_pred"].tolist()
    y_router = gt_df["router_selected"].tolist()
    y_legacy = gt_df["legacy_selected"].tolist()

    clf_metrics = evaluate_model_performance(y_true, y_clf, prefix="classifier_")
    router_metrics = evaluate_model_performance(y_true, y_router, prefix="router_")
    legacy_metrics = evaluate_model_performance(y_true, y_legacy, prefix="legacy_")

    # False-SMALL rate on difficult cases (LARGE ground truth routed to SMALL)
    large_gt = gt_df[gt_df["ground_truth_tier"] == "LARGE"]
    n_large = len(large_gt)
    clf_false_small = (large_gt["clf_pred"] == "SMALL").sum()
    router_false_small = (large_gt["router_selected"] == "SMALL").sum()
    legacy_false_small = (large_gt["legacy_selected"] == "SMALL").sum()

    # False-LARGE rate on simple cases (SMALL ground truth routed to LARGE)
    small_gt = gt_df[gt_df["ground_truth_tier"] == "SMALL"]
    n_small = len(small_gt)
    clf_false_large = (small_gt["clf_pred"] == "LARGE").sum()
    router_false_large = (small_gt["router_selected"] == "LARGE").sum()
    legacy_false_large = (small_gt["legacy_selected"] == "LARGE").sum()

    # ── 2. Breakdown by Case Type ─────────────────────────────────────────────
    case_type_reports = {}
    for ct in df["case_type"].unique():
        ct_sub = eval_df[eval_df["case_type"] == ct]
        has_def = ct_sub["has_defensible_ground_truth"].iloc[0]
        
        clf_dist = ct_sub["clf_pred"].value_counts().to_dict()
        router_dist = ct_sub["router_selected"].value_counts().to_dict()
        esc_count = ct_sub["router_escalated"].sum()
        mean_conf = float(ct_sub["clf_conf"].mean())
        min_conf = float(ct_sub["clf_conf"].min())
        max_conf = float(ct_sub["clf_conf"].max())
        
        ct_data = {
            "count": len(ct_sub),
            "has_defensible_ground_truth": bool(has_def),
            "classifier_tier_distribution": clf_dist,
            "router_tier_distribution": router_dist,
            "escalation_count": int(esc_count),
            "escalation_pct": round(float(esc_count / len(ct_sub) * 100), 2),
            "mean_classifier_confidence": round(mean_conf, 4),
            "min_classifier_confidence": round(min_conf, 4),
            "max_classifier_confidence": round(max_conf, 4),
        }

        if has_def:
            sub_y_true = ct_sub["ground_truth_tier"].tolist()
            sub_y_clf = ct_sub["clf_pred"].tolist()
            sub_y_router = ct_sub["router_selected"].tolist()
            ct_data["classifier_accuracy"] = round(float(accuracy_score(sub_y_true, sub_y_clf)), 4)
            ct_data["router_accuracy"] = round(float(accuracy_score(sub_y_true, sub_y_router)), 4)
            ct_data["ground_truth_distribution"] = ct_sub["ground_truth_tier"].value_counts().to_dict()
        else:
            # For non-defensible cases, check adherence to expected safe routing tier (e.g. MEDIUM)
            sub_exp = ct_sub["expected_routing_tier"].tolist()
            sub_y_router = ct_sub["router_selected"].tolist()
            matches_exp = sum(1 for a, b in zip(sub_y_router, sub_exp) if a == b)
            ct_data["safe_routing_adherence_count"] = matches_exp
            ct_data["safe_routing_adherence_pct"] = round(float(matches_exp / len(ct_sub) * 100), 2)

        case_type_reports[ct] = ct_data

    # ── 3. High-Confidence Failure Analysis ───────────────────────────────────
    # Defensible cases where classifier was >= 0.80 confident but INCORRECT
    high_conf_failures = []
    for _, r in gt_df.iterrows():
        if r["clf_pred"] != r["ground_truth_tier"] and r["clf_conf"] >= 0.80:
            high_conf_failures.append({
                "id": r["id"],
                "query": r["query"][:75] + ("..." if len(r["query"]) > 75 else ""),
                "case_type": r["case_type"],
                "ground_truth": r["ground_truth_tier"],
                "predicted": r["clf_pred"],
                "router_selected": r["router_selected"],
                "confidence": round(r["clf_conf"], 4)
            })

    # Non-defensible cases where classifier was >= 0.80 confident on garbage/empty
    garbage_high_conf = []
    for _, r in eval_df[~eval_df["has_defensible_ground_truth"]].iterrows():
        if r["clf_conf"] >= 0.70:
            garbage_high_conf.append({
                "id": r["id"],
                "query": repr(r["query"][:60]),
                "case_type": r["case_type"],
                "predicted": r["clf_pred"],
                "confidence": round(r["clf_conf"], 4),
                "router_selected": r["router_selected"]
            })

    # ── 4. Construct Final Report ─────────────────────────────────────────────
    report = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "dataset_path": str(data_path),
        "total_queries": len(eval_df),
        "defensible_ground_truth_count": len(gt_df),
        "non_defensible_count": len(eval_df) - len(gt_df),
        "methodology_notes": [
            "Classification accuracy and F1 metrics computed ONLY on the 65 cases with defensible ground truth.",
            "Empty inputs, random nonsense, and ambiguous queries have ground_truth_tier=NONE and are excluded from accuracy.",
            "Zero provider calls were made; evaluation is completely offline and reproducible.",
            "High classifier confidence on out-of-distribution or nonsense text demonstrates linear model overconfidence."
        ],
        "defensible_ground_truth_metrics": {
            "classifier": clf_metrics,
            "production_router_confidence_aware": router_metrics,
            "legacy_router_0.50": legacy_metrics,
            "false_small_risk": {
                "large_queries_total": n_large,
                "classifier_false_small_count": int(clf_false_small),
                "classifier_false_small_rate_pct": round(float(clf_false_small / n_large * 100), 2),
                "router_false_small_count": int(router_false_small),
                "router_false_small_rate_pct": round(float(router_false_small / n_large * 100), 2),
                "legacy_false_small_count": int(legacy_false_small),
                "legacy_false_small_rate_pct": round(float(legacy_false_small / n_large * 100), 2)
            },
            "false_large_risk": {
                "small_queries_total": n_small,
                "classifier_false_large_count": int(clf_false_large),
                "classifier_false_large_rate_pct": round(float(clf_false_large / n_small * 100), 2),
                "router_false_large_count": int(router_false_large),
                "router_false_large_rate_pct": round(float(router_false_large / n_small * 100), 2),
                "legacy_false_large_count": int(legacy_false_large),
                "legacy_false_large_rate_pct": round(float(legacy_false_large / n_small * 100), 2)
            }
        },
        "escalation_summary": {
            "total_escalations": int(eval_df["router_escalated"].sum()),
            "total_escalation_pct": round(float(eval_df["router_escalated"].sum() / len(eval_df) * 100), 2),
            "defensible_escalations": int(gt_df["router_escalated"].sum()),
            "defensible_escalation_pct": round(float(gt_df["router_escalated"].sum() / len(gt_df) * 100), 2),
            "non_defensible_escalations": int(eval_df[~eval_df["has_defensible_ground_truth"]]["router_escalated"].sum()),
            "non_defensible_escalation_pct": round(float(eval_df[~eval_df["has_defensible_ground_truth"]]["router_escalated"].sum() / (len(eval_df) - len(gt_df)) * 100), 2),
        },
        "case_type_breakdown": case_type_reports,
        "high_confidence_failures_on_valid_tasks": high_conf_failures,
        "high_confidence_predictions_on_garbage": garbage_high_conf
    }

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)

    # ── 5. Console Summary Output ─────────────────────────────────────────────
    print("\n" + "-"*70)
    print("  ROBUSTNESS EVALUATION RESULTS (N=65 Defensible Cases)")
    print("-"*70)
    print(f"  Classifier Accuracy        : {clf_metrics['classifier_accuracy']:.4f} | Macro F1: {clf_metrics['classifier_macro_f1']:.4f}")
    print(f"  Production Router Accuracy : {router_metrics['router_accuracy']:.4f} | Macro F1: {router_metrics['router_macro_f1']:.4f}")
    print(f"  Legacy Router (0.50) Acc   : {legacy_metrics['legacy_accuracy']:.4f} | Macro F1: {legacy_metrics['legacy_macro_f1']:.4f}")
    print("-" * 70)
    print("  FALSE-SMALL SEVERITY ANALYSIS (Ground Truth = LARGE, N=28):")
    print(f"    Classifier routed to SMALL : {clf_false_small} / {n_large} ({clf_false_small/n_large*100:.1f}%)")
    print(f"    Prod Router routed to SMALL: {router_false_small} / {n_large} ({router_false_small/n_large*100:.1f}%)")
    print(f"    Legacy Router routed SMALL : {legacy_false_small} / {n_large} ({legacy_false_small/n_large*100:.1f}%)")
    print("-" * 70)
    print("  FALSE-LARGE OVERPAY ANALYSIS (Ground Truth = SMALL, N=21):")
    print(f"    Classifier routed to LARGE : {clf_false_large} / {n_small} ({clf_false_large/n_small*100:.1f}%)")
    print(f"    Prod Router routed to LARGE: {router_false_large} / {n_small} ({router_false_large/n_small*100:.1f}%)")
    print("-" * 70)
    print("  CASE TYPE BREAKDOWN SUMMARY:")
    for ct, d in case_type_reports.items():
        if d["has_defensible_ground_truth"]:
            print(f"    {ct:30s}: Acc={d['router_accuracy']:.2f} | ClfAcc={d['classifier_accuracy']:.2f} | Esc={d['escalation_pct']:5.1f}% | MeanConf={d['mean_classifier_confidence']:.2f} | ClfDist={d['classifier_tier_distribution']}")
        else:
            print(f"    {ct:30s}: FallbackAdherence={d['safe_routing_adherence_pct']:5.1f}% | Esc={d['escalation_pct']:5.1f}% | MeanConf={d['mean_classifier_confidence']:.2f} | ClfDist={d['classifier_tier_distribution']}")
    print("-" * 70)
    print(f"  Robustness report saved to: {output_path}")
    print("=" * 70 + "\n")

    return report


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run offline robustness evaluation.")
    parser.add_argument("--data", type=str, default=str(DEFAULT_DATASET), help="Path to robustness_queries.csv")
    parser.add_argument("--output", type=str, default=str(DEFAULT_OUTPUT), help="Path to output json report")
    args = parser.parse_args()

    run_robustness_evaluation(data_path=Path(args.data), output_path=Path(args.output))
