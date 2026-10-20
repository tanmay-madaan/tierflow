import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { Send, Activity, Clock, TrendingDown, Award, AlertCircle, RefreshCw, Cpu, ChevronRight, CheckCircle, ArrowRight, BarChart2, Layers } from 'lucide-react';
import { api } from '../services/api';
import { StatCard } from '../components/StatCard';
import { ModelBadge } from '../components/ModelBadge';
import { 
  PieChart, Pie, Cell, 
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip as RechartsTooltip, Legend, ResponsiveContainer 
} from 'recharts';

const SAMPLE_QUERIES = [
  { label: 'Capital QA', query: 'What is the capital of India?' },
  { label: 'Explain Gradient Descent', query: 'Why does gradient descent sometimes fail to converge?' },
  { label: 'Fraud Detection Architecture', query: 'Design a machine learning pipeline for detecting fraudulent transactions with severe class imbalance and explain how you would evaluate it.' }
];

const COLORS = {
  SMALL: '#34D399',
  MEDIUM: '#F59E0B',
  LARGE: '#6366F1'
};

const CustomTooltip = ({ active, payload, label }) => {
  if (active && payload && payload.length) {
    return (
      <div className="bg-[#121923] border border-[#293545] rounded-md px-3 py-2 text-xs font-mono shadow-xl">
        <p className="text-[#94A3B8] mb-1">{label || payload[0]?.name}</p>
        {payload.map((entry, idx) => (
          <p key={idx} className="font-semibold text-[#F1F5F9]">
            <span style={{ color: entry.color || entry.fill }}>{entry.name}: </span>
            {entry.value}
          </p>
        ))}
      </div>
    );
  }
  return null;
};

export default function Dashboard({ demoMode }) {
  const [query, setQuery] = useState('');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [metrics, setMetrics] = useState(null);

  useEffect(() => {
    fetchMetrics();
  }, []);

  const fetchMetrics = async () => {
    const data = await api.getMetrics();
    if (data) setMetrics(data);
  };

  const handleQuery = async (e) => {
    e?.preventDefault();
    if (!query.trim()) return;

    setLoading(true);
    const data = await api.queryModel(query, demoMode);
    setResult(data);
    setLoading(false);
    fetchMetrics();
  };

  const pieData = metrics?.model_distribution ? [
    { name: 'SMALL', value: metrics.model_distribution.SMALL || 0 },
    { name: 'MEDIUM', value: metrics.model_distribution.MEDIUM || 0 },
    { name: 'LARGE', value: metrics.model_distribution.LARGE || 0 }
  ] : [];

  const costData = metrics && metrics.avg_cost != null ? [
    { name: 'Adaptive Router', cost: Number(metrics.avg_cost.toFixed(5)) },
    { name: 'Always-Large Baseline', cost: Number((metrics.cost_by_model?.LARGE ?? metrics.avg_baseline_cost ?? metrics.avg_cost).toFixed(5)) }
  ] : [];

  const latencyData = metrics && metrics.avg_latency != null ? [
    { name: 'Adaptive Router', latency: Number(metrics.avg_latency.toFixed(2)) },
    { name: 'Always-Large Baseline', latency: Number((metrics.latency_by_model?.LARGE ?? metrics.avg_baseline_latency ?? metrics.avg_latency).toFixed(2)) }
  ] : [];

  const totalQueries = metrics?.total_queries ?? 0;
  const costSavingsPct = metrics?.avg_cost_reduction != null ? (metrics.avg_cost_reduction * 100).toFixed(1) : '0.0';
  const latencyReductionPct = metrics?.avg_latency_reduction != null ? (metrics.avg_latency_reduction * 100).toFixed(1) : '0.0';
  const qualityRetentionPct = metrics?.avg_quality_retention != null ? `${(metrics.avg_quality_retention * 100).toFixed(1)}%` : '—';

  return (
    <div className="p-6 md:p-8 max-w-7xl mx-auto space-y-6 pb-24 h-full overflow-y-auto">
      {/* Overview Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-4 border-b border-[#293545]">
        <div>
          <div className="flex items-center gap-2.5 mb-1">
            <h1 className="text-xl font-bold tracking-tight text-[#F1F5F9]">
              TIERFLOW <span className="text-[#3B82F6] font-medium">Overview</span>
            </h1>
            <span className="text-[10px] font-mono uppercase px-2 py-0.5 rounded bg-[#1A2431] text-[#94A3B8] border border-[#293545]">
              Adaptive LLM Inference
            </span>
          </div>
          <p className="text-xs text-[#94A3B8]">
            Route smarter. Measure everything. Aggregate telemetry, routing distributions, and empirical efficiency comparisons.
          </p>
        </div>

        <div className="flex items-center gap-2.5">
          <Link
            to="/playground"
            className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-md text-xs font-medium text-white bg-[#3B82F6] hover:bg-blue-500 shadow-sm transition-colors"
          >
            <Cpu className="w-3.5 h-3.5" />
            <span>Open Playground</span>
            <ArrowRight className="w-3 h-3 ml-0.5" />
          </Link>

          <div className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-md text-xs font-mono font-medium border bg-[#121923] border-[#293545]">
            <span className={`w-1.5 h-1.5 rounded-full ${demoMode ? 'bg-amber-400' : 'bg-[#34D399]'}`} />
            <span className="text-[#F1F5F9]">{demoMode ? 'Demo Mode' : 'Live Mode'}</span>
          </div>
        </div>
      </div>

      {/* KPI Stat Cards (With Concrete Context) */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3.5">
        <StatCard
          title="Total Routed Queries"
          value={totalQueries}
          subtitle="Cumulative session & benchmark queries"
          badge="Inferences"
        />
        <StatCard
          title="Mean Latency"
          value={`${metrics?.avg_latency != null ? metrics.avg_latency.toFixed(2) : '0.00'}s`}
          subtitle={`vs ${metrics?.avg_baseline_latency != null ? metrics.avg_baseline_latency.toFixed(2) : '2.80'}s Always-Large`}
          trend="up"
          badge="P50 / Avg"
        />
        <StatCard
          title="Inference Cost Reduction"
          value={`+${costSavingsPct}%`}
          subtitle="Measured against single-tier baseline"
          trend="up"
          badge="Token Savings"
        />
        <StatCard
          title="Quality Score Retention"
          value={qualityRetentionPct}
          subtitle={metrics?.avg_quality_retention != null ? "Benchmark-evaluated retention" : "Awaiting reference evaluation"}
          trend="up"
          badge="Parity"
        />
      </div>

      {/* Quick Route Inspector */}
      <div className="bg-[#121923] border border-[#293545] rounded-md overflow-hidden">
        <div className="px-4 py-2.5 bg-[#0E141C] border-b border-[#293545] flex items-center justify-between text-xs">
          <span className="font-mono text-[11px] font-semibold text-[#F1F5F9] uppercase tracking-wider">
            Quick Route Inspector
          </span>
          <span className="text-[10px] font-mono text-[#94A3B8]">Classify &amp; measure any query</span>
        </div>

        <form onSubmit={handleQuery} className="p-4 space-y-3">
          <div className="flex gap-2">
            <input
              type="text"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder="Test prompt classification (e.g. 'Explain gradient descent convergence criteria')..."
              className="flex-1 bg-[#0E141C] border border-[#293545] rounded-md px-3.5 py-2 text-xs font-sans text-[#F1F5F9] placeholder:text-neutral-600 focus:outline-none focus:border-[#3B82F6] transition-colors"
            />
            <button
              type="submit"
              disabled={loading || !query.trim()}
              className="px-4 py-2 rounded-md text-xs font-medium text-white bg-[#3B82F6] hover:bg-blue-500 shadow-sm disabled:opacity-40 disabled:cursor-not-allowed transition-colors shrink-0 flex items-center gap-1.5"
            >
              {loading ? <RefreshCw className="w-3.5 h-3.5 animate-spin" /> : <Send className="w-3.5 h-3.5" />}
              <span>Inspect Route</span>
            </button>
          </div>

          <div className="flex items-center gap-2 overflow-x-auto text-xs">
            <span className="text-[10px] font-mono text-[#94A3B8] uppercase tracking-wider shrink-0">Quick prompts:</span>
            {SAMPLE_QUERIES.map((s) => (
              <button
                key={s.label}
                type="button"
                onClick={() => setQuery(s.query)}
                className="text-[11px] font-mono px-2 py-0.5 rounded bg-[#1A2431] hover:bg-[#293545] text-[#94A3B8] hover:text-[#F1F5F9] border border-[#293545] transition-colors shrink-0"
              >
                {s.label}
              </button>
            ))}
          </div>
        </form>

        {/* Quick Result Preview */}
        {result && (
          <div className="border-t border-[#293545] bg-[#0E141C] p-4 text-xs font-mono space-y-3">
            <div className="flex flex-wrap items-center justify-between gap-3">
              <div className="flex items-center gap-3">
                <span className="text-[#94A3B8] text-[11px]">Selected:</span>
                <ModelBadge model={result.routing?.selected_model} />
                <span className="text-[#94A3B8]">Confidence: <strong className="text-[#F1F5F9]">{((result.routing?.confidence ?? 0) * 100).toFixed(1)}%</strong></span>
                <span className="text-[#94A3B8]">Complexity: <strong className="text-[#F1F5F9] uppercase">{result.routing?.complexity}</strong></span>
              </div>
              <div className="flex items-center gap-4 text-[11px] text-[#94A3B8]">
                <span>Latency: <strong className="text-[#F1F5F9]">{result.metrics?.latency != null ? result.metrics.latency.toFixed(2) : '0.00'}s</strong></span>
                <span>Cost: <strong className="text-[#F1F5F9]">${result.metrics?.estimated_cost != null ? result.metrics.estimated_cost.toFixed(5) : '0.00000'}</strong></span>
                <span className="text-[#34D399] font-semibold">Saved: {result.comparison?.cost_reduction != null ? result.comparison.cost_reduction.toFixed(1) : '0.0'}%</span>
              </div>
            </div>

            {result.response && (
              <div className="p-3 bg-[#121923] rounded border border-[#293545] text-[#F1F5F9] text-xs font-sans leading-relaxed whitespace-pre-wrap max-h-32 overflow-y-auto">
                {result.response}
              </div>
            )}
          </div>
        )}
      </div>

      {/* Visual Telemetry Charts Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
        {/* Chart 1: Model Routing Distribution */}
        <div className="bg-[#121923] border border-[#293545] rounded-md p-4 flex flex-col justify-between h-72">
          <div className="flex items-center justify-between border-b border-[#293545] pb-2">
            <div className="flex items-center gap-1.5">
              <Layers className="w-3.5 h-3.5 text-[#94A3B8]" />
              <span className="text-[11px] font-mono font-semibold uppercase tracking-wider text-[#F1F5F9]">
                Tier Allocation Share
              </span>
            </div>
            <span className="text-[10px] font-mono text-[#94A3B8]">Ratio (%)</span>
          </div>

          <div className="h-44 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie
                  data={pieData}
                  cx="50%"
                  cy="50%"
                  innerRadius={50}
                  outerRadius={68}
                  paddingAngle={3}
                  dataKey="value"
                  stroke="#121923"
                  strokeWidth={2}
                >
                  {pieData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={COLORS[entry.name] || '#3B82F6'} />
                  ))}
                </Pie>
                <RechartsTooltip content={<CustomTooltip />} />
              </PieChart>
            </ResponsiveContainer>
          </div>

          {/* Legend */}
          <div className="flex items-center justify-center gap-4 text-[11px] font-mono text-[#94A3B8] pt-1 border-t border-[#293545]">
            <span className="flex items-center gap-1.5">
              <span className="w-2 h-2 rounded-full bg-[#34D399]" /> Small ({pieData.find(p=>p.name==='SMALL')?.value || 0})
            </span>
            <span className="flex items-center gap-1.5">
              <span className="w-2 h-2 rounded-full bg-amber-400" /> Medium ({pieData.find(p=>p.name==='MEDIUM')?.value || 0})
            </span>
            <span className="flex items-center gap-1.5">
              <span className="w-2 h-2 rounded-full bg-indigo-400" /> Large ({pieData.find(p=>p.name==='LARGE')?.value || 0})
            </span>
          </div>
        </div>

        {/* Chart 2: Cost Comparison */}
        <div className="bg-[#121923] border border-[#293545] rounded-md p-4 flex flex-col justify-between h-72">
          <div className="flex items-center justify-between border-b border-[#293545] pb-2">
            <div className="flex items-center gap-1.5">
              <TrendingDown className="w-3.5 h-3.5 text-[#34D399]" />
              <span className="text-[11px] font-mono font-semibold uppercase tracking-wider text-[#F1F5F9]">
                Mean Inference Cost ($)
              </span>
            </div>
            <span className="text-[10px] font-mono text-[#34D399] font-semibold">-{costSavingsPct}%</span>
          </div>

          <div className="h-52 w-full pt-2">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={costData} margin={{ top: 10, right: 10, left: -15, bottom: 0 }}>
                <CartesianGrid strokeDasharray="2 2" stroke="#293545" vertical={false} />
                <XAxis dataKey="name" stroke="#293545" tick={{ fill: '#94A3B8', fontSize: 10, fontFamily: 'monospace' }} />
                <YAxis stroke="#293545" tick={{ fill: '#94A3B8', fontSize: 10, fontFamily: 'monospace' }} />
                <RechartsTooltip content={<CustomTooltip />} />
                <Bar dataKey="cost" fill="#3B82F6" radius={[2, 2, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Chart 3: Latency Comparison */}
        <div className="bg-[#121923] border border-[#293545] rounded-md p-4 flex flex-col justify-between h-72">
          <div className="flex items-center justify-between border-b border-[#293545] pb-2">
            <div className="flex items-center gap-1.5">
              <Clock className="w-3.5 h-3.5 text-amber-400" />
              <span className="text-[11px] font-mono font-semibold uppercase tracking-wider text-[#F1F5F9]">
                Mean Latency (Seconds)
              </span>
            </div>
            <span className="text-[10px] font-mono text-amber-400 font-semibold">-{latencyReductionPct}%</span>
          </div>

          <div className="h-52 w-full pt-2">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={latencyData} margin={{ top: 10, right: 10, left: -15, bottom: 0 }}>
                <CartesianGrid strokeDasharray="2 2" stroke="#293545" vertical={false} />
                <XAxis dataKey="name" stroke="#293545" tick={{ fill: '#94A3B8', fontSize: 10, fontFamily: 'monospace' }} />
                <YAxis stroke="#293545" tick={{ fill: '#94A3B8', fontSize: 10, fontFamily: 'monospace' }} />
                <RechartsTooltip content={<CustomTooltip />} />
                <Bar dataKey="latency" fill="#F59E0B" radius={[2, 2, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>

      {/* Observability Protocol Notice */}
      <div className="bg-[#121923] border border-[#293545] rounded-md p-4 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 text-xs font-mono text-[#94A3B8]">
        <div className="flex items-center gap-2.5">
          <CheckCircle className="w-4 h-4 text-[#34D399] flex-shrink-0" />
          <span>
            <strong className="text-[#F1F5F9]">Data Integrity Protocol:</strong> Offline classifier evaluation is performed on held-out test splits. Live inference is powered by configured provider tiers.
          </span>
        </div>
        <Link
          to="/research"
          className="text-[#3B82F6] hover:text-blue-400 font-semibold shrink-0 flex items-center gap-1"
        >
          <span>View Research Benchmarks</span>
          <ArrowRight className="w-3 h-3" />
        </Link>
      </div>
    </div>
  );
}
