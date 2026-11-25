import React, { useState, useEffect } from 'react';
import { api } from '../services/api';
import { StatCard } from '../components/StatCard';
import { ModelBadge } from '../components/ModelBadge';
import { ExecutionModeBadge } from '../components/ExecutionModeBadge';
import { CustomTooltip } from '../components/CustomTooltip';
import { 
  BENCHMARK_METADATA, 
  FIVE_POLICY_DATA, 
  RESEARCH_LIMITATIONS 
} from '../data/benchmarkData';
import { 
  Target, 
  CheckCircle2, 
  TrendingUp, 
  FlaskConical, 
  Play, 
  Info, 
  AlertTriangle, 
  ArrowRight, 
  ShieldCheck, 
  Cpu, 
  RefreshCw, 
  BarChart2,
  Clock, 
  DollarSign, 
  Layers, 
  Activity,
  FileText,
  ChevronDown,
  ChevronUp,
  AlertCircle
} from 'lucide-react';
import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip as RechartsTooltip,
  ResponsiveContainer, Cell, Legend
} from 'recharts';

const CONFUSION_MATRICES = {
  baseline: {
    id: 'baseline',
    label: 'Baseline Model (87.8% Acc, N = 49)',
    modelName: 'Original Baseline (commit b9d49f5)',
    accuracy: '87.8%',
    f1: '88.9%',
    precision: '88.7%',
    recall: '89.8%',
    correctCount: '43 / 49',
    matrix: [
      [10, 0, 0],
      [1, 17, 1],
      [0, 4, 16]
    ],
    note: 'Held-out test split (N = 49, seed = 42). 100% recall on LARGE tasks (10/10), 89.5% on MEDIUM (17/19), 80.0% on SMALL (16/20).'
  },
  phase5c: {
    id: 'phase5c',
    label: 'Phase 5C Model (85.7% Acc, N = 49)',
    modelName: 'Phase 5C Calibrated Artifact',
    accuracy: '85.7%',
    f1: '86.5%',
    precision: '87.1%',
    recall: '86.5%',
    correctCount: '42 / 49',
    matrix: [
      [9, 1, 0],
      [1, 17, 1],
      [0, 4, 16]
    ],
    note: 'Held-out test split (N = 49, seed = 42) after confidence calibration. 1 Large task shifted to Medium.'
  }
};

export default function ResearchResults() {
  const [cMetrics, setCMetrics] = useState(null);
  const [loading, setLoading] = useState(true);
  const [smokeTestLoading, setSmokeTestLoading] = useState(false);
  const [smokeTestResult, setSmokeTestResult] = useState(null);
  const [smokeTestError, setSmokeTestError] = useState(null);
  const [activeAnalysisTab, setActiveAnalysisTab] = useState('category'); // 'category' or 'difficulty'
  const [showMethodology, setShowMethodology] = useState(true);
  const [selectedMatrixId, setSelectedMatrixId] = useState('baseline');

  const activeMatrixConfig = CONFUSION_MATRICES[selectedMatrixId];

  useEffect(() => {
    fetchClassifierMetrics();
  }, []);

  const fetchClassifierMetrics = async () => {
    setLoading(true);
    try {
      const cm = await api.getClassifierMetrics();
      if (cm) setCMetrics(cm);
    } catch (err) {
      console.warn("Classifier metrics fetch failed:", err);
    } finally {
      setLoading(false);
    }
  };

  const handleRunSmokeTest = async () => {
    setSmokeTestLoading(true);
    setSmokeTestError(null);
    try {
      const res = await api.runBenchmark('demo', 5);
      if (res && !res.status) {
        setSmokeTestResult(res);
      } else if (res?.message) {
        setSmokeTestError(res.message);
      }
    } catch (err) {
      console.error("Smoke test failed:", err);
      setSmokeTestError(err.message || 'Demo smoke test execution failed.');
    } finally {
      setSmokeTestLoading(false);
    }
  };

  const policiesList = Object.values(FIVE_POLICY_DATA);

  // Stacked Bar Data for 5-Policy Allocation
  const allocationChartData = policiesList.map(pol => ({
    name: pol.shortName,
    fullName: pol.name,
    small: pol.allocationPct.SMALL,
    medium: pol.allocationPct.MEDIUM,
    large: pol.allocationPct.LARGE,
  }));

  // Cost Comparison Data (Actual vs Projected)
  const costChartData = policiesList.map(pol => ({
    name: pol.shortName,
    fullName: pol.name,
    cost: pol.projectedCost,
    isMeasured: pol.isMeasuredCost,
    color: pol.color
  }));

  // Category Breakdown Data for ADAPTIVE_ML vs RULE_BASED
  const categories = [
    { key: 'analytical_reasoning', label: 'Analytical' },
    { key: 'coding_debugging', label: 'Coding' },
    { key: 'general_knowledge', label: 'Gen. Knowledge' },
    { key: 'instruction_following', label: 'Instruction' },
    { key: 'mathematical_reasoning', label: 'Math' },
    { key: 'multi_step_reasoning', label: 'Multi-Step' },
    { key: 'summarization', label: 'Summarize' },
  ];

  const categoryComparisonData = categories.map(({ key, label }) => {
    const mlLargePct = Math.round(FIVE_POLICY_DATA.ADAPTIVE_ML.byCategory[key].LARGE / FIVE_POLICY_DATA.ADAPTIVE_ML.byCategory[key].total * 100);
    const ruleLargePct = Math.round(FIVE_POLICY_DATA.RULE_BASED.byCategory[key].LARGE / FIVE_POLICY_DATA.RULE_BASED.byCategory[key].total * 100);
    return {
      category: label,
      adaptiveMlLarge: mlLargePct,
      ruleBasedLarge: ruleLargePct
    };
  });

  const difficultyComparisonData = [
    {
      level: 'Easy (N=68)',
      adaptiveMl: Math.round(FIVE_POLICY_DATA.ADAPTIVE_ML.byDifficulty.easy.LARGE / 68 * 100),
      ruleBased: Math.round(FIVE_POLICY_DATA.RULE_BASED.byDifficulty.easy.LARGE / 68 * 100),
    },
    {
      level: 'Medium (N=70)',
      adaptiveMl: Math.round(FIVE_POLICY_DATA.ADAPTIVE_ML.byDifficulty.medium.LARGE / 70 * 100),
      ruleBased: Math.round(FIVE_POLICY_DATA.RULE_BASED.byDifficulty.medium.LARGE / 70 * 100),
    },
    {
      level: 'Hard (N=62)',
      adaptiveMl: Math.round(FIVE_POLICY_DATA.ADAPTIVE_ML.byDifficulty.hard.LARGE / 62 * 100),
      ruleBased: Math.round(FIVE_POLICY_DATA.RULE_BASED.byDifficulty.hard.LARGE / 62 * 100),
    }
  ];

  return (
    <div className="p-4 sm:p-6 lg:p-8 max-w-7xl mx-auto space-y-8 pb-24">
      {/* ── Page Header ────────────────────────────────────────────── */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-4 border-b border-[#263548]">
        <div>
          <div className="flex items-center gap-2.5 mb-1">
            <h1 className="text-xl font-bold tracking-tight text-[#F1F5F9]">
              TIERFLOW <span className="text-[#3B82F6] font-medium">Research &amp; Benchmark</span>
            </h1>
            <span className="text-[10px] font-mono uppercase px-2 py-0.5 rounded bg-[#192536] text-[#A0AEC0] border border-[#263548]">
              Benchmark v2 (N = 200)
            </span>
          </div>
          <p className="text-xs text-[#A0AEC0] font-sans">
            Comprehensive evaluation of held-out router accuracy, empirical Gemini Small-tier performance, and cross-policy routing trade-offs.
          </p>
        </div>

        {/* Demo Smoke Test Trigger */}
        <div className="flex items-center gap-2 shrink-0">
          <button
            onClick={handleRunSmokeTest}
            disabled={smokeTestLoading}
            className="flex items-center gap-1.5 px-3 py-1.5 rounded-md text-xs font-mono font-medium text-white bg-[#192536] hover:bg-[#263548] border border-[#263548] disabled:opacity-40 transition-colors"
            title="Runs an ephemeral 5-prompt demo simulation across the 5 policies to verify backend execution pathways"
          >
            {smokeTestLoading ? <RefreshCw className="w-3.5 h-3.5 animate-spin text-[#3B82F6]" /> : <Play className="w-3.5 h-3.5 text-[#34D399]" />}
            <span>{smokeTestLoading ? 'Executing Smoke Test...' : 'Run Demo Smoke Test (5 Items)'}</span>
          </button>
        </div>
      </div>

      {/* Smoke Test Feedback Notification */}
      {smokeTestResult && (
        <div className="bg-[#141E2A] border border-[#34D399]/40 rounded-md p-3.5 text-xs font-mono flex items-center justify-between gap-3">
          <div className="flex items-center gap-2 text-[#34D399]">
            <CheckCircle2 className="w-4 h-4 shrink-0" />
            <span>Smoke test run <code className="text-[#F1F5F9]">{smokeTestResult.run_id}</code> completed successfully in simulated demo mode.</span>
          </div>
          <button 
            onClick={() => setSmokeTestResult(null)}
            className="text-[#718096] hover:text-[#F1F5F9] text-[10px]"
          >
            Dismiss
          </button>
        </div>
      )}

      {smokeTestError && (
        <div className="bg-red-950/30 border border-red-800/60 rounded-md p-3.5 text-xs font-mono text-red-300 flex items-center gap-2">
          <AlertTriangle className="w-4 h-4 text-red-400 shrink-0" />
          <span>{smokeTestError}</span>
        </div>
      )}

      {/* ── Section 1: ML Classifier Generalization ────────────────── */}
      <section className="space-y-4">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 border-b border-[#263548] pb-2">
          <div className="flex items-center gap-2">
            <Target className="w-4 h-4 text-[#3B82F6]" />
            <h2 className="text-sm font-semibold text-[#F1F5F9] uppercase tracking-wider font-mono">
              1. Router ML Classifier — Original Baseline Held-Out Evaluation (N = 49)
            </h2>
          </div>
          <span className="text-[11px] font-mono text-[#A0AEC0]">
            Original Baseline • Stratified 70/15/15 Split • Seed 42 • No Data Leakage
          </span>
        </div>

        {/* Provenance Audit Note */}
        <div className="bg-[#101722] border border-[#263548] rounded-md p-3.5 text-xs font-mono space-y-1.5">
          <div className="flex items-center gap-2 text-[#3B82F6] font-semibold text-[11px] uppercase tracking-wider">
            <Info className="w-3.5 h-3.5" />
            <span>Model Provenance &amp; Evaluation Audit</span>
          </div>
          <p className="text-[#A0AEC0] font-sans text-xs leading-relaxed">
            The <strong className="text-[#F1F5F9] font-mono">87.8% Accuracy</strong> (43/49 correct) and <strong className="text-[#F1F5F9] font-mono">88.9% Macro-F1</strong> metrics represent the original TF-IDF + Logistic Regression baseline model evaluated on the held-out test split (<code className="text-[#F1F5F9]">queries.csv</code>, N = 49, Seed 42). A subsequent Phase 5C calibration run on the same split yielded <strong className="text-[#F1F5F9] font-mono">85.7% Accuracy</strong> (42/49 correct, 86.5% Macro-F1) when 1 sample shifted from Large to Medium. Both evaluations are strictly held-out test metrics and must not be confused with training set scores.
          </p>
        </div>

        <div className="grid grid-cols-2 lg:grid-cols-4 gap-3.5">
          <StatCard
            title="Baseline Test Accuracy"
            value="87.8%"
            subtitle="Held-Out Test (43/49 correct)"
            badge="Baseline N=49"
          />
          <StatCard
            title="Macro Precision"
            value="88.7%"
            subtitle="Unweighted class average"
            badge="Macro"
          />
          <StatCard
            title="Macro Recall"
            value="89.8%"
            subtitle="Class coverage (LARGE: 100%)"
            badge="Macro"
          />
          <StatCard
            title="Macro F1-Score"
            value="88.9%"
            subtitle="Harmonic mean of P &amp; R"
            badge="Macro"
          />
        </div>

        {/* Confusion Matrix Table */}
        <div className="bg-[#141E2A] border border-[#263548] rounded-md p-5 space-y-4">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 border-b border-[#263548] pb-3">
            <div>
              <div className="flex items-center gap-2 mb-1">
                <h3 className="text-xs font-mono font-semibold uppercase tracking-wider text-[#F1F5F9]">
                  Multiclass Confusion Matrix
                </h3>
                <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-[#101722] text-[#34D399] border border-[#263548]">
                  {activeMatrixConfig.correctCount} Correct ({activeMatrixConfig.accuracy})
                </span>
              </div>
              <p className="text-[11px] text-[#A0AEC0] font-sans">
                {activeMatrixConfig.note}
              </p>
            </div>

            {/* Matrix Model Switcher */}
            <div className="flex items-center gap-1.5 bg-[#101722] p-1 rounded border border-[#263548] shrink-0">
              <button
                type="button"
                onClick={() => setSelectedMatrixId('baseline')}
                className={`px-2.5 py-1 rounded text-[11px] font-mono transition-colors ${
                  selectedMatrixId === 'baseline'
                    ? 'bg-[#192536] text-[#F1F5F9] font-medium border border-[#263548]'
                    : 'text-[#A0AEC0] hover:text-[#F1F5F9]'
                }`}
              >
                Baseline (87.8% Acc)
              </button>
              <button
                type="button"
                onClick={() => setSelectedMatrixId('phase5c')}
                className={`px-2.5 py-1 rounded text-[11px] font-mono transition-colors ${
                  selectedMatrixId === 'phase5c'
                    ? 'bg-[#192536] text-[#F1F5F9] font-medium border border-[#263548]'
                    : 'text-[#A0AEC0] hover:text-[#F1F5F9]'
                }`}
              >
                Phase 5C (85.7% Acc)
              </button>
            </div>
          </div>

          <div className="overflow-x-auto">
            <table className="w-full max-w-lg text-xs font-mono border-collapse">
              <thead>
                <tr>
                  <th className="p-2.5 text-[#A0AEC0] text-left w-36 border-b border-[#263548]">
                    Actual \ Predicted
                  </th>
                  {['LARGE', 'MEDIUM', 'SMALL'].map((label) => (
                    <th key={label} className="p-2.5 text-center font-semibold text-[#F1F5F9] border-b border-[#263548] uppercase">
                      {label}
                    </th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {activeMatrixConfig.matrix.map((row, i) => {
                  const labels = ['LARGE', 'MEDIUM', 'SMALL'];
                  return (
                    <tr key={i} className="border-b border-[#263548]/50">
                      <th className="p-2.5 font-semibold text-[#F1F5F9] text-left border-r border-[#263548] uppercase">
                        {labels[i]}
                      </th>
                      {row.map((cell, j) => {
                        const isCorrect = i === j;
                        return (
                          <td
                            key={j}
                            className={`p-3 text-center font-mono border border-[#263548] font-semibold text-sm tabular-nums ${
                              isCorrect 
                                ? 'bg-[#34D399]/15 text-[#34D399]' 
                                : cell > 0 
                                ? 'bg-red-950/40 text-red-300' 
                                : 'text-[#718096]'
                            }`}
                          >
                            {cell}
                          </td>
                        );
                      })}
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        </div>
      </section>

      {/* ── Section 2: Five-Policy Benchmark Comparison ────────────── */}
      <section className="space-y-4">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 border-b border-[#263548] pb-2">
          <div className="flex items-center gap-2">
            <FlaskConical className="w-4 h-4 text-[#34D399]" />
            <h2 className="text-sm font-semibold text-[#F1F5F9] uppercase tracking-wider font-mono">
              2. Five-Policy Routing Comparison (Benchmark v2, N = 200 Prompts)
            </h2>
          </div>
          <span className="text-[11px] font-mono text-[#A0AEC0]">
            7 Cognitive Categories • Stratified Difficulties
          </span>
        </div>

        {/* Master Comparison Table */}
        <div className="bg-[#141E2A] border border-[#263548] rounded-md overflow-hidden">
          <div className="overflow-x-auto">
            <table className="w-full text-xs font-mono border-collapse min-w-[800px]">
              <thead className="bg-[#101722] text-[#A0AEC0] border-b border-[#263548] text-[10px] uppercase tracking-wider text-left">
                <tr>
                  <th className="p-3">Routing Policy</th>
                  <th className="p-3">Model Mapped</th>
                  <th className="p-3 text-center">Tier Allocation (S / M / L)</th>
                  <th className="p-3 text-right">Large Dep.</th>
                  <th className="p-3 text-right">Cost (200 Queries)</th>
                  <th className="p-3 text-right">Cost vs Large</th>
                  <th className="p-3 text-right">Quality Score</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-[#263548]">
                {policiesList.map((pol) => {
                  const isSmallEmpirical = pol.id === 'ALWAYS_SMALL';
                  const isAdaptive = pol.id === 'ADAPTIVE_ML';
                  const isBaseline = pol.id === 'ALWAYS_LARGE';

                  return (
                    <tr 
                      key={pol.id} 
                      className={`hover:bg-[#192536]/70 transition-colors ${
                        isSmallEmpirical ? 'bg-[#34D399]/5' : isAdaptive ? 'bg-[#3B82F6]/5' : ''
                      }`}
                    >
                      {/* Policy */}
                      <td className="p-3">
                        <div className="flex flex-col gap-1">
                          <div className="flex items-center gap-2">
                            <span className="font-semibold" style={{ color: pol.color }}>
                              {pol.name}
                            </span>
                            <span className="text-[9px] px-1.5 py-0.2 rounded border bg-[#101722] text-[#A0AEC0] border-[#263548]">
                              {pol.tag}
                            </span>
                          </div>
                          <span className={`text-[9px] font-mono w-fit px-1.5 py-0.2 rounded border ${
                            isSmallEmpirical 
                              ? 'bg-[#34D399]/15 text-[#34D399] border-[#34D399]/40 font-semibold'
                              : isAdaptive 
                              ? 'bg-[#3B82F6]/15 text-[#3B82F6] border-[#3B82F6]/40'
                              : pol.id === 'RULE_BASED'
                              ? 'bg-[#A0AEC0]/15 text-[#A0AEC0] border-[#A0AEC0]/40'
                              : pol.id === 'ALWAYS_MEDIUM'
                              ? 'bg-[#F59E0B]/15 text-[#F59E0B] border-[#F59E0B]/40'
                              : 'bg-[#818CF8]/15 text-[#818CF8] border-[#818CF8]/40'
                          }`}>
                            {isSmallEmpirical ? 'EMPIRICAL REAL (N=200)' : pol.id === 'ALWAYS_MEDIUM' ? 'SOFTWARE DEMO (N=200)' : pol.id === 'ALWAYS_LARGE' ? 'PROJECTED BASELINE' : pol.id === 'ADAPTIVE_ML' ? 'ROUTING TRACE (N=200)' : 'HEURISTIC TRACE (N=200)'}
                          </span>
                        </div>
                      </td>

                      {/* Model Mapped */}
                      <td className="p-3 text-[#A0AEC0] text-[11px]">
                        {pol.modelId}
                      </td>

                      {/* Tier Allocation */}
                      <td className="p-3 text-center tabular-nums">
                        <span className="text-[#34D399] font-medium">{pol.allocationPct.SMALL}%</span>
                        <span className="text-[#718096] mx-1">/</span>
                        <span className="text-[#F59E0B] font-medium">{pol.allocationPct.MEDIUM}%</span>
                        <span className="text-[#718096] mx-1">/</span>
                        <span className="text-[#818CF8] font-medium">{pol.allocationPct.LARGE}%</span>
                      </td>

                      {/* Large Dependency */}
                      <td className="p-3 text-right tabular-nums font-semibold text-[#818CF8]">
                        {pol.largeDependencyPct.toFixed(1)}%
                      </td>

                      {/* Cost */}
                      <td className="p-3 text-right tabular-nums">
                        {pol.isMeasuredCost ? (
                          <div className="flex flex-col items-end">
                            <span className="text-[#34D399] font-semibold">${pol.actualCost.toFixed(6)}</span>
                            <span className="text-[9px] text-[#34D399] font-bold uppercase">Measured Real</span>
                          </div>
                        ) : (
                          <div className="flex flex-col items-end">
                            <span className="text-[#F1F5F9]">${pol.projectedCost.toFixed(6)}</span>
                            <span className="text-[9px] text-[#A0AEC0] uppercase">Projected Rate</span>
                          </div>
                        )}
                      </td>

                      {/* Cost vs Large */}
                      <td className="p-3 text-right tabular-nums font-semibold">
                        {isBaseline ? (
                          <span className="text-[#718096]">Baseline</span>
                        ) : (
                          <span className="text-[#34D399]">
                            {pol.costVsLargePct.toFixed(1)}%
                          </span>
                        )}
                      </td>

                      {/* Quality Score */}
                      <td className="p-3 text-right tabular-nums">
                        {pol.qualityScore != null ? (
                          <div className="flex flex-col items-end">
                            <span className="text-[#F1F5F9] font-semibold">{pol.qualityScore.toFixed(2)}/10</span>
                            <span className="text-[9px] text-[#34D399] font-bold uppercase">Empirical N=200</span>
                          </div>
                        ) : (
                          <div className="flex flex-col items-end">
                            <span className="text-[#718096] text-[11px]">Unmeasured</span>
                            <span className="text-[9px] text-[#718096]">Requires Paid Pro Run</span>
                          </div>
                        )}
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        </div>

        {/* Allocation Stacked Bar Chart */}
        <div className="bg-[#141E2A] border border-[#263548] rounded-md p-4 space-y-3">
          <div className="flex items-center justify-between border-b border-[#263548] pb-2 font-mono text-xs">
            <span className="font-semibold text-[#F1F5F9]">
              Policy Model Tier Allocation Share (%)
            </span>
            <div className="flex items-center gap-3 text-[11px]">
              <span className="flex items-center gap-1.5"><span className="w-2.5 h-2.5 rounded bg-[#34D399]" /> Small</span>
              <span className="flex items-center gap-1.5"><span className="w-2.5 h-2.5 rounded bg-[#F59E0B]" /> Medium</span>
              <span className="flex items-center gap-1.5"><span className="w-2.5 h-2.5 rounded bg-[#818CF8]" /> Large</span>
            </div>
          </div>

          <div className="h-44 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={allocationChartData} margin={{ top: 10, right: 10, left: -20, bottom: 0 }} layout="vertical">
                <CartesianGrid strokeDasharray="2 2" stroke="#263548" horizontal={false} />
                <XAxis type="number" domain={[0, 100]} stroke="#718096" tick={{ fill: '#A0AEC0', fontSize: 10, fontFamily: 'monospace' }} unit="%" />
                <YAxis dataKey="name" type="category" stroke="#718096" tick={{ fill: '#A0AEC0', fontSize: 10, fontFamily: 'monospace' }} width={80} />
                <RechartsTooltip content={<CustomTooltip />} />
                <Bar dataKey="small" name="Small %" stackId="alloc" fill="#34D399" />
                <Bar dataKey="medium" name="Medium %" stackId="alloc" fill="#F59E0B" />
                <Bar dataKey="large" name="Large %" stackId="alloc" fill="#818CF8" />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
      </section>

      {/* ── Section 3: Evidence Classification (MANDATORY) ─────────── */}
      <section className="space-y-4">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 border-b border-[#263548] pb-2">
          <div className="flex items-center gap-2">
            <ShieldCheck className="w-4 h-4 text-[#3B82F6]" />
            <h2 className="text-sm font-semibold text-[#F1F5F9] uppercase tracking-wider font-mono">
              3. Experimental Evidence Classification &amp; Verification Status
            </h2>
          </div>
          <span className="text-[10px] font-mono text-[#718096] uppercase">
            Mandatory Academic Demarcation
          </span>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 font-mono text-xs">
          {policiesList.map((pol) => {
            const isEmpirical = pol.evidenceStatus === 'EMPIRICAL_REAL';

            return (
              <div 
                key={pol.id}
                className={`p-4 rounded-md border space-y-2.5 ${
                  isEmpirical 
                    ? 'bg-[#141E2A] border-[#34D399]/40' 
                    : 'bg-[#141E2A] border-[#263548]'
                }`}
              >
                <div className="flex items-center justify-between border-b border-[#263548] pb-2">
                  <div className="flex items-center gap-2">
                    <span className="w-2.5 h-2.5 rounded-full" style={{ backgroundColor: pol.color }} />
                    <span className="font-semibold text-[#F1F5F9]">{pol.name}</span>
                  </div>
                  <span className={`text-[9px] font-mono uppercase px-2 py-0.5 rounded border font-semibold ${
                    isEmpirical 
                      ? 'bg-[#34D399]/15 text-[#34D399] border-[#34D399]/30' 
                      : 'bg-[#192536] text-[#A0AEC0] border-[#263548]'
                  }`}>
                    {isEmpirical ? 'Empirical Real Benchmark' : 'Software Demo Validation'}
                  </span>
                </div>

                <div className="space-y-1">
                  <span className="font-semibold text-[#F1F5F9] text-[11px] block">
                    {pol.evidenceTitle}
                  </span>
                  <p className="text-[#A0AEC0] font-sans text-xs leading-relaxed">
                    {pol.evidenceDescription}
                  </p>
                </div>

                {isEmpirical && (
                  <div className="pt-2 border-t border-[#263548] grid grid-cols-3 gap-2 text-[10px] text-[#34D399]">
                    <div>Latency: <strong>{pol.meanLatency}s</strong></div>
                    <div>Quality: <strong>{pol.qualityScore}/10</strong></div>
                    <div>Actual: <strong>${pol.actualCost}</strong></div>
                  </div>
                )}
              </div>
            );
          })}
        </div>
      </section>

      {/* ── Section 4: Cost Comparison (Actual vs Projected) ───────── */}
      <section className="space-y-4">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 border-b border-[#263548] pb-2">
          <div className="flex items-center gap-2">
            <DollarSign className="w-4 h-4 text-[#34D399]" />
            <h2 className="text-sm font-semibold text-[#F1F5F9] uppercase tracking-wider font-mono">
              4. Cost Comparison: Measured Empirical vs Projected Estimates
            </h2>
          </div>
          <span className="text-[11px] font-mono text-[#A0AEC0]">
            Based on 43,344 measured tokens from Phase 6B.3
          </span>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
          {/* Chart */}
          <div className="lg:col-span-7 bg-[#141E2A] border border-[#263548] rounded-md p-4 space-y-3">
            <div className="flex items-center justify-between border-b border-[#263548] pb-2 font-mono text-xs">
              <span className="font-semibold text-[#F1F5F9]">Total Cost for 200 Benchmark Queries (USD)</span>
              <span className="text-[#34D399] text-[11px]">Small: $0.0876 (Measured)</span>
            </div>

            <div className="h-56 w-full">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={costChartData} margin={{ top: 10, right: 10, left: -10, bottom: 0 }}>
                  <CartesianGrid strokeDasharray="2 2" stroke="#263548" vertical={false} />
                  <XAxis dataKey="name" stroke="#718096" tick={{ fill: '#A0AEC0', fontSize: 10, fontFamily: 'monospace' }} />
                  <YAxis stroke="#718096" tick={{ fill: '#A0AEC0', fontSize: 10, fontFamily: 'monospace' }} tickFormatter={v => `$${v}`} />
                  <RechartsTooltip content={<CustomTooltip />} />
                  <Bar dataKey="cost" name="Total Cost ($)" radius={[2, 2, 0, 0]}>
                    {costChartData.map((entry, idx) => (
                      <Cell key={`cost-cell-${idx}`} fill={entry.color} />
                    ))}
                  </Bar>
                </BarChart>
              </ResponsiveContainer>
            </div>
          </div>

          {/* Cost Synthesis Cards */}
          <div className="lg:col-span-5 space-y-3 font-mono text-xs">
            <div className="bg-[#141E2A] border border-[#34D399]/40 rounded-md p-3.5 space-y-1">
              <span className="text-[10px] text-[#34D399] uppercase font-semibold block">Empirically Measured Baseline</span>
              <div className="flex items-baseline justify-between">
                <span className="text-xl font-bold text-[#F1F5F9]">$0.087601 USD</span>
                <span className="text-[10px] text-[#34D399] font-semibold">ALWAYS_SMALL</span>
              </div>
              <p className="text-[11px] text-[#A0AEC0] font-sans pt-1">
                200 prompts executed on gemini-3.5-flash-lite at $0.000438 per query average.
              </p>
            </div>

            <div className="bg-[#141E2A] border border-[#263548] rounded-md p-3.5 space-y-1">
              <span className="text-[10px] text-[#718096] uppercase font-semibold block">Always-Large Baseline Ceiling</span>
              <div className="flex items-baseline justify-between">
                <span className="text-xl font-bold text-[#818CF8]">$0.425768 USD</span>
                <span className="text-[10px] text-[#818CF8]">+386.0% vs Small</span>
              </div>
              <p className="text-[11px] text-[#A0AEC0] font-sans pt-1">
                Projected using gemini-pro-latest rates ($2.00 in / $12.00 out per 1M tokens).
              </p>
            </div>

            <div className="bg-[#141E2A] border border-[#263548] rounded-md p-3.5 space-y-1">
              <span className="text-[10px] text-[#3B82F6] uppercase font-semibold block">Dynamic Policy Projected Savings</span>
              <div className="flex items-center justify-between text-[#F1F5F9]">
                <span>RULE_BASED: <strong>$0.175405</strong></span>
                <span className="text-[#34D399] font-semibold">-58.8% vs Large</span>
              </div>
              <div className="flex items-center justify-between text-[#F1F5F9] pt-1">
                <span>ADAPTIVE_ML: <strong>$0.256039</strong></span>
                <span className="text-[#34D399] font-semibold">-39.9% vs Large</span>
              </div>
              <p className="text-[10px] text-[#718096] font-sans pt-1">
                Note: Projected costs apply actual Phase 6B.3 token distributions to model pricing models.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* ── Section 5: Routing Analysis ───────────────────────────── */}
      <section className="space-y-4">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 border-b border-[#263548] pb-2">
          <div className="flex items-center gap-2">
            <Layers className="w-4 h-4 text-[#3B82F6]" />
            <h2 className="text-sm font-semibold text-[#F1F5F9] uppercase tracking-wider font-mono">
              5. Architectural Routing Analysis: Adaptive ML vs. Rule-Based
            </h2>
          </div>

          <div className="flex items-center gap-1 bg-[#101722] p-1 rounded border border-[#263548] font-mono text-xs">
            <button
              onClick={() => setActiveAnalysisTab('category')}
              className={`px-2.5 py-1 rounded transition-colors ${
                activeAnalysisTab === 'category' 
                  ? 'bg-[#192536] text-[#F1F5F9] font-semibold' 
                  : 'text-[#718096] hover:text-[#F1F5F9]'
              }`}
            >
              By Category
            </button>
            <button
              onClick={() => setActiveAnalysisTab('difficulty')}
              className={`px-2.5 py-1 rounded transition-colors ${
                activeAnalysisTab === 'difficulty' 
                  ? 'bg-[#192536] text-[#F1F5F9] font-semibold' 
                  : 'text-[#718096] hover:text-[#F1F5F9]'
              }`}
            >
              By Difficulty
            </button>
          </div>
        </div>

        {/* Tab 1: Category Breakdown */}
        {activeAnalysisTab === 'category' ? (
          <div className="bg-[#141E2A] border border-[#263548] rounded-md p-5 space-y-4">
            <div className="flex items-center justify-between border-b border-[#263548] pb-2 font-mono text-xs">
              <div>
                <span className="font-semibold text-[#F1F5F9]">Large-Tier Escalation Rate by Benchmark Category (%)</span>
                <p className="text-[11px] text-[#A0AEC0] font-sans">
                  Shows how frequently each policy routes to the expensive LARGE tier across 7 task domains.
                </p>
              </div>
              <div className="flex items-center gap-3 text-[11px]">
                <span className="flex items-center gap-1.5"><span className="w-2.5 h-2.5 rounded bg-[#3B82F6]" /> Adaptive ML</span>
                <span className="flex items-center gap-1.5"><span className="w-2.5 h-2.5 rounded bg-[#A0AEC0]" /> Rule-Based</span>
              </div>
            </div>

            <div className="h-56 w-full">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={categoryComparisonData} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                  <CartesianGrid strokeDasharray="2 2" stroke="#263548" vertical={false} />
                  <XAxis dataKey="category" stroke="#718096" tick={{ fill: '#A0AEC0', fontSize: 10, fontFamily: 'monospace' }} />
                  <YAxis stroke="#718096" tick={{ fill: '#A0AEC0', fontSize: 10, fontFamily: 'monospace' }} unit="%" domain={[0, 100]} />
                  <RechartsTooltip content={<CustomTooltip />} />
                  <Bar dataKey="adaptiveMlLarge" name="Adaptive ML Large %" fill="#3B82F6" radius={[2, 2, 0, 0]} />
                  <Bar dataKey="ruleBasedLarge" name="Rule-Based Large %" fill="#A0AEC0" radius={[2, 2, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </div>

            <div className="pt-2 border-t border-[#263548] text-xs font-sans text-[#A0AEC0] leading-relaxed">
              <strong className="text-[#F1F5F9] font-mono text-[10px] uppercase block mb-1">Architectural Insight:</strong>
              ADAPTIVE_ML routes 100% of Summarization, 96.7% of Analytical Reasoning, and 92.0% of Instruction Following to LARGE because TF-IDF feature weights identify sentence length and reasoning keywords as requiring Pro models. Conversely, RULE_BASED centers heavily on MEDIUM (51.0%) due to its linear scoring formula.
            </div>
          </div>
        ) : (
          /* Tab 2: Difficulty Breakdown */
          <div className="bg-[#141E2A] border border-[#263548] rounded-md p-5 space-y-4">
            <div className="flex items-center justify-between border-b border-[#263548] pb-2 font-mono text-xs">
              <div>
                <span className="font-semibold text-[#F1F5F9]">Large-Tier Dependency by Difficulty (%)</span>
                <p className="text-[11px] text-[#A0AEC0] font-sans">
                  Percentage of queries escalated to LARGE across Easy, Medium, and Hard prompt tiers.
                </p>
              </div>
              <div className="flex items-center gap-3 text-[11px]">
                <span className="flex items-center gap-1.5"><span className="w-2.5 h-2.5 rounded bg-[#3B82F6]" /> Adaptive ML</span>
                <span className="flex items-center gap-1.5"><span className="w-2.5 h-2.5 rounded bg-[#A0AEC0]" /> Rule-Based</span>
              </div>
            </div>

            <div className="h-56 w-full">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={difficultyComparisonData} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                  <CartesianGrid strokeDasharray="2 2" stroke="#263548" vertical={false} />
                  <XAxis dataKey="level" stroke="#718096" tick={{ fill: '#A0AEC0', fontSize: 10, fontFamily: 'monospace' }} />
                  <YAxis stroke="#718096" tick={{ fill: '#A0AEC0', fontSize: 10, fontFamily: 'monospace' }} unit="%" domain={[0, 100]} />
                  <RechartsTooltip content={<CustomTooltip />} />
                  <Bar dataKey="adaptiveMl" name="Adaptive ML Large %" fill="#3B82F6" radius={[2, 2, 0, 0]} />
                  <Bar dataKey="ruleBased" name="Rule-Based Large %" fill="#A0AEC0" radius={[2, 2, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </div>

            <div className="pt-2 border-t border-[#263548] text-xs font-sans text-[#A0AEC0] leading-relaxed">
              <strong className="text-[#F1F5F9] font-mono text-[10px] uppercase block mb-1">Architectural Insight:</strong>
              In ADAPTIVE_ML, 64.7% of "Easy" queries route to LARGE, highlighting that prompt verbosity heavily biases the classifier regardless of intrinsic difficulty. In RULE_BASED, 21.0% of "Hard" queries route to SMALL due to concise problem statements lacking explicit trigger keywords.
            </div>
          </div>
        )}
      </section>

      {/* ── Section 6: Research Methodology & Limitations ─────────── */}
      <section className="bg-[#141E2A] border border-[#263548] rounded-md overflow-hidden">
        <button
          onClick={() => setShowMethodology(!showMethodology)}
          className="w-full px-5 py-3.5 bg-[#101722] border-b border-[#263548] flex items-center justify-between text-left text-xs font-mono font-semibold uppercase tracking-wider text-[#F1F5F9] hover:bg-[#192536] transition-colors"
        >
          <div className="flex items-center gap-2">
            <FileText className="w-4 h-4 text-[#3B82F6]" />
            <span>6. Research Methodology, Bounds &amp; Limitations</span>
          </div>
          {showMethodology ? <ChevronUp className="w-4 h-4 text-[#A0AEC0]" /> : <ChevronDown className="w-4 h-4 text-[#A0AEC0]" />}
        </button>

        {showMethodology && (
          <div className="p-5 space-y-4 text-xs font-mono">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {RESEARCH_LIMITATIONS.map((lim, idx) => (
                <div key={idx} className="p-3.5 rounded bg-[#101722] border border-[#263548] space-y-1.5">
                  <span className="font-semibold text-[#F1F5F9] text-[11px] block flex items-center gap-1.5">
                    <span className="w-1.5 h-1.5 rounded-full bg-[#F59E0B]" />
                    {lim.title}
                  </span>
                  <p className="text-[#A0AEC0] font-sans leading-relaxed text-xs">
                    {lim.text}
                  </p>
                </div>
              ))}
            </div>

            <div className="pt-3 border-t border-[#263548] text-[#718096] text-[11px] font-sans flex items-center justify-between">
              <span>Benchmark v2 Dataset SHA-256: <code className="text-[#A0AEC0] font-mono">{BENCHMARK_METADATA.sha256.slice(0, 24)}...</code></span>
              <span className="font-mono">Google DeepMind Autonomous Systems • Nov 2026</span>
            </div>
          </div>
        )}
      </section>
    </div>
  );
}
