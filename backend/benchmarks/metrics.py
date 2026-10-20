import numpy as np
from typing import List, Dict, Any, Tuple, Optional
import scipy.stats as stats

def compute_percentile(values: List[float], p: float) -> float:
    """Compute p-th percentile safely."""
    if not values:
        return 0.0
    return float(np.percentile(values, p))


def paired_bootstrap_ci(
    baseline_values: List[float],
    policy_values: List[float],
    n_resamples: int = 1000,
    confidence_level: float = 0.95,
    random_seed: int = 42
) -> Dict[str, Any]:
    """
    Compute paired difference bootstrap confidence interval (Policy - Baseline).
    """
    if len(baseline_values) != len(policy_values) or len(baseline_values) == 0:
        return {"mean_diff": 0.0, "ci_lower": 0.0, "ci_upper": 0.0, "p_value": 1.0}

    diffs = np.array(policy_values) - np.array(baseline_values)
    mean_diff = float(np.mean(diffs))

    # Paired t-test
    if len(diffs) > 1 and np.std(diffs) > 1e-9:
        t_stat, p_val = stats.ttest_rel(policy_values, baseline_values)
    else:
        p_val = 1.0

    # Bootstrap
    rng = np.random.default_rng(random_seed)
    n = len(diffs)
    bootstrap_means = []
    for _ in range(n_resamples):
        sample = rng.choice(diffs, size=n, replace=True)
        bootstrap_means.append(np.mean(sample))

    alpha = (1.0 - confidence_level) / 2.0
    ci_lower = float(np.percentile(bootstrap_means, alpha * 100))
    ci_upper = float(np.percentile(bootstrap_means, (1.0 - alpha) * 100))

    return {
        "mean_diff": round(mean_diff, 6),
        "ci_lower": round(ci_lower, 6),
        "ci_upper": round(ci_upper, 6),
        "p_value": round(float(p_val), 6) if not np.isnan(p_val) else 1.0
    }


def aggregate_benchmark_results(results: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Aggregate raw prompt results into comprehensive research-grade metrics.
    Includes per-policy statistics, comparative savings, category breakdowns, and paired uncertainty.
    """
    if not results:
        return {"policies": {}, "comparisons": {}, "by_category": {}}

    # Group results by policy
    by_policy: Dict[str, List[Dict[str, Any]]] = {}
    for r in results:
        pol = r["policy"]
        by_policy.setdefault(pol, []).append(r)

    policy_summaries = {}
    paired_data: Dict[str, Dict[str, Dict[str, Any]]] = {}

    for pol, pol_items in by_policy.items():
        total = len(pol_items)
        successes = [r for r in pol_items if not r.get("error")]
        failures = [r for r in pol_items if r.get("error")]

        latencies = [r["latency"] for r in successes if r.get("latency") is not None]
        # Quality score accounting:
        # 1. Successful requests only (diagnostic of output quality on completed tasks)
        qualities_successful = [r["quality_score"] for r in successes if r.get("quality_score") is not None]
        # 2. Effective benchmark quality: failed requests (timeouts/rate-limits/errors) receive 0.0
        # to prevent survivorship bias and ensure failures penalize retention.
        qualities_all = [
            r["quality_score"] if (not r.get("error") and r.get("quality_score") is not None) else 0.0
            for r in pol_items
        ]
        costs = [r["cost"] for r in successes if r.get("cost") is not None]
        prompt_tokens = [r.get("prompt_tokens", 0) for r in successes]
        comp_tokens = [r.get("completion_tokens", 0) for r in successes]

        # Tier breakdown
        tiers = {}
        for r in pol_items:
            t = r.get("selected_model", "UNKNOWN")
            tiers[t] = tiers.get(t, 0) + 1

        tier_pcts = {t: round((cnt / total) * 100.0, 2) for t, cnt in tiers.items()}

        mean_lat = float(np.mean(latencies)) if latencies else 0.0
        med_lat = float(np.median(latencies)) if latencies else 0.0
        p95_lat = compute_percentile(latencies, 95) if latencies else 0.0

        mean_qual_successful = float(np.mean(qualities_successful)) if qualities_successful else 0.0
        effective_qual = float(np.mean(qualities_all)) if qualities_all else 0.0
        std_qual = float(np.std(qualities_all)) if qualities_all else 0.0

        total_cost = float(np.sum(costs)) if costs else 0.0
        mean_cost = float(np.mean(costs)) if costs else 0.0

        policy_summaries[pol] = {
            "total_requests": total,
            "successful_requests": len(successes),
            "failed_requests": len(failures),
            "failure_rate_pct": round((len(failures) / total) * 100.0, 2) if total else 0.0,
            "mean_latency_s": round(mean_lat, 4),
            "median_latency_s": round(med_lat, 4),
            "p95_latency_s": round(p95_lat, 4),
            "mean_quality_score": round(effective_qual, 3),
            "effective_quality_score": round(effective_qual, 3),
            "mean_quality_score_successful": round(mean_qual_successful, 3),
            "std_quality_score": round(std_qual, 3),
            "mean_cost_usd": round(mean_cost, 7),
            "total_cost_usd": round(total_cost, 7),
            "total_tokens": int(sum(prompt_tokens) + sum(comp_tokens)),
            "model_distribution_pct": tier_pcts
        }

        # Store paired map for diffs: prompt_id -> result
        paired_data[pol] = {r["prompt_id"]: r for r in pol_items}

    # Comparative analysis against ALWAYS_LARGE baseline
    comparisons = {}
    baseline_pol = "ALWAYS_LARGE"
    if baseline_pol in policy_summaries:
        base_sum = policy_summaries[baseline_pol]
        base_items = paired_data[baseline_pol]

        for pol in by_policy.keys():
            if pol == baseline_pol:
                continue

            pol_sum = policy_summaries[pol]
            pol_items = paired_data[pol]

            # Quality retention: compares effective quality so failures in either policy correctly impact retention
            qual_ret = (pol_sum["effective_quality_score"] / base_sum["effective_quality_score"] * 100.0) if base_sum["effective_quality_score"] > 0 else 0.0

            # Cost reduction
            cost_red = ((base_sum["total_cost_usd"] - pol_sum["total_cost_usd"]) / base_sum["total_cost_usd"] * 100.0) if base_sum["total_cost_usd"] > 0 else 0.0

            # Latency reduction
            lat_red = ((base_sum["mean_latency_s"] - pol_sum["mean_latency_s"]) / base_sum["mean_latency_s"] * 100.0) if base_sum["mean_latency_s"] > 0 else 0.0

            # Paired vectors across shared prompts
            shared_pids = sorted(list(set(base_items.keys()) & set(pol_items.keys())))
            base_lats = [base_items[pid]["latency"] for pid in shared_pids if base_items[pid].get("latency") is not None]
            pol_lats = [pol_items[pid]["latency"] for pid in shared_pids if pol_items[pid].get("latency") is not None]
            base_costs = [base_items[pid]["cost"] for pid in shared_pids if base_items[pid].get("cost") is not None]
            pol_costs = [pol_items[pid]["cost"] for pid in shared_pids if pol_items[pid].get("cost") is not None]
            # In paired quality comparisons, execution failures receive 0.0 to prevent survivorship bias
            base_quals = [base_items[pid]["quality_score"] if not base_items[pid].get("error") else 0.0 for pid in shared_pids]
            pol_quals = [pol_items[pid]["quality_score"] if not pol_items[pid].get("error") else 0.0 for pid in shared_pids]

            # Bootstrap CIs
            ci_lat = paired_bootstrap_ci(base_lats, pol_lats) if len(base_lats) == len(pol_lats) else {"mean_diff": 0.0, "ci_lower": 0.0, "ci_upper": 0.0, "p_value": 1.0}
            ci_cost = paired_bootstrap_ci(base_costs, pol_costs) if len(base_costs) == len(pol_costs) else {"mean_diff": 0.0, "ci_lower": 0.0, "ci_upper": 0.0, "p_value": 1.0}
            ci_qual = paired_bootstrap_ci(base_quals, pol_quals)

            comparisons[pol] = {
                "quality_retention_pct": round(qual_ret, 2),
                "cost_reduction_pct": round(cost_red, 2),
                "latency_reduction_pct": round(lat_red, 2),
                "paired_sample_size": len(shared_pids),
                "latency_diff_ci_95": ci_lat,
                "cost_diff_ci_95": ci_cost,
                "quality_diff_ci_95": ci_qual
            }

    # Breakdown by category
    categories = sorted(list({r["category"] for r in results}))
    by_category = {}
    for cat in categories:
        cat_results = [r for r in results if r["category"] == cat]
        cat_policies = {}
        for pol, pol_items in by_policy.items():
            cat_pol_items = [r for r in cat_results if r["policy"] == pol and not r.get("error")]
            if cat_pol_items:
                cat_policies[pol] = {
                    "count": len(cat_pol_items),
                    "mean_latency_s": round(float(np.mean([r["latency"] for r in cat_pol_items])), 4),
                    "mean_cost_usd": round(float(np.mean([r["cost"] for r in cat_pol_items])), 7),
                    "mean_quality_score": round(float(np.mean([r["quality_score"] for r in cat_pol_items])), 3),
                    "models_selected": {
                        t: [r["selected_model"] for r in cat_pol_items].count(t)
                        for t in set(r["selected_model"] for r in cat_pol_items)
                    }
                }
        by_category[cat] = cat_policies

    return {
        "policies": policy_summaries,
        "comparisons": comparisons,
        "by_category": by_category
    }
