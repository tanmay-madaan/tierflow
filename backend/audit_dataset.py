"""Dataset audit script - run from backend/ directory."""
import pandas as pd
import sys
from pathlib import Path

SEP = "=" * 60

# ── File 1: the one actually loaded by train.py ──────────────────
print(SEP)
print("AUDIT: backend/data/queries.csv  (loaded by train.py)")
print(SEP)
df1 = pd.read_csv("data/queries.csv")
print(f"Rows            : {len(df1)}")
print(f"Columns         : {list(df1.columns)}")
print(f"Unique queries  : {df1['query'].nunique()}")
exact_dups1 = df1.duplicated(subset=["query"]).sum()
print(f"Exact duplicates: {exact_dups1}")
print(f"\nClass distribution:\n{df1['model'].value_counts().to_string()}")
print(f"\nCategory distribution:\n{df1['category'].value_counts().to_string()}")
print(f"\nComplexity distribution:\n{df1['complexity'].value_counts().to_string()}")

# Cross-check label consistency: category vs model
print("\nCategory x Model cross-tab (top rows):")
print(pd.crosstab(df1['category'], df1['model']).to_string())

# ── File 2: stale root-level file ───────────────────────────────
print()
print(SEP)
print("AUDIT: backend/queries.csv  (stale root-level file)")
print(SEP)
try:
    df2 = pd.read_csv("queries.csv")
    print(f"Rows            : {len(df2)}")
    print(f"Columns         : {list(df2.columns)}")
    print(f"Unique queries  : {df2['query'].nunique()}")
    exact_dups2 = df2.duplicated(subset=["query"]).sum()
    print(f"Exact duplicates: {exact_dups2}")
    print(f"\nClass distribution:\n{df2['model'].value_counts().to_string()}")

    # Overlap
    print()
    print(SEP)
    print("OVERLAP between the two files")
    print(SEP)
    set1 = set(df1["query"].tolist())
    set2 = set(df2["query"].tolist())
    overlap = set1 & set2
    print(f"Shared queries  : {len(overlap)}")

    if overlap:
        print("\nSample overlapping queries:")
        for q in list(overlap)[:5]:
            print(f"  - {q[:100]}")
except Exception as e:
    print(f"Error reading backend/queries.csv: {e}")

# ── Label quality check ──────────────────────────────────────────
print()
print(SEP)
print("LABEL QUALITY: same query, different labels?")
print(SEP)
dup_queries = df1[df1.duplicated(subset=["query"], keep=False)]
if len(dup_queries) > 0:
    conflicting = dup_queries.groupby("query")["model"].nunique()
    label_conflicts = conflicting[conflicting > 1]
    print(f"Queries with conflicting labels: {len(label_conflicts)}")
    if len(label_conflicts) > 0:
        print(label_conflicts.index.tolist()[:5])
else:
    print("No duplicate queries found in data/queries.csv — no label conflicts possible.")

# ── Near-duplicate detection (identical prefix) ──────────────────
print()
print(SEP)
print("NEAR-DUPLICATE DETECTION (first 50 chars match)")
print(SEP)
df1["prefix50"] = df1["query"].str.strip().str[:50].str.lower()
near_dups = df1[df1.duplicated(subset=["prefix50"], keep=False)]
print(f"Rows sharing same 50-char prefix: {len(near_dups)}")
if len(near_dups) > 0:
    nd_examples = near_dups.groupby("prefix50")["query"].apply(list).head(5)
    for pfx, qs in nd_examples.items():
        print(f"\n  Prefix: '{pfx}'")
        for q in qs[:3]:
            print(f"    → {q[:100]}")

print()
print("Audit complete.")
