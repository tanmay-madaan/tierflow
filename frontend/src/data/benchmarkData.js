// Canonical Benchmark v2 Experimental Dataset & Research Metadata (N = 200 Prompts)
// Verified in Phase 6E Cross-Policy Comparative Analysis

export const BENCHMARK_METADATA = {
  version: "v2.0",
  total_prompts: 200,
  categories_count: 7,
  sha256: "64e5b21f769cd15f132127335ad79b95362ba5f8a036ce931c76ad22dbe65a9c",
  date: "November 2026",
  models: {
    SMALL: "gemini-3.5-flash-lite",
    MEDIUM: "gemini-flash-latest",
    LARGE: "gemini-pro-latest"
  },
  pricing: {
    SMALL: { input_per_1m: 0.30, output_per_1m: 2.50 },
    MEDIUM: { input_per_1m: 0.75, output_per_1m: 3.75 },
    LARGE: { input_per_1m: 2.00, output_per_1m: 12.00 }
  }
};

export const FIVE_POLICY_DATA = {
  ALWAYS_SMALL: {
    id: "ALWAYS_SMALL",
    name: "Always-Small",
    shortName: "Small",
    tag: "Fixed Tier",
    modelId: "gemini-3.5-flash-lite",
    color: "#34D399",
    evidenceStatus: "EMPIRICAL_REAL",
    evidenceTitle: "Real API Benchmark Completed",
    evidenceDescription: "200 prompts executed via Google AI Studio API with T=0.0 and max_tokens=512. 199 successful requests, 1 infrastructure rate-limit failure (HTTP 429), 7 task failures (6 output-length syntax cutoffs, 1 instruction miss).",
    isMeasuredCost: true,
    actualCost: 0.087601,
    projectedCost: 0.087601,
    costVsLargePct: -79.43,
    costPremiumVsSmallPct: 0.0,
    qualityScore: 7.9291,
    successfulQualityScore: 7.9689,
    meanLatency: 1.4550,
    medianLatency: 1.3138,
    p95Latency: 2.5069,
    totalTokens: 43344,
    promptTokens: 9436,
    completionTokens: 33908,
    allocation: { SMALL: 200, MEDIUM: 0, LARGE: 0 },
    allocationPct: { SMALL: 100.0, MEDIUM: 0.0, LARGE: 0.0 },
    largeDependencyPct: 0.0,
    byCategory: {
      analytical_reasoning: { total: 30, SMALL: 30, MEDIUM: 0, LARGE: 0 },
      coding_debugging: { total: 30, SMALL: 30, MEDIUM: 0, LARGE: 0 },
      general_knowledge: { total: 30, SMALL: 30, MEDIUM: 0, LARGE: 0 },
      instruction_following: { total: 25, SMALL: 25, MEDIUM: 0, LARGE: 0 },
      mathematical_reasoning: { total: 30, SMALL: 30, MEDIUM: 0, LARGE: 0 },
      multi_step_reasoning: { total: 30, SMALL: 30, MEDIUM: 0, LARGE: 0 },
      summarization: { total: 25, SMALL: 25, MEDIUM: 0, LARGE: 0 }
    },
    byDifficulty: {
      easy: { total: 68, SMALL: 68, MEDIUM: 0, LARGE: 0 },
      medium: { total: 70, SMALL: 70, MEDIUM: 0, LARGE: 0 },
      hard: { total: 62, SMALL: 62, MEDIUM: 0, LARGE: 0 }
    }
  },

  ALWAYS_MEDIUM: {
    id: "ALWAYS_MEDIUM",
    name: "Always-Medium",
    shortName: "Medium",
    tag: "Fixed Tier",
    modelId: "gemini-flash-latest",
    color: "#F59E0B",
    evidenceStatus: "SOFTWARE_DEMO",
    evidenceTitle: "Software Integration Validation Only",
    evidenceDescription: "Validated in demo mode for software correctness and provider dispatch. No real 200-prompt model benchmark executed.",
    isMeasuredCost: false,
    actualCost: null,
    projectedCost: 0.134232,
    costVsLargePct: -68.47,
    costPremiumVsSmallPct: 53.23,
    qualityScore: null,
    successfulQualityScore: null,
    meanLatency: null,
    medianLatency: null,
    p95Latency: null,
    totalTokens: 43344,
    allocation: { SMALL: 0, MEDIUM: 200, LARGE: 0 },
    allocationPct: { SMALL: 0.0, MEDIUM: 100.0, LARGE: 0.0 },
    largeDependencyPct: 0.0,
    byCategory: {
      analytical_reasoning: { total: 30, SMALL: 0, MEDIUM: 30, LARGE: 0 },
      coding_debugging: { total: 30, SMALL: 0, MEDIUM: 30, LARGE: 0 },
      general_knowledge: { total: 30, SMALL: 0, MEDIUM: 30, LARGE: 0 },
      instruction_following: { total: 25, SMALL: 0, MEDIUM: 25, LARGE: 0 },
      mathematical_reasoning: { total: 30, SMALL: 0, MEDIUM: 30, LARGE: 0 },
      multi_step_reasoning: { total: 30, SMALL: 0, MEDIUM: 30, LARGE: 0 },
      summarization: { total: 25, SMALL: 0, MEDIUM: 25, LARGE: 0 }
    },
    byDifficulty: {
      easy: { total: 68, SMALL: 0, MEDIUM: 68, LARGE: 0 },
      medium: { total: 70, SMALL: 0, MEDIUM: 70, LARGE: 0 },
      hard: { total: 62, SMALL: 0, MEDIUM: 62, LARGE: 0 }
    }
  },

  ALWAYS_LARGE: {
    id: "ALWAYS_LARGE",
    name: "Always-Large",
    shortName: "Large",
    tag: "Baseline Ceiling",
    modelId: "gemini-pro-latest",
    color: "#818CF8",
    evidenceStatus: "SOFTWARE_DEMO",
    evidenceTitle: "Software Integration Validation Only",
    evidenceDescription: "Validated in demo mode. Pro models are allocated 0 RPD on Google AI Studio Free Tier (returning HTTP 429), preventing unbilled real-API benchmark execution.",
    isMeasuredCost: false,
    actualCost: null,
    projectedCost: 0.425768,
    costVsLargePct: 0.0,
    costPremiumVsSmallPct: 386.03,
    qualityScore: null,
    successfulQualityScore: null,
    meanLatency: null,
    medianLatency: null,
    p95Latency: null,
    totalTokens: 43344,
    allocation: { SMALL: 0, MEDIUM: 0, LARGE: 200 },
    allocationPct: { SMALL: 0.0, MEDIUM: 0.0, LARGE: 100.0 },
    largeDependencyPct: 100.0,
    byCategory: {
      analytical_reasoning: { total: 30, SMALL: 0, MEDIUM: 0, LARGE: 30 },
      coding_debugging: { total: 30, SMALL: 0, MEDIUM: 0, LARGE: 30 },
      general_knowledge: { total: 30, SMALL: 0, MEDIUM: 0, LARGE: 30 },
      instruction_following: { total: 25, SMALL: 0, MEDIUM: 0, LARGE: 25 },
      mathematical_reasoning: { total: 30, SMALL: 0, MEDIUM: 0, LARGE: 30 },
      multi_step_reasoning: { total: 30, SMALL: 0, MEDIUM: 0, LARGE: 30 },
      summarization: { total: 25, SMALL: 0, MEDIUM: 0, LARGE: 25 }
    },
    byDifficulty: {
      easy: { total: 68, SMALL: 0, MEDIUM: 0, LARGE: 68 },
      medium: { total: 70, SMALL: 0, MEDIUM: 0, LARGE: 70 },
      hard: { total: 62, SMALL: 0, MEDIUM: 0, LARGE: 62 }
    }
  },

  ADAPTIVE_ML: {
    id: "ADAPTIVE_ML",
    name: "TIERFLOW Adaptive ML",
    shortName: "Adaptive ML",
    tag: "ML Router",
    modelId: "Dynamic Multi-Tier",
    color: "#3B82F6",
    evidenceStatus: "SOFTWARE_DEMO",
    evidenceTitle: "Full 200-Prompt Routing Validation (Demo Trace)",
    evidenceDescription: "Full software trace of routing decisions on Benchmark v2. Exhibits 60% Large-tier dependency (120 prompts) because TF-IDF feature weights identify sentence complexity and reasoning keywords as requiring Pro models.",
    isMeasuredCost: false,
    actualCost: null,
    projectedCost: 0.256039,
    costVsLargePct: -39.86,
    costPremiumVsSmallPct: 192.28,
    qualityScore: null,
    successfulQualityScore: null,
    meanLatency: null,
    medianLatency: null,
    p95Latency: null,
    totalTokens: 43344,
    allocation: { SMALL: 32, MEDIUM: 48, LARGE: 120 },
    allocationPct: { SMALL: 16.0, MEDIUM: 24.0, LARGE: 60.0 },
    largeDependencyPct: 60.0,
    byCategory: {
      analytical_reasoning: { total: 30, SMALL: 0, MEDIUM: 1, LARGE: 29 },
      coding_debugging: { total: 30, SMALL: 2, MEDIUM: 28, LARGE: 0 },
      general_knowledge: { total: 30, SMALL: 24, MEDIUM: 6, LARGE: 0 },
      instruction_following: { total: 25, SMALL: 1, MEDIUM: 1, LARGE: 23 },
      mathematical_reasoning: { total: 30, SMALL: 5, MEDIUM: 10, LARGE: 15 },
      multi_step_reasoning: { total: 30, SMALL: 0, MEDIUM: 2, LARGE: 28 },
      summarization: { total: 25, SMALL: 0, MEDIUM: 0, LARGE: 25 }
    },
    byDifficulty: {
      easy: { total: 68, SMALL: 10, MEDIUM: 14, LARGE: 44 },
      medium: { total: 70, SMALL: 11, MEDIUM: 19, LARGE: 40 },
      hard: { total: 62, SMALL: 11, MEDIUM: 15, LARGE: 36 }
    }
  },

  RULE_BASED: {
    id: "RULE_BASED",
    name: "Heuristic Rule-Based",
    shortName: "Rule-Based",
    tag: "Heuristic",
    modelId: "Dynamic Multi-Tier",
    color: "#A0AEC0",
    evidenceStatus: "SOFTWARE_DEMO",
    evidenceTitle: "Full 200-Prompt Routing Validation (Demo Trace)",
    evidenceDescription: "Full software trace of routing decisions on Benchmark v2. Centers on Medium (51.0%) due to the linear complexity formula. Vulnerable to keyword brittleness (13 concise hard prompts routed to Small).",
    isMeasuredCost: false,
    actualCost: null,
    projectedCost: 0.175405,
    costVsLargePct: -58.80,
    costPremiumVsSmallPct: 100.23,
    qualityScore: null,
    successfulQualityScore: null,
    meanLatency: null,
    medianLatency: null,
    p95Latency: null,
    totalTokens: 43344,
    allocation: { SMALL: 53, MEDIUM: 102, LARGE: 45 },
    allocationPct: { SMALL: 26.5, MEDIUM: 51.0, LARGE: 22.5 },
    largeDependencyPct: 22.5,
    byCategory: {
      analytical_reasoning: { total: 30, SMALL: 4, MEDIUM: 22, LARGE: 4 },
      coding_debugging: { total: 30, SMALL: 9, MEDIUM: 18, LARGE: 3 },
      general_knowledge: { total: 30, SMALL: 24, MEDIUM: 6, LARGE: 0 },
      instruction_following: { total: 25, SMALL: 7, MEDIUM: 14, LARGE: 4 },
      mathematical_reasoning: { total: 30, SMALL: 7, MEDIUM: 22, LARGE: 1 },
      multi_step_reasoning: { total: 30, SMALL: 2, MEDIUM: 20, LARGE: 8 },
      summarization: { total: 25, SMALL: 0, MEDIUM: 0, LARGE: 25 }
    },
    byDifficulty: {
      easy: { total: 68, SMALL: 20, MEDIUM: 37, LARGE: 11 },
      medium: { total: 70, SMALL: 20, MEDIUM: 32, LARGE: 18 },
      hard: { total: 62, SMALL: 13, MEDIUM: 33, LARGE: 16 }
    }
  }
};

export const RESEARCH_LIMITATIONS = [
  {
    title: "Measured vs. Projected Cost Disparity",
    text: "Only ALWAYS_SMALL possesses empirically verified real API cost and latency telemetry ($0.087601 USD for 200 prompts). Costs for ALWAYS_MEDIUM, ALWAYS_LARGE, ADAPTIVE_ML, and RULE_BASED are mathematically modeled using verified token lengths from Phase 6B.3 combined with published Google AI Studio 2026 pricing rates."
  },
  {
    title: "Pro-Tier Free Quota Restrictions",
    text: "Google AI Studio allocates 0 RPD to Gemini Pro models on unbilled free-tier accounts, returning an immediate HTTP 429 quota exhaustion. Consequently, an empirical 200-prompt live run for ALWAYS_LARGE cannot be executed without enabling paid credit-card billing. Large-tier software dispatch was validated via local simulation."
  },
  {
    title: "Single-Turn Fixed Token Ceiling",
    text: "Benchmark v2 prompts were evaluated under a strict 512 completion token ceiling. While sufficient for 95% of queries, 6 hard coding tasks experienced output truncation resulting in syntax errors. Production routing should scale output token ceilings dynamically with the routed model tier."
  },
  {
    title: "Classifier Over-Routing on Descriptive Prompts",
    text: "ADAPTIVE_ML routes 64.7% of Easy prompts to LARGE because TF-IDF feature weights associate length and explanatory vocabulary ('analyze', 'explain', 'compare') with high complexity, reflecting training corpus vocabulary distributions rather than intrinsic difficulty."
  }
];
