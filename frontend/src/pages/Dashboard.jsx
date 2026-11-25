import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { 
  Send, 
  Activity, 
  Clock, 
  TrendingDown, 
  Award, 
  AlertCircle, 
  RefreshCw, 
  Cpu, 
  ChevronRight, 
  CheckCircle, 
  ArrowRight, 
  BarChart2, 
  Layers,
  Sparkles,
  Info,
  Zap,
  Server
} from 'lucide-react';
import { api } from '../services/api';
import { StatCard } from '../components/StatCard';
import { ModelBadge } from '../components/ModelBadge';
import { ExecutionModeBadge } from '../components/ExecutionModeBadge';
import { CustomTooltip } from '../components/CustomTooltip';
import { EmptyState } from '../components/EmptyState';
import { 
  PieChart, Pie, Cell, 
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip as RechartsTooltip, ResponsiveContainer 
} from 'recharts';

const SAMPLE_QUERIES = [
  { label: 'Capital QA', query: 'What is the capital of India?' },
  { label: 'Gradient Descent', query: 'Why does gradient descent sometimes fail to converge on non-convex loss surfaces?' },
  { label: 'Fraud Detection Architecture', query: 'Design a machine learning pipeline for detecting fraudulent transactions with severe class imbalance, including streaming ingestion, feature store, and monitoring.' }
];

const TIER_COLORS = {
  SMALL: '#34D399',
  MEDIUM: '#F59E0B',
  LARGE: '#818CF8'
};

export default function Dashboard({ demoMode }) {
  const [query, setQuery] = useState('');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [metrics, setMetrics] = useState(null);
  const [metricsLoading, setMetricsLoading] = useState(true);
  const [health, setHealth] = useState(null);

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    setMetricsLoading(true);
    const [m, h] = await Promise.all([
      api.getMetrics(),
      api.getHealth()
    ]);
    if (m) setMetrics(m);
    if (h) setHealth(h);
    setMetricsLoading(false);
  };

  const handleQuery = async (e) => {
    e?.preventDefault();
    if (!query.trim()) return;

    setLoading(true);
    try {
      const data = await api.queryModel(query.trim(), demoMode);
      setResult(data);
      fetchData();
    } catch (err) {
      console.error("Query failed:", err);
    } finally {
      setLoading(false);
    }
  };

  const totalQueries = metrics?.total_queries ?? 0;
  const hasTelemetry = totalQueries > 0;

  // Chart datasets
  const pieData = (hasTelemetry && metrics?.model_distribution) ? [
    { name: 'SMALL', value: metrics.model_distribution.SMALL || 0 },
    { name: 'MEDIUM', value: metrics.model_distribution.MEDIUM || 0 },
    { name: 'LARGE', value: metrics.model_distribution.LARGE || 0 }
  ].filter(d => d.value > 0) : [];

  const costData = (hasTelemetry && metrics && metrics.avg_cost != null) ? [
    { name: 'Adaptive Router', cost: Number(metrics.avg_cost.toFixed(5)) },
    { name: 'Always-Large', cost: Number((metrics.cost_by_model?.LARGE ?? metrics.avg_baseline_cost ?? metrics.avg_cost).toFixed(5)) }
  ] : [];

  const latencyData = (hasTelemetry && metrics && metrics.avg_latency != null) ? [
    { name: 'Adaptive Router', latency: Number(metrics.avg_latency.toFixed(3)) },
    { name: 'Always-Large', latency: Number((metrics.latency_by_model?.LARGE ?? metrics.avg_baseline_latency ?? metrics.avg_latency).toFixed(3)) }
  ] : [];

  // Safely formatted KPI values
  const latencyDisplay = hasTelemetry && metrics?.avg_latency != null
    ? `${metrics.avg_latency.toFixed(2)}s`
    : null;

  const costSavingsDisplay = hasTelemetry && metrics?.avg_cost_reduction != null
    ? `${(metrics.avg_cost_reduction * 100).toFixed(1)}%`
    : null;

  const qualityRetentionDisplay = hasTelemetry && metrics?.avg_quality_retention != null
    ? `${(metrics.avg_quality_retention * 100).toFixed(1)}%`
    : null;

  return (
    <div className="p-4 sm:p-6 lg:p-8 max-w-7xl mx-auto space-y-6 pb-24">
      {/* ── Page Header ────────────────────────────────────────────── */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-4 border-b border-[#263548]">
        <div>
          <div className="flex items-center gap-2.5 mb-1">
            <h1 className="text-xl font-bold tracking-tight text-[#F1F5F9]">
              TIERFLOW <span className="text-[#3B82F6] font-medium">Overview</span>
            </h1>
            <span className="text-[10px] font-mono uppercase px-2 py-0.5 rounded bg-[#192536] text-[#A0AEC0] border border-[#263548]">
              Live Session Telemetry (N = {totalQueries})
            </span>
          </div>
          <p className="text-xs text-[#A0AEC0] font-sans">
            Real-time telemetry from interactive queries. For offline N = 200 benchmark evaluation, see{' '}
            <Link to="/research" className="text-[#3B82F6] hover:underline">
              Research &amp; Benchmark
            </Link>.
          </p>
        </div>

        <div className="flex flex-wrap items-center gap-2.5">
          {/* Provider & Execution Mode status */}
          <div className="inline-flex items-center gap-2 px-3 py-1.5 rounded-md text-xs font-mono border bg-[#141E2A] border-[#263548]">
            <span className={`w-2 h-2 rounded-full ${health?.has_api_key ? 'bg-[#34D399] animate-pulse' : 'bg-[#F59E0B]'}`} />
            <span className="text-[#F1F5F9] font-medium">
              {health?.has_api_key ? 'Live Mode' : 'Demo Mode'}
            </span>
            <span className="text-[#718096]">|</span>
            <span className="text-[#A0AEC0]">{health?.provider || 'Gemini'}</span>
          </div>

          <Link
            to="/playground"
            className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-md text-xs font-medium text-white bg-[#3B82F6] hover:bg-[#2563EB] shadow-xs transition-colors shrink-0"
          >
            <Cpu className="w-3.5 h-3.5" />
            <span>Open Playground</span>
            <ArrowRight className="w-3 h-3 ml-0.5" />
          </Link>
        </div>
      </div>

      {/* ── KPI Metric Cards ──────────────────────────────────────── */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3.5">
        <StatCard
          title="Session Routed Queries"
          value={hasTelemetry ? totalQueries : '0'}
          subtitle={hasTelemetry ? `Live session requests (N = ${totalQueries})` : "Awaiting session or demo queries"}
          badge={`Session N = ${totalQueries}`}
          dataSource={demoMode ? "Simulated" : "Live State"}
        />

        <StatCard
          title="Average Latency"
          value={latencyDisplay}
          subtitle={hasTelemetry && metrics?.avg_baseline_latency != null 
            ? (demoMode 
                ? `vs ${metrics.avg_baseline_latency.toFixed(2)}s Always-Large (Simulated)`
                : `Empirical latency (Baseline unmeasured in live session)`)
            : "Requires session telemetry"}
          trend={latencyDisplay ? "up" : null}
          badge={hasTelemetry ? (demoMode ? "Simulated P50" : "Empirical Real") : "P50 / Avg"}
          dataSource={hasTelemetry ? (demoMode ? "Simulated" : "Measured") : null}
        />

        <StatCard
          title="Inference Cost Reduction"
          value={costSavingsDisplay ? `+${costSavingsDisplay}` : null}
          subtitle={costSavingsDisplay ? "Pricing differential vs Always-Large ($0.075 vs $1.25/M tokens)" : "Requires session telemetry"}
          trend={costSavingsDisplay ? "up" : null}
          badge="Projected Cost Δ"
          badgeColor={costSavingsDisplay ? "success" : "default"}
          dataSource={hasTelemetry ? "Model Rate Cards" : null}
        />

        <StatCard
          title="Quality Score Retention"
          value={qualityRetentionDisplay}
          subtitle={qualityRetentionDisplay 
            ? (demoMode ? `Simulated heuristic parity (N = ${totalQueries})` : "Benchmark-evaluated task parity") 
            : "Unmeasured for freeform live prompts"}
          trend={qualityRetentionDisplay ? "up" : null}
          badge={qualityRetentionDisplay ? (demoMode ? "Simulated Heuristic" : "Reference Evaluated") : "Ground Truth"}
          dataSource={hasTelemetry ? (demoMode ? "Heuristic Evaluator" : "Task Evaluator") : null}
        />
      </div>

      {/* ── Quick Route Inspector ─────────────────────────────────── */}
      <div className="bg-[#141E2A] border border-[#263548] rounded-md overflow-hidden">
        <div className="px-4 py-2.5 bg-[#101722] border-b border-[#263548] flex items-center justify-between text-xs">
          <div className="flex items-center gap-2">
            <Zap className="w-3.5 h-3.5 text-[#3B82F6]" />
            <span className="font-mono text-[11px] font-semibold text-[#F1F5F9] uppercase tracking-wider">
              Quick Route Inspector
            </span>
          </div>
          <span className="text-[10px] font-mono text-[#718096]">
            Classify complexity &amp; predict tier allocation
          </span>
        </div>

        <form onSubmit={handleQuery} className="p-4 space-y-3">
          <div className="space-y-1.5">
            <div className="flex items-center justify-between text-[11px] font-mono text-[#718096]">
              <span>QUERY PROMPT</span>
              <div className="flex items-center gap-2">
                <span>{query.trim() ? query.trim().split(/\s+/).length : 0} words</span>
                <span>•</span>
                <span>{query.length} chars</span>
              </div>
            </div>
            <div className="flex flex-col sm:flex-row gap-2">
              <textarea
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                placeholder="Enter prompt to inspect tier routing (e.g., 'What is the capital of India?' or 'Design a distributed fault-tolerant key-value store')..."
                rows={2}
                className="flex-1 bg-[#0D141D] border border-[#263548] rounded-md px-3.5 py-2 text-xs font-sans text-[#F1F5F9] placeholder:text-[#718096] focus:outline-none focus:border-[#3B82F6] transition-colors resize-y min-h-[60px]"
              />
              <button
                type="submit"
                disabled={loading || !query.trim()}
                className="px-4 py-2 rounded-md text-xs font-mono font-medium text-white bg-[#3B82F6] hover:bg-[#2563EB] shadow-xs disabled:opacity-40 disabled:cursor-not-allowed transition-colors shrink-0 flex items-center justify-center gap-1.5 self-start sm:self-auto h-auto min-h-[42px]"
              >
                {loading ? <RefreshCw className="w-3.5 h-3.5 animate-spin" /> : <Send className="w-3.5 h-3.5" />}
                <span>Inspect Route</span>
              </button>
            </div>
          </div>

          <div className="flex flex-wrap items-center gap-1.5 pt-1 text-xs">
            <span className="text-[10px] font-mono text-[#718096] uppercase tracking-wider shrink-0 mr-1">
              Sample prompts:
            </span>
            {SAMPLE_QUERIES.map((s) => (
              <button
                key={s.label}
                type="button"
                onClick={() => setQuery(s.query)}
                className="text-[11px] font-mono px-2.5 py-1 rounded bg-[#192536] hover:bg-[#263548] text-[#A0AEC0] hover:text-[#F1F5F9] border border-[#263548] transition-colors shrink-0"
                title={s.query}
              >
                {s.label}
              </button>
            ))}
          </div>
        </form>

        {/* Quick Result Preview */}
        {result && (
          <div className="border-t border-[#263548] bg-[#101722] p-4 text-xs font-mono space-y-3">
            <div className="flex flex-wrap items-center justify-between gap-3 bg-[#141E2A] p-3 rounded border border-[#263548]">
              <div className="flex flex-wrap items-center gap-3">
                <span className="text-[#718096] text-[11px]">Selected Tier:</span>
                <ModelBadge model={result.routing?.selected_model} size="lg" />
                <span className="text-[#A0AEC0]">
                  Confidence: <strong className="text-[#F1F5F9]">{((result.routing?.confidence ?? 0) * 100).toFixed(1)}%</strong>
                </span>
                <span className="text-[#A0AEC0]">
                  Complexity: <strong className="text-[#F1F5F9] uppercase">{result.routing?.complexity}</strong>
                </span>
              </div>
              <div className="flex items-center gap-3 text-[11px] text-[#A0AEC0]">
                <span>Latency: <strong className="text-[#F1F5F9]">{result.metrics?.latency != null ? `${result.metrics.latency.toFixed(3)}s` : 'N/A'}</strong></span>
                <span>Cost: <strong className="text-[#F1F5F9]">${result.metrics?.estimated_cost != null ? result.metrics.estimated_cost.toFixed(5) : '0.00000'}</strong></span>
                <ExecutionModeBadge mode={result.execution_mode} />
              </div>
            </div>

            {/* Rationale description */}
            {result.routing?.reasoning && (
              <div className="px-3 py-2 bg-[#0D141D] rounded border border-[#1E2A39] text-[11px] text-[#A0AEC0] flex items-center justify-between">
                <span><strong className="text-[#F1F5F9]">Rationale:</strong> {result.routing.reasoning}</span>
                <span className="text-[10px] text-[#718096] shrink-0 ml-2">TF-IDF + Logistic Regression</span>
              </div>
            )}

            {/* Response preview */}
            {result.response && (
              <div className="p-3 bg-[#0D141D] rounded border border-[#1E2A39] text-[#F1F5F9] text-xs font-sans leading-relaxed whitespace-pre-wrap max-h-32 overflow-y-auto">
                {result.response}
              </div>
            )}
          </div>
        )}
      </div>

      {/* ── Visual Telemetry Section ──────────────────────────────── */}
      <div className="space-y-2">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <BarChart2 className="w-4 h-4 text-[#3B82F6]" />
            <h2 className="text-xs font-mono font-semibold uppercase tracking-wider text-[#F1F5F9]">
              Aggregate System Telemetry
            </h2>
          </div>
          <span className="text-[10px] font-mono text-[#718096]">
            {demoMode ? "Source: Local Simulation / Session" : "Source: Live API Telemetry"}
          </span>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
          {/* Chart 1: Model Routing Distribution */}
          <div className="bg-[#141E2A] border border-[#263548] rounded-md p-4 flex flex-col justify-between h-72">
            <div className="flex items-center justify-between border-b border-[#263548] pb-2">
              <div className="flex items-center gap-1.5">
                <Layers className="w-3.5 h-3.5 text-[#A0AEC0]" />
                <span className="text-[11px] font-mono font-semibold uppercase tracking-wider text-[#F1F5F9]">
                  Tier Allocation Share
                </span>
              </div>
              <span className="text-[10px] font-mono text-[#718096]">Actual Count</span>
            </div>

            {hasTelemetry && pieData.length > 0 ? (
              <>
                <div className="h-44 w-full">
                  <ResponsiveContainer width="100%" height="100%">
                    <PieChart>
                      <Pie
                        data={pieData}
                        cx="50%"
                        cy="50%"
                        innerRadius={48}
                        outerRadius={68}
                        paddingAngle={3}
                        dataKey="value"
                        stroke="#141E2A"
                        strokeWidth={2}
                      >
                        {pieData.map((entry) => (
                          <Cell key={`cell-${entry.name}`} fill={TIER_COLORS[entry.name] || '#3B82F6'} />
                        ))}
                      </Pie>
                      <RechartsTooltip content={<CustomTooltip />} />
                    </PieChart>
                  </ResponsiveContainer>
                </div>

                <div className="flex items-center justify-center gap-4 text-[11px] font-mono text-[#A0AEC0] pt-1 border-t border-[#263548]">
                  <span className="flex items-center gap-1.5">
                    <span className="w-2 h-2 rounded-full bg-[#34D399]" /> Small ({metrics?.model_distribution?.SMALL || 0})
                  </span>
                  <span className="flex items-center gap-1.5">
                    <span className="w-2 h-2 rounded-full bg-[#F59E0B]" /> Med ({metrics?.model_distribution?.MEDIUM || 0})
                  </span>
                  <span className="flex items-center gap-1.5">
                    <span className="w-2 h-2 rounded-full bg-[#818CF8]" /> Large ({metrics?.model_distribution?.LARGE || 0})
                  </span>
                </div>
              </>
            ) : (
              <EmptyState 
                title="No Tier Allocations"
                message="Run prompt inspections or benchmark experiments to populate distribution data."
                className="h-52 border-none bg-transparent"
              />
            )}
          </div>

          {/* Chart 2: Cost Comparison */}
          <div className="bg-[#141E2A] border border-[#263548] rounded-md p-4 flex flex-col justify-between h-72">
            <div className="flex items-center justify-between border-b border-[#263548] pb-2">
              <div className="flex items-center gap-1.5">
                <TrendingDown className="w-3.5 h-3.5 text-[#34D399]" />
                <span className="text-[11px] font-mono font-semibold uppercase tracking-wider text-[#F1F5F9]">
                  Mean Inference Cost ($)
                </span>
              </div>
              <span className="text-[10px] font-mono text-[#34D399] font-semibold">
                {costSavingsDisplay ? `-${costSavingsDisplay}` : 'N/A'}
              </span>
            </div>

            {hasTelemetry && costData.length > 0 ? (
              <div className="h-52 w-full pt-2">
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={costData} margin={{ top: 10, right: 10, left: -15, bottom: 0 }}>
                    <CartesianGrid strokeDasharray="2 2" stroke="#263548" vertical={false} />
                    <XAxis dataKey="name" stroke="#718096" tick={{ fill: '#A0AEC0', fontSize: 10, fontFamily: 'monospace' }} />
                    <YAxis stroke="#718096" tick={{ fill: '#A0AEC0', fontSize: 10, fontFamily: 'monospace' }} />
                    <RechartsTooltip content={<CustomTooltip />} />
                    <Bar dataKey="cost" name="Inference Cost ($)" fill="#3B82F6" radius={[2, 2, 0, 0]} />
                  </BarChart>
                </ResponsiveContainer>
              </div>
            ) : (
              <EmptyState 
                title="No Cost Telemetry"
                message="Cost metrics will display here after executing routed requests."
                className="h-52 border-none bg-transparent"
              />
            )}
          </div>

          {/* Chart 3: Latency Comparison */}
          <div className="bg-[#141E2A] border border-[#263548] rounded-md p-4 flex flex-col justify-between h-72">
            <div className="flex items-center justify-between border-b border-[#263548] pb-2">
              <div className="flex items-center gap-1.5">
                <Clock className="w-3.5 h-3.5 text-[#F59E0B]" />
                <span className="text-[11px] font-mono font-semibold uppercase tracking-wider text-[#F1F5F9]">
                  Mean Latency (Seconds)
                </span>
              </div>
              <span className="text-[10px] font-mono text-[#F59E0B] font-semibold">
                {latencyDisplay || 'N/A'}
              </span>
            </div>

            {hasTelemetry && latencyData.length > 0 ? (
              <div className="h-52 w-full pt-2">
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={latencyData} margin={{ top: 10, right: 10, left: -15, bottom: 0 }}>
                    <CartesianGrid strokeDasharray="2 2" stroke="#263548" vertical={false} />
                    <XAxis dataKey="name" stroke="#718096" tick={{ fill: '#A0AEC0', fontSize: 10, fontFamily: 'monospace' }} />
                    <YAxis stroke="#718096" tick={{ fill: '#A0AEC0', fontSize: 10, fontFamily: 'monospace' }} />
                    <RechartsTooltip content={<CustomTooltip />} />
                    <Bar dataKey="latency" name="Latency (s)" fill="#F59E0B" radius={[2, 2, 0, 0]} />
                  </BarChart>
                </ResponsiveContainer>
              </div>
            ) : (
              <EmptyState 
                title="No Latency Telemetry"
                message="Latency benchmarks will populate once requests are processed."
                className="h-52 border-none bg-transparent"
              />
            )}
          </div>
        </div>
      </div>

      {/* ── Research Architecture Summary ─────────────────────────── */}
      <div className="bg-[#141E2A] border border-[#263548] rounded-md p-5 space-y-4">
        <div className="flex items-center justify-between border-b border-[#263548] pb-3">
          <div className="flex items-center gap-2">
            <Server className="w-4 h-4 text-[#3B82F6]" />
            <h2 className="text-xs font-mono font-semibold uppercase tracking-wider text-[#F1F5F9]">
              How TIERFLOW Adaptive Routing Works
            </h2>
          </div>
          <Link
            to="/research"
            className="text-xs font-mono text-[#3B82F6] hover:text-[#2563EB] flex items-center gap-1 font-semibold transition-colors"
          >
            <span>Explore 200-Prompt Benchmark</span>
            <ChevronRight className="w-3.5 h-3.5" />
          </Link>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-xs font-mono">
          {/* Small Tier */}
          <div className="p-3.5 rounded bg-[#101722] border border-[#263548] space-y-2">
            <div className="flex items-center justify-between">
              <ModelBadge model="SMALL" />
              <span className="text-[10px] text-[#34D399]">$0.30 / $2.50 per 1M</span>
            </div>
            <p className="text-[#A0AEC0] font-sans leading-relaxed text-[11px]">
              Mapped to <strong className="text-[#F1F5F9]">gemini-3.5-flash-lite</strong>. Handles factual lookup, definitions, simple Q&amp;A, and basic summarization with sub-second turnaround.
            </p>
          </div>

          {/* Medium Tier */}
          <div className="p-3.5 rounded bg-[#101722] border border-[#263548] space-y-2">
            <div className="flex items-center justify-between">
              <ModelBadge model="MEDIUM" />
              <span className="text-[10px] text-[#F59E0B]">$0.75 / $3.75 per 1M</span>
            </div>
            <p className="text-[#A0AEC0] font-sans leading-relaxed text-[11px]">
              Mapped to <strong className="text-[#F1F5F9]">gemini-flash-latest</strong>. Balanced reasoning for conceptual explanations, comparisons, multi-step math, and standard programming tasks.
            </p>
          </div>

          {/* Large Tier */}
          <div className="p-3.5 rounded bg-[#101722] border border-[#263548] space-y-2">
            <div className="flex items-center justify-between">
              <ModelBadge model="LARGE" />
              <span className="text-[10px] text-[#818CF8]">$2.00 / $12.00 per 1M</span>
            </div>
            <p className="text-[#A0AEC0] font-sans leading-relaxed text-[11px]">
              Mapped to <strong className="text-[#F1F5F9]">gemini-pro-latest</strong>. Heavy algorithmic proofs, complex systems architecture, formal constraint satisfaction, and long-form synthesis.
            </p>
          </div>
        </div>

        {/* Observability Protocol Notice */}
        <div className="pt-2 border-t border-[#263548] flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3 text-xs font-mono text-[#A0AEC0]">
          <div className="flex items-center gap-2">
            <CheckCircle className="w-4 h-4 text-[#34D399] flex-shrink-0" />
            <span>
              <strong className="text-[#F1F5F9]">Evaluation Protocol:</strong> Held-out classifier testing uses a 70/15/15 stratified split. Model benchmarks use Benchmark v2 ($N=200$ prompts across 7 cognitive categories).
            </span>
          </div>
          <Link
            to="/experiments"
            className="text-[#3B82F6] hover:text-blue-400 font-semibold shrink-0 flex items-center gap-1"
          >
            <span>View Experiment Logs</span>
            <ArrowRight className="w-3 h-3" />
          </Link>
        </div>
      </div>
    </div>
  );
}
