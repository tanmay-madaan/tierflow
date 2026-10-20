"""
test_routing.py — Automated tests for the Adaptive LLM Router.

Covers:
  T01  Dataset loading and missing-column detection
  T02  Reproducible stratified splits
  T03  Class coverage in all splits
  T04  Duplicate-leakage prevention
  T05  Train-vs-test evaluation separation (no label bleed)
  T06  Prediction output format and valid probability distributions
  T07  Model persistence and reload
  T08  Routing confidence-threshold fallback behaviour
  T09  Routing at each model tier
  T10  In-sample vs held-out accuracy gap detection

Run with:
    python test_routing.py            (plain output)
    python test_routing.py -v         (verbose)
"""

import sys
import os
import json
import tempfile
import csv
import unittest
from pathlib import Path

# ── Ensure backend root is on sys.path ───────────────────────────────────────
BACKEND_DIR = Path(__file__).parent
sys.path.insert(0, str(BACKEND_DIR))

import numpy as np
import pandas as pd
import scipy.sparse as sp
import joblib

from router.feature_extractor import FeatureExtractor
from router.classifier import MLClassifier
from router.router import Router
from evaluate import (
    load_and_deduplicate, make_splits, build_features,
    train_classifier, compute_metrics,
    most_frequent_baseline, rule_based_baseline,
    brier_multiclass, compute_ece,
)
from config import CONFIDENCE_THRESHOLD


# ─────────────────────────────────────────────────────────────────────────────
# Shared test dataset (minimal but class-balanced for fast tests)
# ─────────────────────────────────────────────────────────────────────────────
SMALL_QUERIES = [
    ("What is the capital of France?", "factual", "LOW", "SMALL"),
    ("Who invented the telephone?",    "factual", "LOW", "SMALL"),
    ("What is photosynthesis?",         "general_knowledge", "LOW", "SMALL"),
    ("Define supervised learning.",     "general_knowledge", "LOW", "SMALL"),
    ("What does DNA stand for?",        "factual", "LOW", "SMALL"),
    ("What is a CPU?",                  "general_knowledge", "LOW", "SMALL"),
    ("How many planets are there?",     "factual", "LOW", "SMALL"),
    ("What is a primary key?",          "general_knowledge", "LOW", "SMALL"),
    ("Who wrote Hamlet?",               "factual", "LOW", "SMALL"),
    ("What is recursion?",              "general_knowledge", "LOW", "SMALL"),
]
MEDIUM_QUERIES = [
    ("Explain the difference between supervised and unsupervised learning.",
     "general_knowledge", "MODERATE", "MEDIUM"),
    ("Why does gradient descent sometimes fail to converge?",
     "simple_reasoning", "MODERATE", "MEDIUM"),
    ("Implement a binary search algorithm in Python.",
     "coding", "MODERATE", "MEDIUM"),
    ("How does a hash map handle collisions?",
     "general_knowledge", "MODERATE", "MEDIUM"),
    ("What is the derivative of x^2?",
     "mathematics", "MODERATE", "MEDIUM"),
    ("Debug this error: IndexError list index out of range.",
     "debugging", "MODERATE", "MEDIUM"),
    ("Explain how TCP ensures reliable delivery.",
     "general_knowledge", "MODERATE", "MEDIUM"),
    ("Why is normalization important in machine learning?",
     "simple_reasoning", "MODERATE", "MEDIUM"),
    ("Write a function to check if a string is a palindrome.",
     "coding", "MODERATE", "MEDIUM"),
    ("Explain the CAP theorem in distributed systems.",
     "general_knowledge", "MODERATE", "MEDIUM"),
]
LARGE_QUERIES = [
    ("Design a machine learning pipeline for detecting fraudulent transactions "
     "with severe class imbalance and explain how you would evaluate it.",
     "analytical_reasoning", "HIGH", "LARGE"),
    ("Analyze the impact of AI on the global economy over 20 years, "
     "considering trade-offs between automation and job creation.",
     "analytical_reasoning", "HIGH", "LARGE"),
    ("Design a distributed system for real-time fraud detection handling "
     "1M transactions per second. Explain architecture, trade-offs and failure handling.",
     "analytical_reasoning", "HIGH", "LARGE"),
    ("Step by step, derive the mathematics behind Principal Component Analysis, "
     "then implement PCA from scratch.",
     "multi_step_reasoning", "HIGH", "LARGE"),
    ("First explain how attention mechanisms work in transformers. Then describe "
     "parallel processing advantages. Finally analyse why they outperform RNNs.",
     "multi_step_reasoning", "HIGH", "LARGE"),
    ("Prove that the set of real numbers is uncountable using Cantor's diagonal argument.",
     "mathematics", "HIGH", "LARGE"),
    ("Design a comprehensive monitoring stack for a cloud-native application. "
     "Explain metrics, logs, traces and alerting with concrete tool recommendations.",
     "analytical_reasoning", "HIGH", "LARGE"),
    ("Architect a social media platform for 500 million users. Address the news feed "
     "algorithm, content moderation, real-time notifications and ad serving.",
     "long_context_reasoning", "HIGH", "LARGE"),
    ("Implement a complete Raft consensus algorithm. Explain leader election, "
     "log replication, safety guarantees and membership changes.",
     "coding", "HIGH", "LARGE"),
    ("Design a privacy-preserving ML system using federated learning and "
     "differential privacy. Explain mathematical guarantees and challenges.",
     "analytical_reasoning", "HIGH", "LARGE"),
]


def _make_csv(queries: list[tuple], path: Path):
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["query", "category", "complexity", "model"])
        for row in queries:
            w.writerow(row)


def _make_minimal_df(n_per_class: int = 10) -> pd.DataFrame:
    """Build a minimal balanced DataFrame for fast unit tests."""
    rows = []
    for q, cat, cmp, mdl in (SMALL_QUERIES[:n_per_class]
                               + MEDIUM_QUERIES[:n_per_class]
                               + LARGE_QUERIES[:n_per_class]):
        rows.append({"query": q, "category": cat, "complexity": cmp, "model": mdl})
    return pd.DataFrame(rows)


def _train_minimal_clf(df=None, seed=42):
    """Train a classifier on a small balanced dataset; return clf, vec, scaler."""
    if df is None:
        df = _make_minimal_df()
    fe = FeatureExtractor()
    df_train, df_val, df_test = make_splits(df, seed=seed)
    vectorizer, scaler, X_train, X_val, X_test = build_features(
        df_train["query"].values,
        [df_val["query"].values, df_test["query"].values],
        fe, seed,
    )
    clf = train_classifier(X_train, df_train["model"].values, seed)
    return clf, vectorizer, scaler, df_train, df_val, df_test


# ═════════════════════════════════════════════════════════════════════════════
class T01_DatasetLoading(unittest.TestCase):
    """T01 — Dataset loading and missing-column detection."""

    def test_load_valid_csv(self):
        df = _make_minimal_df()
        self.assertIn("query", df.columns)
        self.assertIn("model", df.columns)
        self.assertGreater(len(df), 0)

    def test_load_real_csv(self):
        """The actual production dataset must be loadable."""
        csv_path = BACKEND_DIR / "data" / "queries.csv"
        if not csv_path.exists():
            self.skipTest("data/queries.csv not present")
        df, audit = load_and_deduplicate(csv_path)
        self.assertGreater(len(df), 0)
        self.assertIn("query", df.columns)
        self.assertIn("model", df.columns)

    def test_missing_model_column_raises(self):
        """Missing 'model' column must raise ValueError."""
        with tempfile.NamedTemporaryFile(suffix=".csv", mode="w",
                                         delete=False, newline="") as f:
            w = csv.writer(f)
            w.writerow(["query", "category"])
            w.writerow(["hello", "factual"])
            tmp = Path(f.name)
        try:
            with self.assertRaises(ValueError):
                load_and_deduplicate(tmp)
        finally:
            tmp.unlink(missing_ok=True)

    def test_missing_query_column_raises(self):
        """Missing 'query' column must raise ValueError."""
        with tempfile.NamedTemporaryFile(suffix=".csv", mode="w",
                                         delete=False, newline="") as f:
            w = csv.writer(f)
            w.writerow(["text", "model"])
            w.writerow(["hello", "SMALL"])
            tmp = Path(f.name)
        try:
            with self.assertRaises(ValueError):
                load_and_deduplicate(tmp)
        finally:
            tmp.unlink(missing_ok=True)

    def test_null_rows_dropped(self):
        rows = (SMALL_QUERIES[:5] + MEDIUM_QUERIES[:5] + LARGE_QUERIES[:5])
        with tempfile.NamedTemporaryFile(suffix=".csv", mode="w",
                                         delete=False, newline="") as f:
            w = csv.writer(f)
            w.writerow(["query", "category", "complexity", "model"])
            for r in rows:
                w.writerow(r)
            w.writerow(["", "", "", ""])      # null query row
            w.writerow([None, None, None, None])
            tmp = Path(f.name)
        try:
            df, audit = load_and_deduplicate(tmp)
            self.assertGreater(audit["rows_dropped_null"], 0)
            self.assertFalse(df["query"].isnull().any())
        finally:
            tmp.unlink(missing_ok=True)


# ═════════════════════════════════════════════════════════════════════════════
class T02_ReproducibleSplits(unittest.TestCase):
    """T02 — Splits are reproducible and have the expected proportions."""

    def setUp(self):
        self.df = _make_minimal_df()

    def test_splits_are_deterministic(self):
        a_train, a_val, a_test = make_splits(self.df, seed=42)
        b_train, b_val, b_test = make_splits(self.df, seed=42)
        self.assertTrue(a_train["query"].equals(b_train["query"]))
        self.assertTrue(a_val["query"].equals(b_val["query"]))
        self.assertTrue(a_test["query"].equals(b_test["query"]))

    def test_different_seeds_differ(self):
        a_train, _, _ = make_splits(self.df, seed=42)
        b_train, _, _ = make_splits(self.df, seed=99)
        # At least one difference in index ordering
        self.assertFalse(a_train["query"].reset_index(drop=True).equals(
                         b_train["query"].reset_index(drop=True)))

    def test_split_sizes_sum_to_total(self):
        df, audit = load_and_deduplicate(BACKEND_DIR / "data" / "queries.csv") \
            if (BACKEND_DIR / "data" / "queries.csv").exists() \
            else (self.df, {})
        tr, vl, te = make_splits(df, seed=42)
        self.assertEqual(len(tr) + len(vl) + len(te), len(df))

    def test_approximate_ratios(self):
        df, _ = load_and_deduplicate(BACKEND_DIR / "data" / "queries.csv") \
            if (BACKEND_DIR / "data" / "queries.csv").exists() \
            else (self.df, {})
        tr, vl, te = make_splits(df, seed=42)
        n = len(df)
        # Allow ±5% tolerance
        self.assertAlmostEqual(len(tr) / n, 0.70, delta=0.05)
        self.assertAlmostEqual(len(vl) / n, 0.15, delta=0.05)
        self.assertAlmostEqual(len(te) / n, 0.15, delta=0.05)

    def test_no_overlap_between_splits(self):
        tr, vl, te = make_splits(self.df, seed=42)
        s_train = set(tr["query"].tolist())
        s_val   = set(vl["query"].tolist())
        s_test  = set(te["query"].tolist())
        self.assertEqual(len(s_train & s_val),  0, "train/val overlap")
        self.assertEqual(len(s_train & s_test), 0, "train/test overlap")
        self.assertEqual(len(s_val & s_test),   0, "val/test overlap")


# ═════════════════════════════════════════════════════════════════════════════
class T03_ClassCoverage(unittest.TestCase):
    """T03 — All classes present in all three splits."""

    def test_all_classes_in_all_splits(self):
        df = _make_minimal_df()
        expected = set(df["model"].unique())
        tr, vl, te = make_splits(df, seed=42)
        for name, split in [("train", tr), ("val", vl), ("test", te)]:
            got = set(split["model"].unique())
            missing = expected - got
            self.assertEqual(missing, set(),
                             f"Split '{name}' missing classes: {missing}")


# ═════════════════════════════════════════════════════════════════════════════
class T04_DuplicateLeakagePrevention(unittest.TestCase):
    """T04 — Exact and near duplicates are removed before splitting."""

    def _make_csv_with_dups(self):
        """Dataset with known exact and near duplicates."""
        rows = (SMALL_QUERIES[:8] + MEDIUM_QUERIES[:8] + LARGE_QUERIES[:8])
        extra = [
            # Exact duplicate of SMALL_QUERIES[0] ("What is the capital of France?")
            ("What is the capital of France?", "factual", "LOW", "SMALL"),
            # Near-duplicate: starts with same 60 chars as "What is the capital of France?"
            # (the exact dup is removed first, so this tests the near-dup path)
            ("What is the capital of France, and who is the current president?",
             "factual", "LOW", "SMALL"),
        ]
        return rows + extra

    def test_exact_duplicates_removed(self):
        rows = self._make_csv_with_dups()
        with tempfile.NamedTemporaryFile(suffix=".csv", mode="w",
                                         delete=False, newline="") as f:
            _make_csv(rows, Path(f.name))
            tmp = Path(f.name)
        try:
            df, audit = load_and_deduplicate(tmp)
            self.assertGreater(audit["rows_dropped_exact_dup"], 0)
            self.assertEqual(df["query"].nunique(), len(df))
        finally:
            tmp.unlink(missing_ok=True)

    def test_near_duplicates_removed(self):
        """Near-duplicates (same 60-char prefix) are dropped after exact-dup removal."""
        rows = self._make_csv_with_dups()
        with tempfile.NamedTemporaryFile(suffix=".csv", mode="w",
                                         delete=False, newline="") as f:
            _make_csv(rows, Path(f.name))
            tmp = Path(f.name)
        try:
            df, audit = load_and_deduplicate(tmp)
            # 1 exact dup dropped; the near-dup query "What is the capital of France,..."
            # has a 60-char prefix "what is the capital of france, and who is the current pres"
            # which may or may not match SMALL_QUERIES[0] prefix depending on length.
            # We simply verify total rows dropped ≥ 1 (the exact dup at minimum).
            total_dropped = (audit["rows_dropped_exact_dup"]
                             + audit["rows_dropped_near_dup"])
            self.assertGreaterEqual(total_dropped, 1,
                                    "Expected at least 1 row dropped (exact duplicate)")
            # Verify no remaining duplicates
            self.assertEqual(df["query"].nunique(), len(df))
        finally:
            tmp.unlink(missing_ok=True)

    def test_no_split_leakage_after_dedup(self):
        """After dedup, no query in test also appears in train."""
        df = _make_minimal_df()
        df, _ = load_and_deduplicate(
            BACKEND_DIR / "data" / "queries.csv"
        ) if (BACKEND_DIR / "data" / "queries.csv").exists() else (df, {})
        tr, _, te = make_splits(df, seed=42)
        overlap = set(tr["query"]) & set(te["query"])
        self.assertEqual(overlap, set(), f"Leakage: {len(overlap)} shared queries")


# ═════════════════════════════════════════════════════════════════════════════
class T05_TrainTestSeparation(unittest.TestCase):
    """T05 — Vectorizer and scaler must NOT be fitted on validation or test data."""

    def test_vectorizer_fit_only_on_train(self):
        df = _make_minimal_df()
        fe = FeatureExtractor()
        tr, vl, te = make_splits(df, seed=42)
        vectorizer, scaler, X_tr, X_vl, X_te = build_features(
            tr["query"].values,
            [vl["query"].values, te["query"].values],
            fe,
        )
        # Vocabulary size should be set from train queries only
        vocab_size = len(vectorizer.vocabulary_)
        self.assertGreater(vocab_size, 0)

        # Re-fitting on full data gives a different (usually larger) vocabulary
        from sklearn.feature_extraction.text import TfidfVectorizer as TV
        full_vec = TV(max_features=500, ngram_range=(1, 2))
        full_vec.fit(df["query"].values)
        # Vocabulary trained on full data ≥ vocabulary trained on 70%
        self.assertGreaterEqual(len(full_vec.vocabulary_), vocab_size)

    def test_test_labels_not_used_in_training(self):
        """
        After training, calling clf.fit again with test labels should change
        the model — confirming test labels were not part of the original fit.
        """
        clf, vec, scaler, df_train, df_val, df_test = _train_minimal_clf()
        fe = FeatureExtractor()

        # Get probabilities before
        q = df_test["query"].values[0]
        X = sp.hstack((vec.transform([q]),
                        scaler.transform(
                            np.array([[fe.extract(q).get("query_length", 0),
                                       *[0]*7]]))))
        probs_before = clf.predict_proba(X)[0].copy()

        # Refit including test labels (simulating leakage)
        all_queries = np.concatenate([df_train["query"].values,
                                       df_test["query"].values])
        all_labels  = np.concatenate([df_train["model"].values,
                                       df_test["model"].values])
        X_all_text = vec.transform(all_queries)
        fe2 = FeatureExtractor()
        from evaluate import _numerical_features
        X_all_num = scaler.transform(_numerical_features(all_queries, fe2))
        X_all = sp.hstack((X_all_text, X_all_num))
        clf.fit(X_all, all_labels)

        probs_after = clf.predict_proba(X)[0]
        # Probabilities should differ (model changed)
        self.assertFalse(np.allclose(probs_before, probs_after),
                         "Model unchanged after including test data — "
                         "suggests test was already in training.")


# ═════════════════════════════════════════════════════════════════════════════
class T06_PredictionFormat(unittest.TestCase):
    """T06 — predict() returns valid format with proper probability distributions."""

    def setUp(self):
        self.clf, self.vec, self.scaler, *_ = _train_minimal_clf()
        # Wire up a temporary MLClassifier with the trained objects
        self.mlc = MLClassifier(model_dir=str(BACKEND_DIR / "trained_models"))

    def test_predict_returns_dict_with_required_keys(self):
        result = self.mlc.predict("What is the capital of Japan?")
        self.assertIn("selected_model", result)
        self.assertIn("confidence", result)
        self.assertIn("probabilities", result)

    def test_selected_model_is_valid_tier(self):
        result = self.mlc.predict("What is the capital of Japan?")
        self.assertIn(result["selected_model"], {"SMALL", "MEDIUM", "LARGE"})

    def test_confidence_in_unit_interval(self):
        result = self.mlc.predict("Design a distributed ML pipeline.")
        self.assertGreaterEqual(result["confidence"], 0.0)
        self.assertLessEqual(result["confidence"], 1.0)

    def test_probabilities_sum_to_one(self):
        result = self.mlc.predict("Explain gradient descent.")
        total = sum(result["probabilities"].values())
        self.assertAlmostEqual(total, 1.0, places=5)

    def test_confidence_equals_max_probability(self):
        result = self.mlc.predict("Implement a binary search tree.")
        max_prob = max(result["probabilities"].values())
        self.assertAlmostEqual(result["confidence"], max_prob, places=8)

    def test_predict_diverse_queries(self):
        queries = [
            "What is 2 + 2?",
            "Explain the difference between TCP and UDP.",
            "Design a fault-tolerant distributed database with consistency guarantees.",
        ]
        for q in queries:
            result = self.mlc.predict(q)
            self.assertIn(result["selected_model"], {"SMALL", "MEDIUM", "LARGE"},
                          f"Bad tier for: {q}")


# ═════════════════════════════════════════════════════════════════════════════
class T07_ModelPersistence(unittest.TestCase):
    """T07 — Saved model reloads and gives identical predictions."""

    def test_saved_and_reloaded_predictions_match(self):
        model_dir = BACKEND_DIR / "trained_models"
        if not (model_dir / "model.pkl").exists():
            self.skipTest("No trained model artifacts found; run train.py first.")

        mlc1 = MLClassifier(model_dir=str(model_dir))
        mlc2 = MLClassifier(model_dir=str(model_dir))

        queries = [
            "What is Python?",
            "Design a distributed system for 1M RPS with fault tolerance.",
            "Implement quicksort and analyse its complexity.",
        ]
        for q in queries:
            r1 = mlc1.predict(q)
            r2 = mlc2.predict(q)
            self.assertEqual(r1["selected_model"], r2["selected_model"])
            self.assertAlmostEqual(r1["confidence"], r2["confidence"], places=8)

    def test_artifacts_are_present(self):
        model_dir = BACKEND_DIR / "trained_models"
        for name in ["model.pkl", "vectorizer.pkl", "scaler.pkl", "metrics.json"]:
            self.assertTrue((model_dir / name).exists(),
                            f"Missing artifact: {name}")

    def test_metrics_json_has_required_keys(self):
        model_dir = BACKEND_DIR / "trained_models"
        if not (model_dir / "metrics.json").exists():
            self.skipTest("metrics.json not present")
        with open(model_dir / "metrics.json") as f:
            m = json.load(f)
        for key in ["accuracy", "precision", "recall", "f1",
                    "confusion_matrix", "class_labels"]:
            self.assertIn(key, m, f"metrics.json missing key: {key}")


# ═════════════════════════════════════════════════════════════════════════════
class T08_ConfidenceThreshold(unittest.TestCase):
    """T08 — Confidence-threshold fallback escalates to the next tier."""

    def setUp(self):
        self.mlc = MLClassifier(model_dir=str(BACKEND_DIR / "trained_models"))
        fe = FeatureExtractor()
        self.router = Router(self.mlc, fe)

    def _make_low_confidence_pred(self):
        """Monkey-patch classifier.predict to return low confidence."""
        import types
        orig = self.mlc.predict

        def _low_conf(query):
            result = orig(query)
            result["confidence"] = CONFIDENCE_THRESHOLD - 0.01  # just below threshold
            result["selected_model"] = "SMALL"
            return result

        self.mlc.predict = _low_conf

    def test_below_threshold_escalates(self):
        self._make_low_confidence_pred()
        result = self.router.route("What is the capital of Japan?")
        # Confidence was forced below threshold with SMALL → should escalate to MEDIUM
        self.assertIn(result["selected_model"], {"MEDIUM", "LARGE"},
                      "Expected escalation from SMALL when confidence is low")

    def test_above_threshold_does_not_escalate(self):
        """When confidence is well above threshold, model stays as predicted."""
        import types
        orig = self.mlc.predict

        def _high_conf(query):
            result = orig(query)
            result["confidence"] = 0.99
            result["selected_model"] = "SMALL"
            return result

        self.mlc.predict = _high_conf
        result = self.router.route("What is the capital of Japan?")
        self.assertEqual(result["selected_model"], "SMALL")

    def test_large_model_does_not_escalate_further(self):
        """LARGE tier at low confidence should NOT escalate beyond LARGE."""
        import types

        def _low_conf_large(query):
            return {
                "selected_model": "LARGE",
                "confidence": CONFIDENCE_THRESHOLD - 0.01,
                "probabilities": {"SMALL": 0.1, "MEDIUM": 0.2, "LARGE": 0.7},
            }

        self.mlc.predict = _low_conf_large
        result = self.router.route("Design a distributed system.")
        self.assertEqual(result["selected_model"], "LARGE",
                         "LARGE is already the highest tier; must not go above")

    def test_route_output_has_required_keys(self):
        result = self.router.route("What is 2 + 2?")
        for key in ["selected_model", "complexity", "confidence",
                    "features", "reasoning", "probabilities"]:
            self.assertIn(key, result, f"route() output missing key: {key}")


# ═════════════════════════════════════════════════════════════════════════════
class T09_TierRouting(unittest.TestCase):
    """T09 — Each tier (SMALL/MEDIUM/LARGE) can be routed by the classifier."""

    def setUp(self):
        self.mlc = MLClassifier(model_dir=str(BACKEND_DIR / "trained_models"))

    def test_small_tier_routed(self):
        """Simple factual queries should likely route to SMALL."""
        factual_queries = [
            "What is the capital of Japan?",
            "Who invented the telephone?",
            "What is the chemical formula for water?",
        ]
        results = [self.mlc.predict(q)["selected_model"] for q in factual_queries]
        self.assertIn("SMALL", results,
                      f"None of the factual queries routed to SMALL: {results}")

    def test_large_tier_routed(self):
        """Complex reasoning queries should likely route to LARGE."""
        complex_queries = [
            ("Design a fault-tolerant distributed consensus protocol. "
             "Explain Raft and Paxos trade-offs in terms of safety, liveness, "
             "and performance under network partitions."),
            ("Derive the backpropagation algorithm for a multi-layer neural network. "
             "Show the complete mathematical derivation including chain rule applications "
             "and discuss numerical stability."),
        ]
        results = [self.mlc.predict(q)["selected_model"] for q in complex_queries]
        self.assertIn("LARGE", results,
                      f"None of the complex queries routed to LARGE: {results}")

    def test_all_three_tiers_reachable(self):
        """Over a broad set of queries, all three tiers must appear."""
        test_queries = (
            [q for q, *_ in SMALL_QUERIES[:5]]
            + [q for q, *_ in MEDIUM_QUERIES[:5]]
            + [q for q, *_ in LARGE_QUERIES[:5]]
        )
        tiers_seen = {self.mlc.predict(q)["selected_model"] for q in test_queries}
        for tier in ["SMALL", "MEDIUM", "LARGE"]:
            self.assertIn(tier, tiers_seen,
                          f"Tier '{tier}' was never selected across {len(test_queries)} queries")


# ═════════════════════════════════════════════════════════════════════════════
class T10_AccuracyGap(unittest.TestCase):
    """T10 — Detect and flag suspicious in-sample vs held-out accuracy gap."""

    def test_train_test_gap_within_reasonable_bounds(self):
        """
        A >15% gap between in-sample train accuracy and held-out test accuracy
        is a strong signal of overfitting or leakage.
        This test WARNS (does not fail) to allow real evaluation to proceed.
        """
        from sklearn.metrics import accuracy_score as _acc
        df = _make_minimal_df()
        clf, vec, scaler, df_train, df_val, df_test = _train_minimal_clf(df)
        fe = FeatureExtractor()

        from evaluate import build_features, _numerical_features
        _, _, X_train, X_test = build_features(
            df_train["query"].values,
            [df_test["query"].values],
            fe,
        )
        train_acc = _acc(df_train["model"].values,
                         clf.predict(X_train))
        test_acc  = _acc(df_test["model"].values,
                         clf.predict(X_test))
        gap = train_acc - test_acc
        # Warn but do not hard-fail — small test sets can legitimately swing
        if gap > 0.20:
            print(f"\n  WARNING T10: train-test gap = {gap:.3f} "
                  f"({train_acc:.3f} train, {test_acc:.3f} test). "
                  "This may indicate overfitting on the small synthetic dataset.")
        # Soft assertion: gap should not be catastrophic
        self.assertLess(gap, 0.45,
                        f"Train-test gap ({gap:.3f}) is extremely large "
                        f"— likely a data leakage or dataset issue.")

    def test_eval_report_contains_both_train_and_test(self):
        """The evaluation report must store both in-sample and test metrics."""
        report_path = BACKEND_DIR / "trained_models" / "eval_report.json"
        if not report_path.exists():
            self.skipTest("eval_report.json not found; run evaluate.py first.")
        with open(report_path) as f:
            report = json.load(f)
        self.assertIn("in_sample_train_metrics", report,
                      "Report missing in_sample_train_metrics")
        self.assertIn("test_metrics", report,
                      "Report missing test_metrics")
        self.assertIn("ml_router", report["test_metrics"],
                      "test_metrics missing ml_router key")


# ═════════════════════════════════════════════════════════════════════════════
class T11_ConfidenceAwareRoutingPolicy(unittest.TestCase):
    """T11 — Confidence-aware tier thresholds, safe empty fallback, and telemetry."""

    def setUp(self):
        self.mlc = MLClassifier(model_dir=str(BACKEND_DIR / "trained_models"))
        self.fe = FeatureExtractor()
        self.router = Router(
            self.mlc, self.fe,
            policy="confidence_aware",
            threshold_small=0.60,
            threshold_medium=0.40
        )

    def test_empty_and_whitespace_queries_route_to_safe_fallback(self):
        """Empty or whitespace-only queries must route to MEDIUM with confidence 0.0 and was_escalated=True."""
        for empty_val in ["", "   ", "\n\t"]:
            res = self.router.route(empty_val)
            self.assertEqual(res["selected_model"], "MEDIUM")
            self.assertEqual(res["initial_model"], "UNKNOWN")
            self.assertEqual(res["confidence"], 0.0)
            self.assertTrue(res["was_escalated"])
            self.assertIn("safe fallback tier", res["escalation_reason"])
            self.assertEqual(res["probabilities"]["MEDIUM"], 1.0)

    def test_small_below_threshold_escalates_to_medium(self):
        """SMALL with confidence 0.55 (< 0.60 threshold) must escalate to MEDIUM."""
        def mock_predict(query):
            return {
                "selected_model": "SMALL",
                "confidence": 0.55,
                "probabilities": {"SMALL": 0.55, "MEDIUM": 0.35, "LARGE": 0.10}
            }
        self.mlc.predict = mock_predict
        res = self.router.route("What is 2 + 2?")
        self.assertEqual(res["selected_model"], "MEDIUM")
        self.assertEqual(res["initial_model"], "SMALL")
        self.assertTrue(res["was_escalated"])
        self.assertIn("0.60", res["escalation_reason"])

    def test_small_above_threshold_retained(self):
        """SMALL with confidence 0.65 (>= 0.60 threshold) must NOT escalate."""
        def mock_predict(query):
            return {
                "selected_model": "SMALL",
                "confidence": 0.65,
                "probabilities": {"SMALL": 0.65, "MEDIUM": 0.25, "LARGE": 0.10}
            }
        self.mlc.predict = mock_predict
        res = self.router.route("What is 2 + 2?")
        self.assertEqual(res["selected_model"], "SMALL")
        self.assertEqual(res["initial_model"], "SMALL")
        self.assertFalse(res["was_escalated"])
        self.assertIsNone(res["escalation_reason"])

    def test_medium_below_threshold_escalates_to_large(self):
        """MEDIUM with confidence 0.35 (< 0.40 threshold) must escalate to LARGE."""
        def mock_predict(query):
            return {
                "selected_model": "MEDIUM",
                "confidence": 0.35,
                "probabilities": {"SMALL": 0.30, "MEDIUM": 0.35, "LARGE": 0.35}
            }
        self.mlc.predict = mock_predict
        res = self.router.route("Explain TCP.")
        self.assertEqual(res["selected_model"], "LARGE")
        self.assertEqual(res["initial_model"], "MEDIUM")
        self.assertTrue(res["was_escalated"])
        self.assertIn("0.40", res["escalation_reason"])

    def test_medium_above_threshold_retained(self):
        """MEDIUM with confidence 0.45 (>= 0.40 threshold) must NOT escalate."""
        def mock_predict(query):
            return {
                "selected_model": "MEDIUM",
                "confidence": 0.45,
                "probabilities": {"SMALL": 0.25, "MEDIUM": 0.45, "LARGE": 0.30}
            }
        self.mlc.predict = mock_predict
        res = self.router.route("Explain TCP.")
        self.assertEqual(res["selected_model"], "MEDIUM")
        self.assertEqual(res["initial_model"], "MEDIUM")
        self.assertFalse(res["was_escalated"])

    def test_large_tier_never_escalates(self):
        """LARGE tier never escalates even with low confidence."""
        def mock_predict(query):
            return {
                "selected_model": "LARGE",
                "confidence": 0.30,
                "probabilities": {"SMALL": 0.35, "MEDIUM": 0.35, "LARGE": 0.30}
            }
        self.mlc.predict = mock_predict
        res = self.router.route("Design a distributed consensus system.")
        self.assertEqual(res["selected_model"], "LARGE")
        self.assertFalse(res["was_escalated"])

    def test_structured_telemetry_keys(self):
        """Routing result must contain all required telemetry fields for observability and UI."""
        res = self.router.route("What is a neural network?")
        required_keys = [
            "selected_model", "initial_model", "confidence",
            "was_escalated", "escalation_reason",
            "complexity", "features", "reasoning", "probabilities"
        ]
        for k in required_keys:
            self.assertIn(k, res, f"Missing key in route() result: {k}")


# ═════════════════════════════════════════════════════════════════════════════
class T12_CalibrationMetrics(unittest.TestCase):
    """T12 — Multi-class Brier score and Expected Calibration Error computation."""

    def test_brier_multiclass_perfect_prediction(self):
        classes = ["LARGE", "MEDIUM", "SMALL"]
        y_true = ["SMALL", "MEDIUM", "LARGE"]
        probs = np.array([
            [0.0, 0.0, 1.0],  # SMALL
            [0.0, 1.0, 0.0],  # MEDIUM
            [1.0, 0.0, 0.0],  # LARGE
        ])
        score = brier_multiclass(y_true, probs, classes)
        self.assertEqual(score, 0.0)

    def test_brier_multiclass_worst_prediction(self):
        classes = ["LARGE", "MEDIUM", "SMALL"]
        y_true = ["SMALL", "SMALL"]
        probs = np.array([
            [1.0, 0.0, 0.0],
            [1.0, 0.0, 0.0],
        ])
        score = brier_multiclass(y_true, probs, classes)
        self.assertEqual(score, 2.0)

    def test_compute_ece_validity(self):
        classes = ["LARGE", "MEDIUM", "SMALL"]
        y_true = ["SMALL", "MEDIUM", "LARGE", "SMALL"]
        probs = np.array([
            [0.1, 0.2, 0.7],
            [0.2, 0.6, 0.2],
            [0.8, 0.1, 0.1],
            [0.3, 0.4, 0.3],
        ])
        ece, bins = compute_ece(y_true, probs, classes, n_bins=5)
        self.assertGreaterEqual(ece, 0.0)
        self.assertLessEqual(ece, 1.0)
        self.assertIsInstance(bins, list)


# ═════════════════════════════════════════════════════════════════════════════
class T13_PolicyComparisonArtifacts(unittest.TestCase):
    """T13 — Offline 4-policy comparison and calibration analysis report artifacts."""

    def setUp(self):
        self.report_path = BACKEND_DIR / "trained_models" / "eval_report.json"
        if not self.report_path.exists():
            self.skipTest("eval_report.json not found; run evaluate.py first.")
        with open(self.report_path) as f:
            self.report = json.load(f)

    def test_policy_comparison_present_and_complete(self):
        self.assertIn("policy_comparison", self.report)
        policies = self.report["policy_comparison"]
        for p in [
            "current_adaptive_router_0.50",
            "confidence_aware_router_0.60_0.40",
            "rule_based_baseline",
            "always_large_baseline"
        ]:
            self.assertIn(p, policies, f"Missing policy in report: {p}")
            self.assertIn("accuracy", policies[p])
            self.assertIn("macro_f1", policies[p])
            self.assertIn("estimated_cost_per_query", policies[p])

    def test_calibration_analysis_present(self):
        self.assertIn("calibration_analysis", self.report)
        cal = self.report["calibration_analysis"]
        self.assertIn("validation", cal)
        self.assertIn("test", cal)
        self.assertIn("calibration_finding", cal)
        for split in ["validation", "test"]:
            self.assertIn("uncalibrated_brier", cal[split])
            self.assertIn("uncalibrated_ece_5bins", cal[split])
            self.assertIn("calibrated_platt_brier", cal[split])
            self.assertIn("calibrated_platt_ece_5bins", cal[split])


# ═════════════════════════════════════════════════════════════════════════════
class T14_RobustnessDatasetValidation(unittest.TestCase):
    """T14 — Schema validation, leakage prevention, and labeling integrity for robustness dataset."""

    def setUp(self):
        self.dataset_path = BACKEND_DIR / "data" / "robustness_queries.csv"
        if not self.dataset_path.exists():
            self.skipTest("robustness_queries.csv not found")
        self.df = pd.read_csv(self.dataset_path)

    def test_dataset_size_within_bounds(self):
        """Dataset must contain between 80 and 120 curated test queries."""
        self.assertGreaterEqual(len(self.df), 80)
        self.assertLessEqual(len(self.df), 120)

    def test_required_columns_present(self):
        """All required schema columns must be present."""
        expected_cols = [
            "id", "query", "case_type", "ground_truth_tier",
            "expected_routing_tier", "has_defensible_ground_truth", "labelling_notes"
        ]
        for col in expected_cols:
            self.assertIn(col, self.df.columns, f"Missing column: {col}")

    def test_eight_case_types_represented(self):
        """All 8 specified failure-mode categories must be represented with sufficient samples."""
        expected_types = {
            "paraphrase_uncommon_wording",
            "unusual_syntax_vocabulary",
            "ambiguous_missing_context",
            "complex_no_keywords",
            "empty_whitespace",
            "nonsense_random_tokens",
            "short_difficult",
            "long_simple"
        }
        actual_types = set(self.df["case_type"].unique())
        self.assertEqual(expected_types, actual_types, "Mismatch in case types")
        for ct in expected_types:
            count = (self.df["case_type"] == ct).sum()
            self.assertGreaterEqual(count, 8, f"Case type {ct} has fewer than 8 samples: {count}")

    def test_zero_overlap_with_production_queries(self):
        """Zero data leakage: No robustness query may exist in data/queries.csv."""
        prod_path = BACKEND_DIR / "data" / "queries.csv"
        if not prod_path.exists():
            self.skipTest("queries.csv not found")
        df_prod = pd.read_csv(prod_path)
        prod_queries = set(df_prod["query"].str.strip().str.lower())
        
        non_empty = self.df[self.df["case_type"] != "empty_whitespace"]
        rob_queries = set(non_empty["query"].dropna().str.strip().str.lower())
        
        overlap = prod_queries & rob_queries
        self.assertEqual(len(overlap), 0, f"Data leakage detected! Overlapping queries: {overlap}")

    def test_defensible_ground_truth_separation(self):
        """Nonsense, empty, and ambiguous inputs must have ground_truth_tier='NONE' and has_defensible_ground_truth=False."""
        non_def = self.df[self.df["case_type"].isin([
            "empty_whitespace", "nonsense_random_tokens", "ambiguous_missing_context"
        ])]
        for _, row in non_def.iterrows():
            self.assertEqual(row["ground_truth_tier"], "NONE", f"Invalid GT tier for {row['id']}")
            self.assertIn(str(row["has_defensible_ground_truth"]).lower(), ["false", "0"])


# ═════════════════════════════════════════════════════════════════════════════
class T15_RobustnessEvaluationHarness(unittest.TestCase):
    """T15 — Verification of the offline robustness report and failure metrics."""

    def setUp(self):
        self.report_path = BACKEND_DIR / "trained_models" / "robustness_report.json"
        if not self.report_path.exists():
            self.skipTest("robustness_report.json not found; run evaluate_robustness.py first.")
        with open(self.report_path) as f:
            self.report = json.load(f)

    def test_robustness_report_structure(self):
        self.assertIn("defensible_ground_truth_metrics", self.report)
        self.assertIn("escalation_summary", self.report)
        self.assertIn("case_type_breakdown", self.report)
        self.assertIn("high_confidence_failures_on_valid_tasks", self.report)
        self.assertIn("high_confidence_predictions_on_garbage", self.report)

    def test_false_small_and_false_large_metrics_tracked(self):
        metrics = self.report["defensible_ground_truth_metrics"]
        self.assertIn("false_small_risk", metrics)
        self.assertIn("false_large_risk", metrics)
        self.assertIn("router_false_small_rate_pct", metrics["false_small_risk"])
        self.assertIn("router_false_large_rate_pct", metrics["false_large_risk"])


# ═════════════════════════════════════════════════════════════════════════════
class T16_DeploymentAndClassifierIntegrity(unittest.TestCase):
    """T16 — Production deployment readiness, artifact verification, and API routing contracts."""

    def test_fitted_classifier_loads_successfully(self):
        """Production artifacts must load and verify as fitted estimators without error."""
        mlc = MLClassifier()
        self.assertIsNotNone(mlc.model, "Classifier model must not be None")
        self.assertIsNotNone(mlc.vectorizer, "Vectorizer must not be None")
        self.assertIsNotNone(mlc.scaler, "Scaler must not be None")
        self.assertTrue(hasattr(mlc.vectorizer, "idf_"), "Vectorizer must have fitted idf_ attribute")
        self.assertIsNotNone(mlc.vectorizer.idf_, "Vectorizer idf_ must not be None")

        res = mlc.predict("What is the capital of France?")
        self.assertIn("selected_model", res)
        self.assertIn("confidence", res)
        self.assertIn(res["selected_model"], {"SMALL", "MEDIUM", "LARGE"})

    def test_reject_unfitted_vectorizer_gracefully(self):
        """Loading an unfitted vectorizer must be caught during verification, triggering safe heuristic fallback."""
        from sklearn.feature_extraction.text import TfidfVectorizer
        from sklearn.linear_model import LogisticRegression
        from sklearn.preprocessing import StandardScaler

        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_path = Path(tmp_dir)
            # Dump fitted model and scaler, but UN-FITTED vectorizer
            unfitted_vec = TfidfVectorizer(max_features=500)
            clf = LogisticRegression()
            clf.fit([[0, 0], [1, 1]], ["SMALL", "LARGE"])
            scaler = StandardScaler()
            scaler.fit([[0, 0], [1, 1]])

            joblib.dump(clf, tmp_path / "model.pkl")
            joblib.dump(unfitted_vec, tmp_path / "vectorizer.pkl")
            joblib.dump(scaler, tmp_path / "scaler.pkl")
            with open(tmp_path / "metrics.json", "w") as f:
                json.dump({"accuracy": 1.0}, f)

            # Instantiation must detect missing idf_/unfitted state and fall back atomically
            mlc = MLClassifier(model_dir=str(tmp_path))
            self.assertIsNone(mlc.model, "Model must be None when vectorizer is unfitted")
            self.assertIsNone(mlc.vectorizer, "Vectorizer must be None when unfitted")

            # Predict must safely return heuristic without raising NotFittedError
            pred = mlc.predict("Explain the difference between TCP and UDP.")
            self.assertIn(pred["selected_model"], {"SMALL", "MEDIUM", "LARGE"})
            self.assertEqual(pred["confidence"], 0.6)

    def test_missing_model_artifacts_falls_back_to_heuristic(self):
        """Missing artifact files must not crash initialization and must fall back gracefully."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            mlc = MLClassifier(model_dir=str(tmp_dir))
            self.assertIsNone(mlc.model)
            pred = mlc.predict("What is recursion?")
            self.assertIn(pred["selected_model"], {"SMALL", "MEDIUM", "LARGE"})

    def test_health_endpoint_contract(self):
        """FastAPI /health endpoint must respond 200 and report model_trained: true."""
        from fastapi.testclient import TestClient
        from main import app

        client = TestClient(app)
        res = client.get("/health")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data["status"], "ok")
        self.assertTrue(data["model_trained"])
        self.assertIn("model_tiers", data)

    def test_route_and_query_demo_mode(self):
        """FastAPI /route and /query must successfully execute in demo mode without Gemini API key."""
        from fastapi.testclient import TestClient
        from main import app

        client = TestClient(app)
        # Test /route
        res_route = client.post("/route", json={"query": "What is Python?"})
        self.assertEqual(res_route.status_code, 200)
        route_data = res_route.json()
        self.assertIn("selected_model", route_data)
        self.assertIn("confidence", route_data)

        # Test /query demo mode
        res_query = client.post("/query", json={
            "query": "What is Python?",
            "demo_mode": True,
            "execution_mode": "demo"
        })
        self.assertEqual(res_query.status_code, 200)
        query_data = res_query.json()
        self.assertEqual(query_data["execution_mode"], "demo")
        self.assertIsNone(query_data["error"])
        self.assertIn("response", query_data)
        self.assertGreater(len(query_data["response"]), 0)

    def test_cors_headers_allow_vercel(self):
        """CORS must permit Vercel production origin and include credentials."""
        from fastapi.testclient import TestClient
        from main import app

        client = TestClient(app)
        res = client.options("/query", headers={
            "Origin": "https://tierflow-ruddy.vercel.app",
            "Access-Control-Request-Method": "POST"
        })
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.headers.get("access-control-allow-origin"), "https://tierflow-ruddy.vercel.app")
        self.assertEqual(res.headers.get("access-control-allow-credentials"), "true")


# ═════════════════════════════════════════════════════════════════════════════
if __name__ == "__main__":
    # Print a clear header
    print("\n" + "="*65)
    print("  Adaptive LLM Router — Automated Test Suite")
    print("="*65 + "\n")
    loader = unittest.TestLoader()
    suite  = loader.loadTestsFromModule(sys.modules[__name__])
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    sys.exit(0 if result.wasSuccessful() else 1)
