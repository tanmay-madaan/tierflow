import React, { useState, useEffect } from 'react';
import { api } from '../services/api';
import { ModelBadge } from '../components/ModelBadge';
import { Search, ChevronDown, ChevronUp, Clock, Copy, Check, Filter } from 'lucide-react';

export default function Experiments() {
  const [experiments, setExperiments] = useState([]);
  const [loading, setLoading] = useState(true);
  const [expandedId, setExpandedId] = useState(null);
  const [search, setSearch] = useState('');
  const [tierFilter, setTierFilter] = useState('ALL');
  const [copiedId, setCopiedId] = useState(null);

  useEffect(() => {
    const fetchExp = async () => {
      setLoading(true);
      const data = await api.getExperiments(100);
      setExperiments(data || []);
      setLoading(false);
    };
    fetchExp();
  }, []);

  const handleCopy = (id, text) => {
    navigator.clipboard.writeText(text);
    setCopiedId(id);
    setTimeout(() => setCopiedId(null), 2000);
  };

  const filtered = experiments.filter((exp) => {
    const matchesSearch =
      (exp.query || '').toLowerCase().includes(search.toLowerCase()) ||
      (exp.selected_model || '').toLowerCase().includes(search.toLowerCase()) ||
      (exp.response || '').toLowerCase().includes(search.toLowerCase());
    const matchesTier = tierFilter === 'ALL' || exp.selected_model === tierFilter;
    return matchesSearch && matchesTier;
  });

  return (
    <div className="p-6 md:p-8 max-w-7xl mx-auto space-y-6 pb-24 h-full overflow-y-auto">
      {/* Page Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-4 border-b border-[#293545]">
        <div>
          <div className="flex items-center gap-2.5 mb-1">
            <h1 className="text-xl font-bold tracking-tight text-[#F1F5F9]">
              TIERFLOW <span className="text-[#3B82F6] font-medium">Experiment Log</span>
            </h1>
            <span className="text-[10px] font-mono uppercase px-2 py-0.5 rounded bg-[#1A2431] text-[#94A3B8] border border-[#293545]">
              Audit Trace
            </span>
          </div>
          <p className="text-xs text-[#94A3B8]">
            Route smarter. Measure everything. Immutable trace of routed requests, classifier predictions, generated outputs, and telemetry.
          </p>
        </div>

        {/* Search & Filter Toolbar */}
        <div className="flex items-center gap-2">
          {/* Tier Filter */}
          <select
            value={tierFilter}
            onChange={(e) => setTierFilter(e.target.value)}
            className="bg-[#121923] border border-[#293545] rounded-md px-2.5 py-1.5 text-xs font-mono text-[#F1F5F9] focus:outline-none focus:border-[#3B82F6] transition-colors"
          >
            <option value="ALL">All Tiers</option>
            <option value="SMALL">Small Tier</option>
            <option value="MEDIUM">Medium Tier</option>
            <option value="LARGE">Large Tier</option>
          </select>

          {/* Search Box */}
          <div className="relative w-64">
            <Search className="absolute left-2.5 top-1/2 -translate-y-1/2 w-3.5 h-3.5 text-[#94A3B8]" />
            <input 
              type="text" 
              placeholder="Filter by query or output..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              className="w-full bg-[#121923] border border-[#293545] rounded-md pl-8 pr-3 py-1.5 text-xs font-sans text-[#F1F5F9] placeholder:text-neutral-600 focus:outline-none focus:border-[#3B82F6] transition-colors"
            />
          </div>
        </div>
      </div>

      {/* Table Container */}
      <div className="bg-[#121923] border border-[#293545] rounded-md overflow-hidden">
        {/* Table summary bar */}
        <div className="px-4 py-2 bg-[#0E141C] border-b border-[#293545] flex items-center justify-between text-[11px] font-mono text-[#94A3B8]">
          <span>Showing {filtered.length} of {experiments.length} logged queries</span>
          <span className="text-[10px] text-[#94A3B8]/60">Sorted by most recent</span>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs font-mono border-collapse">
            <thead className="bg-[#0E141C] text-[#94A3B8] border-b border-[#293545] text-[10px] uppercase tracking-wider">
              <tr>
                <th className="px-4 py-3 w-12 text-center">#</th>
                <th className="px-4 py-3 w-24">Mode</th>
                <th className="px-4 py-3">Query</th>
                <th className="px-4 py-3 w-28">Tier</th>
                <th className="px-4 py-3 w-24">Complexity</th>
                <th className="px-4 py-3 text-right w-24">Latency</th>
                <th className="px-4 py-3 text-right w-28">Cost (Est.)</th>
                <th className="px-4 py-3 text-right w-24">Quality</th>
                <th className="px-4 py-3 w-10"></th>
              </tr>
            </thead>
            <tbody className="divide-y divide-[#293545]">
              {loading ? (
                <tr>
                  <td colSpan="9" className="px-4 py-12 text-center text-[#94A3B8]">
                    <div className="flex justify-center mb-2">
                      <div className="w-5 h-5 border-2 border-[#3B82F6] border-t-transparent rounded-full animate-spin" />
                    </div>
                    <span>Loading experiment records...</span>
                  </td>
                </tr>
              ) : filtered.length === 0 ? (
                <tr>
                  <td colSpan="9" className="px-4 py-12 text-center text-[#94A3B8] font-sans text-xs">
                    No matching experiments found in database.
                  </td>
                </tr>
              ) : (
                filtered.map((exp, idx) => {
                  const isExpanded = expandedId === exp.id;
                  const isRealMode = exp.execution_mode === 'real' || (!exp.demo_mode && exp.execution_mode !== 'demo');
                  return (
                    <React.Fragment key={exp.id || idx}>
                      <tr 
                        className={`hover:bg-[#1A2431]/60 cursor-pointer transition-colors ${isExpanded ? 'bg-[#1A2431]/60' : ''}`}
                        onClick={() => setExpandedId(isExpanded ? null : exp.id)}
                      >
                        <td className="px-4 py-3 text-[#94A3B8] text-center text-[11px] tabular-nums">
                          {idx + 1}
                        </td>
                        <td className="px-4 py-3">
                          <span className={`inline-flex items-center gap-1 text-[9px] font-mono uppercase px-1.5 py-0.5 rounded border ${
                            isRealMode
                              ? 'bg-[#34D399]/15 text-[#34D399] border-[#34D399]/30'
                              : 'bg-[#1A2431] text-[#94A3B8] border-[#293545]'
                          }`}>
                            <span className={`w-1 h-1 rounded-full ${isRealMode ? 'bg-[#34D399]' : 'bg-[#94A3B8]'}`} />
                            {isRealMode ? 'Live' : 'Demo'}
                          </span>
                        </td>
                        <td className="px-4 py-3 font-sans text-[#F1F5F9] truncate max-w-sm">
                          {exp.query}
                        </td>
                        <td className="px-4 py-3">
                          <ModelBadge model={exp.selected_model} />
                        </td>
                        <td className="px-4 py-3 text-[#94A3B8] uppercase text-[11px]">
                          {exp.complexity || 'LOW'}
                        </td>
                        <td className="px-4 py-3 text-right text-[#F1F5F9] tabular-nums">
                          {exp.latency != null ? `${exp.latency.toFixed(2)}s` : '—'}
                        </td>
                        <td className="px-4 py-3 text-right text-[#F1F5F9] tabular-nums">
                          {exp.estimated_cost != null ? `$${exp.estimated_cost.toFixed(5)}` : '—'}
                        </td>
                        <td className="px-4 py-3 text-right tabular-nums">
                          <span className="text-[#F1F5F9] font-semibold">
                            {exp.quality_score != null ? `${exp.quality_score.toFixed(1)}/10` : '—'}
                          </span>
                        </td>
                        <td className="px-4 py-3 text-[#94A3B8] text-center">
                          {isExpanded ? <ChevronUp className="w-3.5 h-3.5" /> : <ChevronDown className="w-3.5 h-3.5" />}
                        </td>
                      </tr>

                      {/* Expanded Detail Panel */}
                      {isExpanded && (
                        <tr className="bg-[#0E141C] border-b border-[#293545]">
                          <td colSpan="9" className="p-5">
                            <div className="grid grid-cols-1 lg:grid-cols-2 gap-4 mb-4">
                              {/* Full Query */}
                              <div className="space-y-1.5">
                                <div className="flex items-center justify-between text-[11px] font-mono text-[#94A3B8]">
                                  <span>FULL PROMPT / QUERY</span>
                                  <button
                                    type="button"
                                    onClick={(e) => {
                                      e.stopPropagation();
                                      handleCopy(`q-${exp.id}`, exp.query);
                                    }}
                                    className="flex items-center gap-1 hover:text-[#F1F5F9]"
                                  >
                                    {copiedId === `q-${exp.id}` ? <Check className="w-3 h-3 text-[#34D399]" /> : <Copy className="w-3 h-3" />}
                                    <span>{copiedId === `q-${exp.id}` ? 'Copied' : 'Copy'}</span>
                                  </button>
                                </div>
                                <div className="bg-[#121923] border border-[#293545] rounded-md p-3.5 text-xs text-[#F1F5F9] font-sans leading-relaxed whitespace-pre-wrap select-text">
                                  {exp.query}
                                </div>
                              </div>

                              {/* Generated Response */}
                              <div className="space-y-1.5">
                                <div className="flex items-center justify-between text-[11px] font-mono text-[#94A3B8]">
                                  <span>GENERATED OUTPUT</span>
                                  <button
                                    type="button"
                                    onClick={(e) => {
                                      e.stopPropagation();
                                      handleCopy(`r-${exp.id}`, exp.response);
                                    }}
                                    className="flex items-center gap-1 hover:text-[#F1F5F9]"
                                  >
                                    {copiedId === `r-${exp.id}` ? <Check className="w-3 h-3 text-[#34D399]" /> : <Copy className="w-3 h-3" />}
                                    <span>{copiedId === `r-${exp.id}` ? 'Copied' : 'Copy'}</span>
                                  </button>
                                </div>
                                <div className="bg-[#121923] border border-[#293545] rounded-md p-3.5 text-xs text-[#F1F5F9] font-sans leading-relaxed whitespace-pre-wrap max-h-48 overflow-y-auto select-text">
                                  {exp.response || '(No response captured)'}
                                </div>
                              </div>
                            </div>

                            {/* Telemetry metadata footer */}
                            <div className="pt-3 border-t border-[#293545] flex flex-wrap items-center justify-between gap-4 text-[11px] font-mono text-[#94A3B8]">
                              <div className="flex items-center gap-4">
                                <span>Timestamp: <strong className="text-[#F1F5F9]">{exp.timestamp ? new Date(exp.timestamp).toLocaleString() : 'N/A'}</strong></span>
                                <span>Confidence: <strong className="text-[#F1F5F9]">{exp.confidence != null ? `${(exp.confidence * 100).toFixed(1)}%` : '—'}</strong></span>
                                <span>Mode: <strong className="text-[#F1F5F9]">{isRealMode ? 'Live Provider Inference' : 'Simulated Template (Demo)'}</strong></span>
                              </div>
                              <div className="flex items-center gap-3">
                                <span>Baseline Latency: {exp.baseline_latency != null ? `${exp.baseline_latency.toFixed(2)}s` : '—'}</span>
                                <span>Baseline Cost: {exp.baseline_cost != null ? `$${exp.baseline_cost.toFixed(5)}` : '—'}</span>
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
