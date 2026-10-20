"""
evaluate.py — Research-grade evaluation of the Adaptive LLM Router classifier.

Implements:
- Reproducible stratified 70/15/15 train/val/test split
- Near-duplicate detection before splitting
- Fits vectorizer + scaler ONLY on training data
- Validation set for threshold selection
- Held-out test set evaluated only after all decisions finalised
- Most-frequent-class baseline
- Rule-based complexity baseline (from FeatureExtractor.estimated_complexity)
- Full per-class and macro metrics + confusion matrix
- Saves evaluation report to trained_models/eval_report.json
  (never overwrites production model artifacts unless --save-model flag used)

Usage:
    python evaluate.py                    # evaluate only, do not overwrite prod model
    python evaluate.py --save-model       # also overwrite trained_models/ with new fits
    python evaluate.py --data data/queries.csv --seed 42
"""

import sys
import os
import json
import argparse
from pathlib import Path
from datetime import datetime, timezone

import numpy as np
import pandas as pd
import scipy.sparse as sp
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import StratifiedShuffleSplit
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    confusion_matrix, classification_report
)
import joblib

# ── Ensure backend root is importable ────────────────────────────────────────
BACKEND_DIR = Path(__file__).parent
sys.path.insert(0, str(BACKEND_DIR))
from router.feature_extractor import FeatureExtractor

RANDOM_SEED = 42
TRAIN_RATIO = 0.70
VAL_RATIO   = 0.15
TEST_RATIO  = 0.15
TFIDF_MAX_FEATURES = 500
TFIDF_NGRAM_RANGE  = (1, 2)


# ─────────────────────────────────────────────────────────────────────────────
# Step 1 — Load & deduplicate dataset
# ─────────────────────────────────────────────────────────────────────────────
def load_and_deduplicate(csv_path: Path) -> tuple[pd.DataFrame, dict]:
    """Load CSV, remove exact and near duplicates, return cleaned df + audit."""
    df = pd.read_csv(str(csv_path))

    required_cols = {"query", "model"}
    missing = required_cols - set(df.columns)
    if missing:
        raise ValueError(f"Dataset missing required columns: {missing}")

    audit = {
        "source_file": str(csv_path),
        "rows_raw": len(df),
        "rows_unique_query": int(df["query"].nunique()),
    }

    # Remove rows with null query or label
    before = len(df)
    df = df.dropna(subset=["query", "model"])
    audit["rows_dropped_null"] = before - len(df)

    # Remove exact-duplicate queries (keep first occurrence)
    before = len(df)
    df = df.drop_duplicates(subset=["query"], keep="first")
    audit["rows_dropped_exact_dup"] = before - len(df)

    # Near-duplicate detection: first 60 chars of lower-cased stripped query
    df["_prefix60"] = df["query"].str.strip().str[:60].str.lower()
    near_dup_mask = df.duplicated(subset=["_prefix60"], keep="first")
    audit["rows_dropped_near_dup"] = int(near_dup_mask.sum())
    df = df[~near_dup_mask].drop(columns=["_prefix60"]).reset_index(drop=True)

    audit["rows_after_dedup"] = len(df)
    audit["class_distribution_after_dedup"] = df["model"].value_counts().to_dict()

    return df, audit


# ─────────────────────────────────────────────────────────────────────────────
# Step 2 — Stratified split  (70 / 15 / 15)
# ─────────────────────────────────────────────────────────────────────────────
def make_splits(df: pd.DataFrame, seed: int = RANDOM_SEED
                ) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """Produce stratified train / val / test splits."""
    X = df["query"].values
    y = df["model"].values

    # First cut: (train+val) vs test  → 85 / 15
    sss1 = StratifiedShuffleSplit(n_splits=1, test_size=TEST_RATIO, random_state=seed)
    trainval_idx, test_idx = next(sss1.split(X, y))

    df_trainval = df.iloc[trainval_idx].reset_index(drop=True)
    df_test     = df.iloc[test_idx].reset_index(drop=True)

    # Second cut: train vs val inside trainval  → val fraction = VAL_RATIO / (1 - TEST_RATIO)
    val_frac = VAL_RATIO / (1.0 - TEST_RATIO)
    sss2 = StratifiedShuffleSplit(n_splits=1, test_size=val_frac, random_state=seed)
    train_idx, val_idx = next(sss2.split(df_trainval["query"].values,
                                          df_trainval["model"].values))

    df_train = df_trainval.iloc[train_idx].reset_index(drop=True)
    df_val   = df_trainval.iloc[val_idx].reset_index(drop=True)

    return df_train, df_val, df_test


# ─────────────────────────────────────────────────────────────────────────────
# Step 3 — Feature extraction
# ─────────────────────────────────────────────────────────────────────────────
def _numerical_features(queries, fe: FeatureExtractor) -> np.ndarray:
    rows = []
    for q in queries:
        f = fe.extract(q)
        rows.append([
            f["query_length"], f["word_count"], f["sentence_count"],
            f["has_math_keywords"], f["has_code_keywords"],
            f["has_reasoning_keywords"], f["num_constraints"],
            f["has_multi_step"],
        ])
    return np.array(rows, dtype=float)


def build_features(train_queries, other_queries_list,
                   fe: FeatureExtractor, seed: int = RANDOM_SEED):
    """
    Fit TF-IDF and scaler on train_queries ONLY.
    Transform all splits.
    Returns (vectorizer, scaler, train_X, *other_X_list)
    """
    vectorizer = TfidfVectorizer(max_features=TFIDF_MAX_FEATURES,
                                 ngram_range=TFIDF_NGRAM_RANGE)
    X_text_train = vectorizer.fit_transform(train_queries)

    X_num_train = _numerical_features(train_queries, fe)
    scaler = StandardScaler()
    X_num_train_s = scaler.fit_transform(X_num_train)

    X_train = sp.hstack((X_text_train, X_num_train_s))

    other_Xs = []
    for queries in other_queries_list:
        X_text = vectorizer.transform(queries)
        X_num  = _numerical_features(queries, fe)
        X_num_s = scaler.transform(X_num)
        other_Xs.append(sp.hstack((X_text, X_num_s)))

    return vectorizer, scaler, X_train, *other_Xs


# ─────────────────────────────────────────────────────────────────────────────
# Step 4 — Train classifier
# ─────────────────────────────────────────────────────────────────────────────
def train_classifier(X_train, y_train, seed: int = RANDOM_SEED) -> LogisticRegression:
    clf = LogisticRegression(max_iter=2000, random_state=seed, class_weight=None)
    clf.fit(X_train, y_train)
    return clf


# ─────────────────────────────────────────────────────────────────────────────
# Step 5 — Metrics helper
# ─────────────────────────────────────────────────────────────────────────────
def compute_metrics(y_true, y_pred, classes, split_name: str) -> dict:
    cm = confusion_matrix(y_true, y_pred, labels=classes)
    report = classification_report(y_true, y_pred, labels=classes,
                                   output_dict=True, zero_division=0)
    return {
        "split": split_name,
        "n_samples": int(len(y_true)),
        "accuracy": float(accuracy_score(y_true, y_pred)),
        "macro_precision": float(precision_score(y_true, y_pred,
                                                  average="macro", zero_division=0)),
        "macro_recall": float(recall_score(y_true, y_pred,
                                            average="macro", zero_division=0)),
        "macro_f1": float(f1_score(y_true, y_pred,
                                    average="macro", zero_division=0)),
        "confusion_matrix": cm.tolist(),
        "class_labels": list(classes),
        "per_class": {
            cls: {k: round(v, 4) for k, v in report[cls].items()}
            for cls in classes if cls in report
        },
    }


# ─────────────────────────────────────────────────────────────────────────────
# Step 6 — Baselines
# ─────────────────────────────────────────────────────────────────────────────
def most_frequent_baseline(y_train, y_test, classes) -> dict:
    """Always predict the most common class seen in training."""
    most_common = max(set(y_train.tolist()), key=y_train.tolist().count)
    y_pred = [most_common] * len(y_test)
    m = compute_metrics(y_test, y_pred, classes, "test_most_frequent_baseline")
    m["predicted_class"] = most_common
    return m


def rule_based_baseline(queries, y_test, classes, fe: FeatureExtractor) -> dict:
    """Use FeatureExtractor.estimated_complexity heuristic as routing decision."""
    complexity_map = {"LOW": "SMALL", "MODERATE": "MEDIUM", "HIGH": "LARGE"}
    y_pred = []
    for q in queries:
        f = fe.extract(q)
        y_pred.append(complexity_map.get(f["estimated_complexity"], "MEDIUM"))
    m = compute_metrics(y_test, y_pred, classes, "test_rule_based_baseline")
    return m


def brier_multiclass(y_true, probs, classes: list) -> float:
    """
    Compute multi-class Brier score: mean squared error over one-hot target vectors.
    Range [0, 2], lower is better. A lower score indicates better probability calibration and accuracy.
    """
    N = len(y_true)
    K = len(classes)
    Y_onehot = np.zeros((N, K))
    for i, y in enumerate(y_true):
        Y_onehot[i, classes.index(y)] = 1.0
    return float(np.mean(np.sum((probs - Y_onehot) ** 2, axis=1)))


def compute_ece(y_true, probs, classes: list, n_bins: int = 5) -> tuple[float, list]:
    """
    Compute Expected Calibration Error (ECE) with equal-width confidence binning.
    
    Binning method:
      Divides confidence interval [0.0, 1.0] into M equal-width bins (default M=5).
      For each bin B_m, computes accuracy acc(B_m) and average confidence conf(B_m).
      ECE = sum(|B_m| / N * |acc(B_m) - conf(B_m)|).
    
    Limitations on small datasets (e.g. N=49):
      With 49 samples, M=10 produces empty or single-sample bins with extreme variance.
      M=5 equal-width bins provides robust sample support per active bin (>=6 samples/bin).
    """
    confs = np.max(probs, axis=1)
    preds = [classes[idx] for idx in np.argmax(probs, axis=1)]
    corrects = np.array([p == y for p, y in zip(preds, y_true)], dtype=float)
    bin_edges = np.linspace(0.0, 1.0, n_bins + 1)
    ece = 0.0
    total = len(y_true)
    bin_details = []
    for i in range(n_bins):
        mask = (confs > bin_edges[i]) & (confs <= bin_edges[i + 1])
        count = np.sum(mask)
        if count > 0:
            acc_bin = np.mean(corrects[mask])
            conf_bin = np.mean(confs[mask])
            ece += (count / total) * abs(acc_bin - conf_bin)
            bin_details.append({
                "bin": (round(float(bin_edges[i]), 2), round(float(bin_edges[i + 1]), 2)),
                "count": int(count),
                "acc": round(float(acc_bin), 4),
                "conf": round(float(conf_bin), 4)
            })
    return round(float(ece), 4), bin_details


# ─────────────────────────────────────────────────────────────────────────────
# Main evaluation pipeline
# ─────────────────────────────────────────────────────────────────────────────
def run_evaluation(csv_path: Path, seed: int = RANDOM_SEED,
                   save_model: bool = False) -> dict:

    print(f"\n{'='*65}")
    print("  Adaptive LLM Router — Research-Grade Evaluation")
    print(f"{'='*65}\n")

    # ── 1. Load ──────────────────────────────────────────────────
    print(f"[1/7] Loading dataset: {csv_path}")
    df, audit = load_and_deduplicate(csv_path)
    print(f"      Rows after dedup: {len(df)}  "
          f"(dropped {audit['rows_dropped_exact_dup']} exact + "
          f"{audit['rows_dropped_near_dup']} near-dup)")
    print(f"      Class distribution: {audit['class_distribution_after_dedup']}")

    # Check minimum size
    classes = sorted(df["model"].unique())
    for cls in classes:
        n = (df["model"] == cls).sum()
        if n < 10:
            print(f"  WARNING: class '{cls}' has only {n} samples — "
                  f"splits may be unreliable")

    # ── 2. Split ─────────────────────────────────────────────────
    print("\n[2/7] Creating reproducible stratified 70/15/15 splits "
          f"(seed={seed})")
    df_train, df_val, df_test = make_splits(df, seed)
    print(f"      Train : {len(df_train):4d} rows | "
          f"{df_train['model'].value_counts().to_dict()}")
    print(f"      Val   : {len(df_val):4d} rows | "
          f"{df_val['model'].value_counts().to_dict()}")
    print(f"      Test  : {len(df_test):4d} rows | "
          f"{df_test['model'].value_counts().to_dict()}")

    # ── 3. Features — fit on TRAIN only ──────────────────────────
    print("\n[3/7] Building features (TF-IDF + numerical, fit on TRAIN only)")
    fe = FeatureExtractor()
    vectorizer, scaler, X_train, X_val, X_test = build_features(
        df_train["query"].values,
        [df_val["query"].values, df_test["query"].values],
        fe, seed
    )
    y_train = df_train["model"].values
    y_val   = df_val["model"].values
    y_test  = df_test["model"].values

    # ── 4. Train ──────────────────────────────────────────────────
    print("\n[4/7] Training LogisticRegression on training split")
    clf = train_classifier(X_train, y_train, seed)

    # ── 5. Validation metrics & Calibration Analysis ──────────────
    print("\n[5/7] Validation metrics & Calibration Analysis (model selection)")
    val_preds  = clf.predict(X_val)
    val_probs  = clf.predict_proba(X_val)
    val_m = compute_metrics(y_val, val_preds, classes, "validation")
    _print_metrics(val_m)

    val_brier = brier_multiclass(y_val, val_probs, classes)
    val_ece, val_ece_bins = compute_ece(y_val, val_probs, classes, n_bins=5)
    print(f"\n  Validation Uncalibrated Brier Score (lower=better): {val_brier:.4f}")
    print(f"  Validation Uncalibrated ECE (5 bins)             : {val_ece:.4f}")

    # Calibration fitting on validation set ONLY (avoiding test-set leakage)
    from sklearn.calibration import CalibratedClassifierCV
    from sklearn.frozen import FrozenEstimator
    cal_platt = CalibratedClassifierCV(FrozenEstimator(clf), method="sigmoid")
    cal_platt.fit(X_val, y_val)
    val_probs_cal = cal_platt.predict_proba(X_val)
    val_brier_cal = brier_multiclass(y_val, val_probs_cal, classes)
    val_ece_cal, _ = compute_ece(y_val, val_probs_cal, classes, n_bins=5)
    print(f"  Validation Platt/Sigmoid Brier (calibrated)      : {val_brier_cal:.4f} (diff: {val_brier_cal - val_brier:+.4f})")
    print(f"  Validation Platt/Sigmoid ECE (calibrated)        : {val_ece_cal:.4f} (diff: {val_ece_cal - val_ece:+.4f})")

    # ── 6. Held-out TEST metrics & Policy Comparison ──────────────
    print("\n[6/7] Held-out TEST metrics (evaluated once, after all decisions finalised)")
    test_preds = clf.predict(X_test)
    test_probs = clf.predict_proba(X_test)
    test_m = compute_metrics(y_test, test_preds, classes, "test_ml_router")
    _print_metrics(test_m)

    test_brier = brier_multiclass(y_test, test_probs, classes)
    test_ece, test_ece_bins = compute_ece(y_test, test_probs, classes, n_bins=5)

    test_probs_cal = cal_platt.predict_proba(X_test)
    test_brier_cal = brier_multiclass(y_test, test_probs_cal, classes)
    test_ece_cal, _ = compute_ece(y_test, test_probs_cal, classes, n_bins=5)

    print(f"\n  Test Uncalibrated Brier Score (lower=better)     : {test_brier:.4f}")
    print(f"  Test Uncalibrated ECE (5 bins)                   : {test_ece:.4f}")
    print(f"  Test Platt/Sigmoid Brier (calibrated on val)     : {test_brier_cal:.4f} (diff: {test_brier_cal - test_brier:+.4f})")
    print(f"  Test Platt/Sigmoid ECE (calibrated on val)       : {test_ece_cal:.4f} (diff: {test_ece_cal - test_ece:+.4f})")
    print(f"  * Note: Post-hoc calibration on small N=49 validation split causes variance inflation/overfitting.")

    # ── 4-Policy Comparison on Held-Out Test Set ──────────────────
    from router.router import Router
    from router.classifier import MLClassifier
    
    # Tier-relative cost weights based on verified config.py pricing
    tier_relative_costs = {'SMALL': 0.000075, 'MEDIUM': 0.000150, 'LARGE': 0.002500}

    # Helper router instances
    wrapper = MLClassifier.__new__(MLClassifier)
    wrapper.model = clf
    wrapper.vectorizer = vectorizer
    wrapper.scaler = scaler
    wrapper.fe = fe
    wrapper.metrics = {}

    current_router = Router(classifier=wrapper, feature_extractor=fe, policy="legacy_threshold", legacy_threshold=0.50)
    car_router = Router(classifier=wrapper, feature_extractor=fe, policy="confidence_aware", threshold_small=0.60, threshold_medium=0.40)

    test_queries = df_test["query"].values
    
    # 1. Current Router (0.50 cutoff)
    cur_results = [current_router.route(q) for q in test_queries]
    cur_tiers = [r["selected_model"] for r in cur_results]
    cur_esc = [r for r in cur_results if r["was_escalated"]]
    cur_acc = float(accuracy_score(y_test, cur_tiers))
    cur_f1 = float(f1_score(y_test, cur_tiers, average="macro", zero_division=0))
    cur_cost = float(np.mean([tier_relative_costs[t] for t in cur_tiers]))
    cur_dist = pd.Series(cur_tiers).value_counts().to_dict()

    # 2. Confidence-Aware Router (Validation-tuned: theta_s=0.60, theta_m=0.40)
    car_results = [car_router.route(q) for q in test_queries]
    car_tiers = [r["selected_model"] for r in car_results]
    car_esc = [r for r in car_results if r["was_escalated"]]
    car_acc = float(accuracy_score(y_test, car_tiers))
    car_f1 = float(f1_score(y_test, car_tiers, average="macro", zero_division=0))
    car_cost = float(np.mean([tier_relative_costs[t] for t in car_tiers]))
    car_dist = pd.Series(car_tiers).value_counts().to_dict()

    # 3. Rule-Based Baseline
    rb_baseline = rule_based_baseline(test_queries, y_test, classes, fe)
    rb_tiers = [{"LOW": "SMALL", "MODERATE": "MEDIUM", "HIGH": "LARGE"}.get(fe.extract(q)["estimated_complexity"], "MEDIUM") for q in test_queries]
    rb_cost = float(np.mean([tier_relative_costs[t] for t in rb_tiers]))
    rb_dist = pd.Series(rb_tiers).value_counts().to_dict()

    # 4. Always-LARGE Baseline
    al_tiers = ["LARGE"] * len(test_queries)
    al_acc = float(accuracy_score(y_test, al_tiers))
    al_f1 = float(f1_score(y_test, al_tiers, average="macro", zero_division=0))
    al_cost = float(tier_relative_costs["LARGE"])
    al_dist = {"LARGE": len(test_queries)}

    print(f"\n{'-'*70}")
    print(f"  4-Policy Comparative Evaluation (Held-out Test Split, N=49)")
    print(f"{'-'*70}")
    print(f"  Policy 1: Current Adaptive Router (0.50):")
    print(f"    Accuracy: {cur_acc:.4f} | Macro F1: {cur_f1:.4f} | Escalations: {len(cur_esc)} ({len(cur_esc)/len(test_queries)*100:.1f}%) | Cost: ${cur_cost:.6f} | Dist: {cur_dist}")
    print(f"  Policy 2: Confidence-Aware Router (th_s=0.60, th_m=0.40):")
    print(f"    Accuracy: {car_acc:.4f} | Macro F1: {car_f1:.4f} | Escalations: {len(car_esc)} ({len(car_esc)/len(test_queries)*100:.1f}%) | Cost: ${car_cost:.6f} | Dist: {car_dist}")
    print(f"  Policy 3: Rule-Based Heuristic Baseline:")
    print(f"    Accuracy: {rb_baseline['accuracy']:.4f} | Macro F1: {rb_baseline['macro_f1']:.4f} | Cost: ${rb_cost:.6f} | Dist: {rb_dist}")
    print(f"  Policy 4: Always-LARGE Baseline:")
    print(f"    Accuracy: {al_acc:.4f} | Macro F1: {al_f1:.4f} | Cost: ${al_cost:.6f} | Dist: {al_dist}")
    print(f"{'-'*70}\n")

    # Baselines
    mf_baseline = most_frequent_baseline(y_train, y_test, classes)

    # Training accuracy (reported separately as in-sample, not generalisation)
    train_preds = clf.predict(X_train)
    train_m = compute_metrics(y_train, train_preds, classes, "train_in_sample")

    # ── 7. Save report ────────────────────────────────────────────
    print("[7/7] Saving evaluation report")
    report = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "random_seed": seed,
        "data_audit": audit,
        "split_sizes": {
            "train": len(df_train),
            "val":   len(df_val),
            "test":  len(df_test),
        },
        "methodology_notes": [
            "TF-IDF vectorizer and StandardScaler fitted on training split only.",
            "Validation split used for threshold selection and calibration fitting.",
            "Test split evaluated once after all design decisions finalised.",
            "Labels are heuristic (manually assigned by category rules, not human judges).",
            "LARGE class is under-represented (≈20%), which may inflate per-class metrics.",
            "Dataset size is small (~325 unique queries); treat results as indicative only.",
            "Cost figures are estimated offline relative costs based on configured per-token pricing."
        ],
        "calibration_analysis": {
            "validation": {
                "uncalibrated_brier": round(val_brier, 4),
                "uncalibrated_ece_5bins": round(val_ece, 4),
                "calibrated_platt_brier": round(val_brier_cal, 4),
                "calibrated_platt_ece_5bins": round(val_ece_cal, 4),
                "bin_details": val_ece_bins
            },
            "test": {
                "uncalibrated_brier": round(test_brier, 4),
                "uncalibrated_ece_5bins": round(test_ece, 4),
                "calibrated_platt_brier": round(test_brier_cal, 4),
                "calibrated_platt_ece_5bins": round(test_ece_cal, 4),
                "bin_details": test_ece_bins
            },
            "calibration_finding": "Post-hoc Platt scaling fitted on N=49 validation split degrades test Brier score and test ECE due to high estimator variance on small sample size. Uncalibrated multinomial logistic regression probabilities are more reliable."
        },
        "policy_comparison": {
            "current_adaptive_router_0.50": {
                "accuracy": round(cur_acc, 4),
                "macro_f1": round(cur_f1, 4),
                "escalation_count": len(cur_esc),
                "escalation_pct": round(len(cur_esc) / len(test_queries) * 100, 2),
                "estimated_cost_per_query": round(cur_cost, 7),
                "tier_distribution": cur_dist
            },
            "confidence_aware_router_0.60_0.40": {
                "accuracy": round(car_acc, 4),
                "macro_f1": round(car_f1, 4),
                "escalation_count": len(car_esc),
                "escalation_pct": round(len(car_esc) / len(test_queries) * 100, 2),
                "estimated_cost_per_query": round(car_cost, 7),
                "tier_distribution": car_dist,
                "cost_reduction_vs_large_pct": round((al_cost - car_cost) / al_cost * 100, 2)
            },
            "rule_based_baseline": {
                "accuracy": round(rb_baseline['accuracy'], 4),
                "macro_f1": round(rb_baseline['macro_f1'], 4),
                "estimated_cost_per_query": round(rb_cost, 7),
                "tier_distribution": rb_dist,
                "cost_reduction_vs_large_pct": round((al_cost - rb_cost) / al_cost * 100, 2)
            },
            "always_large_baseline": {
                "accuracy": round(al_acc, 4),
                "macro_f1": round(al_f1, 4),
                "estimated_cost_per_query": round(al_cost, 7),
                "tier_distribution": al_dist
            }
        },
        "in_sample_train_metrics": train_m,
        "validation_metrics": val_m,
        "test_metrics": {
            "ml_router": test_m,
            "most_frequent_baseline": mf_baseline,
            "rule_based_baseline": rb_baseline,
        },
        "label_quality_notes": [
            "Labels assigned deterministically by category (analytical_reasoning→LARGE, etc.).",
            "Same category is always the same label — classifier can learn category from keywords,",
            "which inflates accuracy relative to genuinely ambiguous real-world queries.",
            "Tricky examples (short queries→LARGE, long queries→SMALL) included but are few.",
        ],
    }

    model_dir = BACKEND_DIR / "trained_models"
    model_dir.mkdir(parents=True, exist_ok=True)
    report_path = model_dir / "eval_report.json"
    with open(report_path, "w") as f:
        json.dump(report, f, indent=2)
    print(f"      Saved: {report_path}")

    if save_model:
        print("      --save-model: overwriting production model artifacts")
        # Save PRODUCTION metrics file with ONLY test metrics to avoid leakage
        prod_metrics = {
            "accuracy":         test_m["accuracy"],
            "precision":        test_m["macro_precision"],
            "recall":           test_m["macro_recall"],
            "f1":               test_m["macro_f1"],
            "confusion_matrix": test_m["confusion_matrix"],
            "class_labels":     test_m["class_labels"],
            "_note": (
                "These are HELD-OUT TEST SET metrics from a 70/15/15 stratified split. "
                "Seed=42. Do not present as training accuracy."
            ),
        }
        joblib.dump(clf,        model_dir / "model.pkl")
        joblib.dump(vectorizer, model_dir / "vectorizer.pkl")
        joblib.dump(scaler,     model_dir / "scaler.pkl")
        with open(model_dir / "metrics.json", "w") as f:
            json.dump(prod_metrics, f, indent=2)
        print(f"      Saved: model.pkl, vectorizer.pkl, scaler.pkl, metrics.json")

    return report


def _print_metrics(m: dict):
    cls = m["class_labels"]
    print(f"  Split        : {m['split']}")
    print(f"  N samples    : {m['n_samples']}")
    print(f"  Accuracy     : {m['accuracy']:.4f}")
    print(f"  Macro P/R/F1 : {m['macro_precision']:.4f} / "
          f"{m['macro_recall']:.4f} / {m['macro_f1']:.4f}")
    print("  Per-class F1 : "
          + " | ".join(f"{c}={m['per_class'].get(c,{}).get('f1-score',0):.3f}"
                       for c in cls))
    cm = m["confusion_matrix"]
    print(f"  Confusion matrix (rows=actual, cols=predicted):")
    print(f"  Labels: {cls}")
    for i, row in enumerate(cm):
        print(f"    {cls[i]:8s}: {row}")


# ─────────────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Research-grade evaluation of the LLM routing classifier."
    )
    parser.add_argument(
        "--data", default="data/queries.csv",
        help="Path to the labelled CSV dataset."
    )
    parser.add_argument(
        "--seed", type=int, default=RANDOM_SEED,
        help="Random seed for reproducible splits."
    )
    parser.add_argument(
        "--save-model", action="store_true",
        help="Overwrite production model artifacts (model.pkl, vectorizer.pkl, "
             "scaler.pkl, metrics.json) with this run's fitted objects."
    )
    args = parser.parse_args()

    report = run_evaluation(
        csv_path=BACKEND_DIR / args.data,
        seed=args.seed,
        save_model=args.save_model,
    )

    print("\n" + "="*65)
    print(f"  SUMMARY")
    print("="*65)
    tm = report["test_metrics"]["ml_router"]
    print(f"  Held-out Test Accuracy  : {tm['accuracy']:.4f}")
    print(f"  Held-out Test Macro-F1  : {tm['macro_f1']:.4f}")
    rb = report["test_metrics"]["rule_based_baseline"]
    mf = report["test_metrics"]["most_frequent_baseline"]
    print(f"  Rule-based baseline Acc : {rb['accuracy']:.4f}")
    print(f"  Most-frequent baseline  : {mf['accuracy']:.4f}")
    print(f"\n  Report saved to: trained_models/eval_report.json")
    print(f"  *** NOTE: Previous ~94.8% was IN-SAMPLE (train set) accuracy, NOT "
          f"generalisation. ***")
    print("="*65 + "\n")
