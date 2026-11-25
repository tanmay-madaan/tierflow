import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { api } from '../services/api';
import { ModelBadge } from '../components/ModelBadge';
import { ExecutionModeBadge } from '../components/ExecutionModeBadge';
import { EmptyState } from '../components/EmptyState';
import { 
  Search, 
  ChevronDown, 
  ChevronUp, 
  Clock, 
  Copy, 
  Check, 
  Filter, 
  RefreshCw, 
  AlertCircle, 
  CheckCircle2, 
  Calendar,
  Layers,
  Database,
  ArrowUpDown,
  Info
} from 'lucide-react';

export default function Experiments() {
  const [experiments, setExperiments] = useState([]);
  const [loading, setLoading] = useState(true);
  const [expandedId, setExpandedId] = useState(null);
  const [search, setSearch] = useState('');
  const [tierFilter, setTierFilter] = useState('ALL');
  const [modeFilter, setModeFilter] = useState('ALL');
  const [statusFilter, setStatusFilter] = useState('ALL');
  const [copiedId, setCopiedId] = useState(null);

  useEffect(() => {
    fetchExperiments();
  }, []);

  const fetchExperiments = async () => {
    setLoading(true);
    try {
      const data = await api.getExperiments(200);
      setExperiments(data || []);
    } catch (err) {
      console.warn("Failed to load experiments:", err);
      setExperiments([]);
    } finally {
      setLoading(false);
    }
  };

  const handleCopy = (id, text) => {
    navigator.clipboard.writeText(text);
    setCopiedId(id);
    setTimeout(() => setCopiedId(null), 2000);
  };

  // Summary statistics computed directly from loaded experiments
  const totalCount = experiments.length;
  const realCount = experiments.filter(e => e.execution_mode === 'real' || (!e.demo_mode && e.execution_mode !== 'demo')).length;
  const demoCount = experiments.filter(e => e.execution_mode === 'demo' || e.demo_mode === true).length;
  const failedCount = experiments.filter(e => Boolean(e.error)).length;
  const successCount = totalCount - failedCount;

  // Multi-criteria filtering
  const filtered = experiments.filter((exp) => {
    const isReal = exp.execution_mode === 'real' || (!exp.demo_mode && exp.execution_mode !== 'demo');
    const isFailed = Boolean(exp.error);

    // Search query matches
    const qStr = (exp.query || '').toLowerCase();
    const modelStr = (exp.selected_model || '').toLowerCase();
    const respStr = (exp.response || '').toLowerCase();
    const sTerm = search.toLowerCase();
    const matchesSearch = !search || qStr.includes(sTerm) || modelStr.includes(sTerm) || respStr.includes(sTerm);

    // Tier matches
    const matchesTier = tierFilter === 'ALL' || (exp.selected_model || '').toUpperCase() === tierFilter;

    // Mode matches
    const matchesMode = modeFilter === 'ALL' || (modeFilter === 'REAL' ? isReal : !isReal);

    // Status matches
    const matchesStatus = statusFilter === 'ALL' || (statusFilter === 'SUCCESS' ? !isFailed : isFailed);

    return matchesSearch && matchesTier && matchesMode && matchesStatus;
  });

  return (
    <div className="p-4 sm:p-6 lg:p-8 max-w-7xl mx-auto space-y-6 pb-24">
      {/* ── Page Header ────────────────────────────────────────────── */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-4 border-b border-[#263548]">
        <div>
          <div className="flex items-center gap-2.5 mb-1">
            <h1 className="text-xl font-bold tracking-tight text-[#F1F5F9]">
              TIERFLOW <span className="text-[#3B82F6] font-medium">Live Request Log</span>
            </h1>
            <span className="text-[10px] font-mono uppercase px-2 py-0.5 rounded bg-[#192536] text-[#A0AEC0] border border-[#263548]">
              Session Audit Trace
            </span>
          </div>
          <p className="text-xs text-[#A0AEC0] font-sans">
            Audit record of individual interactive Playground queries &amp; real-time API requests. For batch benchmark suites, see{' '}
            <Link to="/research" className="text-[#3B82F6] hover:underline">
              Research &amp; Benchmark
            </Link>.
          </p>
        </div>

        <button
          onClick={fetchExperiments}
          disabled={loading}
          className="flex items-center gap-1.5 px-3 py-1.5 rounded-md text-xs font-mono font-medium text-[#A0AEC0] bg-[#141E2A] hover:bg-[#192536] hover:text-[#F1F5F9] border border-[#263548] transition-colors shrink-0 self-start sm:self-auto"
        >
          <RefreshCw className={`w-3.5 h-3.5 ${loading ? 'animate-spin' : ''}`} />
          <span>Refresh</span>
        </button>
      </div>

      {/* ── Scope Disclaimer Banner ─────────────────────────────────── */}
      <div className="bg-[#101722] border border-[#263548] rounded-md p-3 text-xs font-mono flex items-center justify-between gap-3">
        <div className="flex items-center gap-2 text-[#A0AEC0]">
          <Info className="w-4 h-4 text-[#3B82F6] shrink-0" />
          <span>
            <strong className="text-[#F1F5F9]">Scope Notice:</strong> This audit log records individual queries submitted through the Playground or API. It does not represent full 200-prompt batch benchmark evaluations. For comprehensive cross-policy analysis and empirical test suites, view <Link to="/research" className="text-[#3B82F6] underline">Research &amp; Benchmark</Link>.
          </span>
        </div>
      </div>

      {/* ── Summary Counters Strip ─────────────────────────────────── */}
      <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-5 gap-3 text-xs font-mono">
        <div className="bg-[#141E2A] border border-[#263548] rounded-md p-3">
          <span className="text-[10px] text-[#718096] uppercase tracking-wider block mb-1">Total Logged</span>
          <span className="text-xl font-semibold text-[#F1F5F9]">{totalCount}</span>
        </div>
        <div className="bg-[#141E2A] border border-[#263548] rounded-md p-3">
          <span className="text-[10px] text-[#718096] uppercase tracking-wider block mb-1">Live Provider</span>
          <span className="text-xl font-semibold text-[#34D399]">{realCount}</span>
        </div>
        <div className="bg-[#141E2A] border border-[#263548] rounded-md p-3">
          <span className="text-[10px] text-[#718096] uppercase tracking-wider block mb-1">Simulated Demo</span>
          <span className="text-xl font-semibold text-[#3B82F6]">{demoCount}</span>
        </div>
        <div className="bg-[#141E2A] border border-[#263548] rounded-md p-3">
          <span className="text-[10px] text-[#718096] uppercase tracking-wider block mb-1">Successful</span>
          <span className="text-xl font-semibold text-[#F1F5F9]">{successCount}</span>
        </div>
        <div className="bg-[#141E2A] border border-[#263548] rounded-md p-3 col-span-2 sm:col-span-1">
          <span className="text-[10px] text-[#718096] uppercase tracking-wider block mb-1">Failed / Errors</span>
          <span className={`text-xl font-semibold ${failedCount > 0 ? 'text-[#EF4444]' : 'text-[#718096]'}`}>
            {failedCount}
          </span>
        </div>
      </div>

      {/* ── Search & Multi-Filter Bar ──────────────────────────────── */}
      <div className="bg-[#141E2A] border border-[#263548] rounded-md p-3.5 flex flex-col md:flex-row items-stretch md:items-center justify-between gap-3 text-xs font-mono">
        {/* Search Input */}
        <div className="relative flex-1">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-3.5 h-3.5 text-[#718096]" />
          <input
            type="text"
            placeholder="Search queries, models, or responses..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="w-full bg-[#0D141D] border border-[#263548] rounded-md pl-9 pr-3 py-1.5 text-xs font-sans text-[#F1F5F9] placeholder:text-[#718096] focus:outline-none focus:border-[#3B82F6] transition-colors"
          />
        </div>

        {/* Dropdown Filters */}
        <div className="flex flex-wrap items-center gap-2">
          {/* Tier Filter */}
          <select
            value={tierFilter}
            onChange={(e) => setTierFilter(e.target.value)}
            className="bg-[#0D141D] border border-[#263548] rounded-md px-2.5 py-1.5 text-xs font-mono text-[#F1F5F9] focus:outline-none focus:border-[#3B82F6] transition-colors"
          >
            <option value="ALL">All Tiers</option>
            <option value="SMALL">Small Tier</option>
            <option value="MEDIUM">Medium Tier</option>
            <option value="LARGE">Large Tier</option>
          </select>

          {/* Mode Filter */}
          <select
            value={modeFilter}
            onChange={(e) => setModeFilter(e.target.value)}
            className="bg-[#0D141D] border border-[#263548] rounded-md px-2.5 py-1.5 text-xs font-mono text-[#F1F5F9] focus:outline-none focus:border-[#3B82F6] transition-colors"
          >
            <option value="ALL">All Modes</option>
            <option value="REAL">Live API Only</option>
            <option value="DEMO">Demo Mode Only</option>
          </select>

          {/* Status Filter */}
          <select
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value)}
            className="bg-[#0D141D] border border-[#263548] rounded-md px-2.5 py-1.5 text-xs font-mono text-[#F1F5F9] focus:outline-none focus:border-[#3B82F6] transition-colors"
          >
            <option value="ALL">All Statuses</option>
            <option value="SUCCESS">Success Only</option>
            <option value="FAILED">Errors Only</option>
          </select>
        </div>
      </div>

      {/* ── Table Container ────────────────────────────────────────── */}
      <div className="bg-[#141E2A] border border-[#263548] rounded-md overflow-hidden">
        {/* Table summary bar */}
        <div className="px-4 py-2.5 bg-[#101722] border-b border-[#263548] flex items-center justify-between text-[11px] font-mono text-[#A0AEC0]">
          <span>Showing <strong className="text-[#F1F5F9]">{filtered.length}</strong> of {totalCount} records</span>
          <span className="text-[10px] text-[#718096]">Sorted by newest first</span>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs font-mono border-collapse min-w-[760px]">
            <thead className="bg-[#101722] text-[#A0AEC0] border-b border-[#263548] text-[10px] uppercase tracking-wider">
              <tr>
                <th className="px-4 py-3 w-12 text-center">#</th>
                <th className="px-4 py-3 w-28">Mode</th>
                <th className="px-4 py-3">Prompt / Query</th>
                <th className="px-4 py-3 w-24">Tier</th>
                <th className="px-4 py-3 w-24">Complexity</th>
                <th className="px-4 py-3 text-right w-24">Latency</th>
                <th className="px-4 py-3 text-right w-28">Cost</th>
                <th className="px-4 py-3 text-right w-20">Quality</th>
                <th className="px-4 py-3 text-center w-24">Status</th>
                <th className="px-4 py-3 w-10"></th>
              </tr>
            </thead>
            <tbody className="divide-y divide-[#263548]">
              {loading ? (
                <tr>
                  <td colSpan="10" className="px-4 py-16 text-center text-[#718096]">
                    <div className="flex justify-center mb-2">
                      <div className="w-5 h-5 border-2 border-[#3B82F6] border-t-transparent rounded-full animate-spin" />
                    </div>
                    <span>Loading experiment records...</span>
                  </td>
                </tr>
              ) : filtered.length === 0 ? (
                <tr>
                  <td colSpan="10" className="p-8">
                    <EmptyState
                      title="No Matching Experiments"
                      message="No records matched the selected query, tier, mode, or status filters."
                      className="border-none bg-transparent"
                    />
                  </td>
                </tr>
              ) : (
                filtered.map((exp, idx) => {
                  const isExpanded = expandedId === (exp.id || idx);
                  const isRealMode = exp.execution_mode === 'real' || (!exp.demo_mode && exp.execution_mode !== 'demo');
                  const hasError = Boolean(exp.error);

                  return (
                    <React.Fragment key={exp.id || idx}>
                      <tr 
                        className={`hover:bg-[#192536]/70 cursor-pointer transition-colors ${isExpanded ? 'bg-[#192536]' : ''}`}
                        onClick={() => setExpandedId(isExpanded ? null : (exp.id || idx))}
                      >
                        <td className="px-4 py-3 text-[#718096] text-center text-[11px] tabular-nums">
                          {idx + 1}
                        </td>
                        <td className="px-4 py-3">
                          <ExecutionModeBadge mode={exp.execution_mode || (exp.demo_mode ? 'demo' : 'real')} />
                        </td>
                        <td className="px-4 py-3 font-sans text-[#F1F5F9] truncate max-w-xs sm:max-w-md">
                          {exp.query}
                        </td>
                        <td className="px-4 py-3">
                          <ModelBadge model={exp.selected_model} />
                        </td>
                        <td className="px-4 py-3 text-[#A0AEC0] uppercase text-[11px]">
                          {exp.complexity || 'LOW'}
                        </td>
                        <td className="px-4 py-3 text-right text-[#F1F5F9] tabular-nums">
                          {exp.latency != null ? `${exp.latency.toFixed(3)}s` : 'N/A'}
                        </td>
                        <td className="px-4 py-3 text-right text-[#F1F5F9] tabular-nums">
                          {exp.estimated_cost != null ? `$${exp.estimated_cost.toFixed(5)}` : 'N/A'}
                        </td>
                        <td className="px-4 py-3 text-right tabular-nums">
                          <span className="text-[#F1F5F9] font-semibold">
                            {exp.quality_score != null ? `${exp.quality_score.toFixed(1)}/10` : 'N/A'}
                          </span>
                        </td>
                        <td className="px-4 py-3 text-center">
                          {hasError ? (
                            <span className="inline-flex items-center gap-1 text-[10px] text-[#EF4444] font-semibold">
                              <AlertCircle className="w-3 h-3" /> Error
                            </span>
                          ) : (
                            <span className="inline-flex items-center gap-1 text-[10px] text-[#34D399]">
                              <CheckCircle2 className="w-3 h-3" /> OK
                            </span>
                          )}
                        </td>
                        <td className="px-4 py-3 text-[#718096] text-center">
                          {isExpanded ? <ChevronUp className="w-3.5 h-3.5 text-[#3B82F6]" /> : <ChevronDown className="w-3.5 h-3.5" />}
                        </td>
                      </tr>

                      {/* ── Expanded Detail Panel ──────────────────────────── */}
                      {isExpanded && (
                        <tr className="bg-[#101722] border-b border-[#263548]">
                          <td colSpan="10" className="p-5">
                            <div className="space-y-4">
                              {/* Metadata Strip */}
                              <div className="grid grid-cols-2 sm:grid-cols-4 lg:grid-cols-6 gap-3 text-xs font-mono bg-[#141E2A] p-3 rounded border border-[#263548]">
                                <div>
                                  <span className="text-[10px] text-[#718096] uppercase block">Record ID</span>
                                  <span className="font-semibold text-[#F1F5F9] text-[11px] truncate block">
                                    {exp.id ? `exp_${exp.id}` : 'session_query'}
                                  </span>
                                </div>
                                <div>
                                  <span className="text-[10px] text-[#718096] uppercase block">Execution Mode</span>
                                  <ExecutionModeBadge mode={exp.execution_mode || (exp.demo_mode ? 'demo' : 'real')} />
                                </div>
                                <div>
                                  <span className="text-[10px] text-[#718096] uppercase block">Model ID</span>
                                  <span className="font-semibold text-[#F1F5F9] text-[11px] truncate block" title={exp.model_id}>
                                    {exp.model_id || exp.selected_model || 'N/A'}
                                  </span>
                                </div>
                                <div>
                                  <span className="text-[10px] text-[#718096] uppercase block">Confidence</span>
                                  <span className="font-semibold text-[#F1F5F9] tabular-nums">
                                    {exp.confidence != null ? `${(exp.confidence * 100).toFixed(1)}%` : 'N/A'}
                                  </span>
                                </div>
                                <div>
                                  <span className="text-[10px] text-[#718096] uppercase block">Token Usage</span>
                                  <span className="font-semibold text-[#F1F5F9] text-[11px] tabular-nums">
                                    {(exp.prompt_tokens || 0) + (exp.completion_tokens || 0) > 0
                                      ? `${(exp.prompt_tokens || 0) + (exp.completion_tokens || 0)} (${exp.prompt_tokens || 0} in / ${exp.completion_tokens || 0} out)`
                                      : 'N/A'}
                                  </span>
                                </div>
                                <div>
                                  <span className="text-[10px] text-[#718096] uppercase block">Timestamp</span>
                                  <span className="text-[#A0AEC0] text-[10px] truncate block">
                                    {exp.timestamp ? new Date(exp.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' }) : 'N/A'}
                                  </span>
                                </div>
                              </div>

                              {/* Error display if present */}
                              {hasError && (
                                <div className="bg-red-950/30 border border-red-800/60 rounded p-3 text-xs text-red-300 font-mono space-y-1">
                                  <span className="font-semibold text-red-200 uppercase text-[10px] block">Error Details:</span>
                                  <p>{typeof exp.error === 'string' ? exp.error : JSON.stringify(exp.error)}</p>
                                </div>
                              )}

                              {/* Prompt & Response Boxes */}
                              <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
                                {/* Full Prompt */}
                                <div className="space-y-1.5">
                                  <div className="flex items-center justify-between text-[11px] font-mono text-[#A0AEC0]">
                                    <span>FULL PROMPT / QUERY</span>
                                    <button
                                      type="button"
                                      onClick={(e) => {
                                        e.stopPropagation();
                                        handleCopy(`q-${exp.id || idx}`, exp.query);
                                      }}
                                      className="flex items-center gap-1 hover:text-[#F1F5F9] transition-colors"
                                    >
                                      {copiedId === `q-${exp.id || idx}` ? <Check className="w-3 h-3 text-[#34D399]" /> : <Copy className="w-3 h-3" />}
                                      <span>{copiedId === `q-${exp.id || idx}` ? 'Copied' : 'Copy'}</span>
                                    </button>
                                  </div>
                                  <div className="bg-[#0D141D] border border-[#263548] rounded-md p-3.5 text-xs text-[#F1F5F9] font-sans leading-relaxed whitespace-pre-wrap select-text max-h-56 overflow-y-auto">
                                    {exp.query}
                                  </div>
                                </div>

                                {/* Generated Response */}
                                <div className="space-y-1.5">
                                  <div className="flex items-center justify-between text-[11px] font-mono text-[#A0AEC0]">
                                    <span>GENERATED MODEL OUTPUT</span>
                                    {exp.response && (
                                      <button
                                        type="button"
                                        onClick={(e) => {
                                          e.stopPropagation();
                                          handleCopy(`r-${exp.id || idx}`, exp.response);
                                        }}
                                        className="flex items-center gap-1 hover:text-[#F1F5F9] transition-colors"
                                      >
                                        {copiedId === `r-${exp.id || idx}` ? <Check className="w-3 h-3 text-[#34D399]" /> : <Copy className="w-3 h-3" />}
                                        <span>{copiedId === `r-${exp.id || idx}` ? 'Copied' : 'Copy'}</span>
                                      </button>
                                    )}
                                  </div>
                                  <div className="bg-[#0D141D] border border-[#263548] rounded-md p-3.5 text-xs text-[#F1F5F9] font-sans leading-relaxed whitespace-pre-wrap max-h-56 overflow-y-auto select-text">
                                    {exp.response || <span className="text-[#718096] italic">(No response output captured)</span>}
                                  </div>
                                </div>
                              </div>
                            </div>
                          </td>
                        </tr>
                      )}
                    </React.Fragment>
                  );
                })
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
