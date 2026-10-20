import json
import hashlib
from pathlib import Path
from typing import List, Dict, Any, Optional
from config import BENCHMARK_DATA_DIR

BENCHMARK_VERSION = "1.0.0"
DEFAULT_BENCHMARK_FILE = BENCHMARK_DATA_DIR / "benchmark_v1.json"

REQUIRED_FIELDS = {"id", "category", "prompt", "reference_answer", "eval_type", "source", "license"}
VALID_CATEGORIES = {"factual", "reasoning", "mathematics", "coding", "summarization"}
VALID_EVAL_TYPES = {"factual_match", "reasoning_choice", "math_numeric", "code_eval", "summary_overlap"}

class BenchmarkDatasetError(Exception):
    """Raised when benchmark dataset fails validation."""
    pass


class BenchmarkDataset:
    """
    Separate, leakage-free benchmark dataset loader.
    Strictly isolated from classifier training dataset.
    """
    def __init__(self, filepath: Optional[Path] = None):
        self.filepath = filepath or DEFAULT_BENCHMARK_FILE
        self.items: List[Dict[str, Any]] = []
        self.manifest: Dict[str, Any] = {}
        self.load()

    def load(self) -> List[Dict[str, Any]]:
        """Load, validate, deduplicate, and compute manifest for benchmark dataset."""
        if not self.filepath.exists():
            raise BenchmarkDatasetError(f"Benchmark file not found at: {self.filepath}")

        with open(self.filepath, "r", encoding="utf-8") as f:
            content = f.read()

        file_hash = hashlib.sha256(content.encode("utf-8")).hexdigest()
        data = json.loads(content)

        if not isinstance(data, list):
            raise BenchmarkDatasetError("Benchmark data must be a JSON array of items.")

        seen_ids = set()
        seen_prompts = set()
        validated_items = []

        for idx, item in enumerate(data):
            # Check required fields
            missing = REQUIRED_FIELDS - set(item.keys())
            if missing:
                raise BenchmarkDatasetError(f"Item #{idx} missing required fields: {missing}")

            item_id = item["id"]
            prompt = item["prompt"].strip()
            cat = item["category"]
            eval_type = item["eval_type"]

            # Validate categories and evaluation types
            if cat not in VALID_CATEGORIES:
                raise BenchmarkDatasetError(f"Item {item_id} has invalid category: '{cat}'. Must be one of {VALID_CATEGORIES}")
            if eval_type not in VALID_EVAL_TYPES:
                raise BenchmarkDatasetError(f"Item {item_id} has invalid eval_type: '{eval_type}'. Must be one of {VALID_EVAL_TYPES}")

            # Deduplication
            if item_id in seen_ids:
                raise BenchmarkDatasetError(f"Duplicate item id found: '{item_id}'")
            if prompt in seen_prompts:
                # Deduplicate exact duplicate prompts
                continue

            seen_ids.add(item_id)
            seen_prompts.add(prompt)
            validated_items.append(item)

        self.items = validated_items

        # Build manifest
        category_counts = {}
        for item in self.items:
            c = item["category"]
            category_counts[c] = category_counts.get(c, 0) + 1

        self.manifest = {
            "version": BENCHMARK_VERSION,
            "filepath": str(self.filepath),
            "sha256": file_hash,
            "total_items": len(self.items),
            "category_counts": category_counts,
            "categories": sorted(list(category_counts.keys()))
        }
        return self.items

    def get_by_category(self, category: str) -> List[Dict[str, Any]]:
        """Filter benchmark items by category."""
        return [item for item in self.items if item["category"] == category]

    def check_leakage_with_training_data(self, training_csv_path: Path) -> List[str]:
        """
        Ensure 0% overlap between benchmark evaluation prompts and classifier training set.
        Returns any overlapping prompt strings (should always be empty).
        """
        import pandas as pd
        if not training_csv_path.exists():
            return []

        df_train = pd.read_csv(training_csv_path)
        train_prompts = set(df_train["query"].str.strip().str.lower().tolist())
        bench_prompts = set(item["prompt"].strip().lower() for item in self.items)

        overlap = list(train_prompts & bench_prompts)
        return overlap
