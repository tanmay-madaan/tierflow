import React, { useState, useEffect, useRef } from 'react';
import { Send, RefreshCw, AlertCircle, Zap, Brain, Shield, ChevronRight, Info, CheckCircle, Sparkles, Key, AlertTriangle, Copy, Check } from 'lucide-react';
import { api } from '../services/api';
import { ModelBadge } from '../components/ModelBadge';

const TIER_INFO = {
  SMALL: {
    label: 'Small Model',
    color: '#34D399',
    description: 'Ultra-fast, lowest latency & cost. Ideal for factual queries, simple definitions, and direct lookups.',
    examples: ['What is the capital of India?', 'What is the capital of Japan?', 'Define supervised learning.'],
  },
  MEDIUM: {
    label: 'Medium Model',
    color: '#F59E0B',
    description: 'Balanced throughput and reasoning. Handles explanations, comparisons, trade-off analysis, and code synthesis.',
    examples: [
      'Why does gradient descent sometimes fail to converge?',
      'Explain the difference between TCP and UDP protocols.',
      'Write a Python function to check if a string is a palindrome.',
    ],
  },
  LARGE: {
    label: 'Large Model',
    color: '#6366F1',
    description: 'Deep multi-step reasoning, architectural system design, formal proofs, and complex algorithmic constraints.',
    examples: [
      'Design a machine learning pipeline for detecting fraudulent transactions with severe class imbalance.',
      'Prove that there are infinitely many prime numbers using a rigorous mathematical argument.',
    ],
  },
};

const SAMPLE_QUERIES = [
  { tag: 'QA', label: 'Capital QA', query: 'What is the capital of India?' },
  { tag: 'Factual', label: 'Definition', query: 'Define supervised learning in machine learning.' },
  { tag: 'Reasoning', label: 'Optimization', query: 'Why does gradient descent sometimes fail to converge?' },
  { tag: 'Networking', label: 'TCP vs UDP', query: 'Explain the difference between TCP and UDP protocols.' },
  { tag: 'Coding', label: 'Python Palindrome', query: 'Write a Python function to check if a string is a palindrome.' },
  { tag: 'Design', label: 'Fraud Detection Pipeline', query: 'Design a machine learning pipeline for detecting fraudulent transactions with severe class imbalance and explain how you would evaluate it.' },
];

function ProbabilityBar({ model, prob }) {
  const colors = { SMALL: 'bg-[#34D399]', MEDIUM: 'bg-amber-400', LARGE: 'bg-indigo-400' };
  return (
    <div>
      <div className="flex justify-between items-center text-xs mb-1 font-mono">
        <span className="text-[#94A3B8] uppercase text-[11px]">{model}</span>
        <span className="text-[#F1F5F9] font-semibold tabular-nums">{(prob * 100).toFixed(1)}%</span>
      </div>
      <div className="w-full bg-[#0E141C] border border-[#293545] rounded h-1.5 overflow-hidden">
        <div
          className={`h-full rounded transition-all duration-300 ${colors[model] || 'bg-[#3B82F6]'}`}
          style={{ width: `${Math.max(2, prob * 100)}%` }}
        />
      </div>
    </div>
  );
}

export default function RouterPlayground() {
  const [query, setQuery] = useState('');
  const [executionMode, setExecutionMode] = useState('real'); // 'real' or 'demo'
  const [backendHealth, setBackendHealth] = useState(null);
  const [routingResult, setRoutingResult] = useState(null);   // from /route
  const [fullResult, setFullResult] = useState(null);          // from /query
  const [routingLoading, setRoutingLoading] = useState(false);
  const [fullLoading, setFullLoading] = useState(false);
  const [error, setError] = useState(null);
  const [copied, setCopied] = useState(false);

  const textareaRef = useRef(null);
  const resultsRef = useRef(null);

  useEffect(() => {
    api.getHealth().then(data => {
      if (data) {
        setBackendHealth(data);
        // Default to real mode only if server has API key configured; otherwise default to demo mode
        setExecutionMode(data.has_api_key ? 'real' : 'demo');
      }
    });
  }, []);

  useEffect(() => {
    if (routingResult || fullResult) {
      setTimeout(() => {
        resultsRef.current?.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
      }, 50);
    }
  }, [routingResult, fullResult]);

  const handleRouteOnly = async (e) => {
    e?.preventDefault();
    const q = query.trim();
    if (!q) return;
    setError(null);
    setRoutingResult(null);
    setFullResult(null);
    setRoutingLoading(true);
    try {
      const data = await api.routeQuery(q);
      setRoutingResult(data);
    } catch (err) {
      setError(err.message || 'Failed to route query.');
    } finally {
      setRoutingLoading(false);
    }
  };

  const handleAskAndRoute = async (modeOverride = null) => {
    const q = query.trim();
    if (!q) return;
    const mode = modeOverride || executionMode;
    setError(null);
    setFullLoading(true);
    setFullResult(null);
    try {
      try {
        const routeData = await api.routeQuery(q);
        if (routeData) setRoutingResult(routeData);
      } catch (rErr) {
        console.warn("Pre-route call failed, proceeding to query:", rErr);
      }

      const isDemo = (mode === 'demo');
      const data = await api.queryModel(q, isDemo, mode);
      setFullResult(data);
      if (data?.routing) {
        setRoutingResult(data.routing);
      }
    } catch (err) {
      setError(err.message || 'Inference request failed.');
    } finally {
      setFullLoading(false);
    }
  };

  const selectSample = (q) => {
    setQuery(q);
    setRoutingResult(null);
    setFullResult(null);
    setError(null);
    textareaRef.current?.focus();
  };

  const copyResponse = () => {
    if (fullResult?.response) {
      navigator.clipboard.writeText(fullResult.response);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    }
  };

  const hasApiKey = backendHealth ? backendHealth.has_api_key : false;
  const wordCount = query.trim() ? query.trim().split(/\s+/).length : 0;
  const targetModelId = routingResult
    ? (backendHealth?.model_tiers?.[routingResult.selected_model]?.model_id || routingResult.selected_model)
    : null;

  return (
    <div className="p-6 md:p-8 max-w-6xl mx-auto space-y-6 pb-24 h-full overflow-y-auto">
      {/* Page Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-4 border-b border-[#293545]">
        <div>
          <div className="flex items-center gap-2.5 mb-1">
            <h1 className="text-xl font-bold tracking-tight text-[#F1F5F9]">
              TIERFLOW <span className="text-[#3B82F6] font-medium">Playground</span>
            </h1>
            <span className="text-[10px] font-mono uppercase px-2 py-0.5 rounded bg-[#1A2431] text-[#94A3B8] border border-[#293545]">
              Adaptive LLM Inference
            </span>
          </div>
          <p className="text-xs text-[#94A3B8]">
            Route smarter. Measure everything. Submit queries to inspect ML classifier predictions and stream real LLM inference.
          </p>
        </div>

        {/* Execution Mode Selector */}
        <div className="flex items-center gap-1 bg-[#121923] p-1 rounded-md border border-[#293545]">
          <button
            type="button"
            onClick={() => { setExecutionMode('real'); setFullResult(null); }}
            className={`flex items-center gap-1.5 px-3 py-1.5 rounded text-xs font-medium transition-colors ${
              executionMode === 'real'
                ? 'bg-[#1A2431] text-[#F1F5F9] border border-[#293545] shadow-xs'
                : 'text-[#94A3B8] hover:text-[#F1F5F9]'
            }`}
          >
            <span className={`w-1.5 h-1.5 rounded-full ${hasApiKey ? 'bg-[#34D399]' : 'bg-amber-400'}`} />
            <span>Real LLM Inference</span>
          </button>
          <button
            type="button"
            onClick={() => { setExecutionMode('demo'); setFullResult(null); }}
            className={`flex items-center gap-1.5 px-3 py-1.5 rounded text-xs font-medium transition-colors ${
              executionMode === 'demo'
                ? 'bg-[#1A2431] text-[#F1F5F9] border border-[#293545] shadow-xs'
                : 'text-[#94A3B8] hover:text-[#F1F5F9]'
            }`}
          >
            <span className="w-1.5 h-1.5 rounded-full bg-[#3B82F6]" />
            <span>Demo Mode (Offline)</span>
          </button>
        </div>
      </div>

      {/* Mode Status Pill */}
      {executionMode === 'real' && !hasApiKey && (
        <div className="flex items-start gap-2.5 bg-amber-950/30 border border-amber-800/60 rounded-md p-3 text-xs text-amber-300">
          <Key className="w-4 h-4 text-amber-400 flex-shrink-0 mt-0.5" />
          <div className="leading-relaxed">
            <strong className="text-amber-200">Gemini API Key Required for Real Inference:</strong> Add{' '}
            <code className="font-mono bg-amber-950/80 px-1.5 py-0.5 rounded text-amber-300 border border-amber-800/60">
              GEMINI_API_KEY=your_key
            </code>{' '}
            in <code className="font-mono text-[#F1F5F9]">backend/.env</code>, or switch to <strong>Demo Mode</strong> to evaluate simulated inference.
          </div>
        </div>
      )}

      {/* Query Editor Box */}
      <div className="bg-[#121923] border border-[#293545] rounded-md overflow-hidden focus-within:border-[#3B82F6] transition-colors">
        {/* Editor Toolbar Header */}
        <div className="flex items-center justify-between px-4 py-2.5 bg-[#0E141C] border-b border-[#293545] text-xs font-mono text-[#94A3B8]">
          <span className="font-semibold text-[#F1F5F9] text-[11px] tracking-wider uppercase">Prompt / Query Input</span>
          <div className="flex items-center gap-3 text-[11px]">
            <span>{wordCount} words</span>
            <span className="text-[#94A3B8]/60">•</span>
            <span>{query.length} chars</span>
          </div>
        </div>

        {/* Textarea */}
        <textarea
          ref={textareaRef}
          value={query}
          onChange={(e) => {
            setQuery(e.target.value);
            setError(null);
          }}
          placeholder="Enter any query or task description (e.g., 'What is the capital of India?' or a complex algorithmic problem)..."
          className="w-full bg-[#0E141C] p-4 text-sm font-sans text-[#F1F5F9] placeholder:text-neutral-600 focus:outline-none resize-y min-h-[120px] leading-relaxed selection:bg-[#3B82F6]/30"
          rows={5}
          onKeyDown={(e) => {
            if (e.key === 'Enter' && (e.ctrlKey || e.metaKey)) {
              e.preventDefault();
              handleAskAndRoute();
            }
          }}
        />

        {/* Bottom Actions & Sample Chips */}
        <div className="p-3 bg-[#0E141C] border-t border-[#293545] flex flex-col md:flex-row md:items-center justify-between gap-3">
          {/* Sample Chips */}
          <div className="flex items-center gap-1.5 overflow-x-auto pb-1 md:pb-0">
            <span className="text-[10px] font-mono text-[#94A3B8] uppercase tracking-wider mr-1 shrink-0">Samples:</span>
            {SAMPLE_QUERIES.map((s) => (
              <button
                key={s.label}
                type="button"
                onClick={() => selectSample(s.query)}
                className="text-[11px] font-mono px-2 py-1 rounded bg-[#1A2431] hover:bg-[#293545] text-[#94A3B8] hover:text-[#F1F5F9] border border-[#293545] transition-colors shrink-0"
                title={s.query}
              >
                {s.label}
              </button>
            ))}
          </div>

          {/* Action Buttons */}
          <div className="flex items-center gap-2 shrink-0">
            <span className="text-[10px] font-mono text-[#94A3B8] hidden lg:inline mr-1">⌘/Ctrl+Enter</span>
            <button
              type="button"
              onClick={handleRouteOnly}
              disabled={routingLoading || fullLoading || !query.trim()}
              className="flex items-center gap-1.5 px-3 py-1.5 rounded-md text-xs font-mono font-medium text-[#F1F5F9] bg-[#1A2431] hover:bg-[#293545] border border-[#293545] disabled:opacity-40 disabled:cursor-not-allowed transition-colors"
            >
              {routingLoading ? <RefreshCw className="w-3.5 h-3.5 animate-spin text-[#94A3B8]" /> : <Brain className="w-3.5 h-3.5 text-[#94A3B8]" />}
              <span>Predict Route</span>
            </button>
            <button
              type="button"
              onClick={() => handleAskAndRoute()}
              disabled={fullLoading || !query.trim()}
              className="flex items-center gap-1.5 px-4 py-1.5 rounded-md text-xs font-medium text-white bg-[#3B82F6] hover:bg-blue-500 shadow-sm disabled:opacity-40 disabled:cursor-not-allowed transition-colors"
            >
              {fullLoading ? <RefreshCw className="w-3.5 h-3.5 animate-spin" /> : <Send className="w-3.5 h-3.5" />}
              <span>{executionMode === 'real' ? 'Ask Real LLM' : 'Ask Model (Demo)'}</span>
            </button>
          </div>
        </div>
      </div>

      {/* Global Error Banner */}
      {error && (
        <div className="flex items-start gap-2.5 bg-red-950/30 border border-red-800/60 rounded-md p-3 text-xs text-red-300">
          <AlertCircle className="w-4 h-4 text-red-400 flex-shrink-0 mt-0.5" />
          <div>
            <strong className="text-red-200">Error:</strong> {error}
          </div>
        </div>
      )}

      {/* ── Results & Telemetry Console ─────────────────────────────────── */}
      {routingResult && (
        <div ref={resultsRef} className="space-y-4">
          {/* Decision & Performance Status Strip */}
          <div className="bg-[#121923] border border-[#293545] rounded-md p-4 grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-4 text-xs font-mono">
            {/* 1. Routed Tier */}
            <div className="space-y-1">
              <span className="text-[10px] text-[#94A3B8] uppercase tracking-wider block">ML Decision</span>
              <ModelBadge model={routingResult.selected_model} />
            </div>

            {/* 2. Target Model */}
            <div className="space-y-1 truncate">
              <span className="text-[10px] text-[#94A3B8] uppercase tracking-wider block">Target Model</span>
              <span className="font-semibold text-[#F1F5F9] truncate block" title={targetModelId}>
                {targetModelId}
              </span>
            </div>

            {/* 3. Confidence */}
            <div className="space-y-1">
              <span className="text-[10px] text-[#94A3B8] uppercase tracking-wider block">Confidence</span>
              <span className="font-semibold text-[#F1F5F9] tabular-nums">
                {((routingResult.confidence ?? 0) * 100).toFixed(1)}%
              </span>
            </div>

            {/* 4. Complexity */}
            <div className="space-y-1">
              <span className="text-[10px] text-[#94A3B8] uppercase tracking-wider block">Complexity</span>
              <span className="text-[#F1F5F9] uppercase font-semibold">
                {routingResult.complexity || 'LOW'}
              </span>
            </div>

            {/* 5. Latency */}
            <div className="space-y-1">
              <span className="text-[10px] text-[#94A3B8] uppercase tracking-wider block">Latency</span>
              <span className="font-semibold text-[#F1F5F9] tabular-nums">
                {fullResult?.metrics?.latency != null ? `${fullResult.metrics.latency.toFixed(3)}s` : '—'}
              </span>
            </div>

            {/* 6. Estimated Cost */}
            <div className="space-y-1">
              <span className="text-[10px] text-[#94A3B8] uppercase tracking-wider block">Cost (Est.)</span>
              <span className="font-semibold text-[#F1F5F9] tabular-nums">
                {fullResult?.metrics?.estimated_cost != null ? `$${fullResult.metrics.estimated_cost.toFixed(6)}` : '—'}
              </span>
            </div>
          </div>

          {/* Decision Rationale */}
          {routingResult.reasoning && (
            <div className="bg-[#0E141C] border border-[#293545] rounded-md px-4 py-2.5 text-xs text-[#F1F5F9] flex items-center justify-between gap-4">
              <div className="flex items-center gap-2">
                <span className="font-mono text-[10px] uppercase tracking-wider text-[#94A3B8]">Rationale:</span>
                <span>{routingResult.reasoning}</span>
              </div>
              <span className="font-mono text-[10px] text-[#94A3B8] shrink-0">TF-IDF + Logistic Regression</span>
            </div>
          )}

          {/* ── Generated Response Panel (FLAGSHIP VISIBILITY) ──────────── */}
          {fullLoading && (
            <div className="bg-[#121923] border border-[#3B82F6]/40 rounded-md p-5 space-y-3 animate-pulse">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2 text-xs font-mono text-[#F1F5F9]">
                  <RefreshCw className="w-3.5 h-3.5 text-[#3B82F6] animate-spin" />
                  <span>Generating response via <strong className="text-white">{targetModelId}</strong>...</span>
                </div>
                <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-[#1A2431] text-[#3B82F6] border border-[#293545] uppercase">
                  In Flight
                </span>
              </div>
              <div className="space-y-2 pt-1">
                <div className="h-3.5 bg-[#1A2431] rounded w-5/6"></div>
                <div className="h-3.5 bg-[#1A2431] rounded w-4/6"></div>
                <div className="h-3.5 bg-[#1A2431] rounded w-3/6"></div>
              </div>
            </div>
          )}

          {fullResult && !fullLoading && (
            <div className="space-y-3">
              {fullResult.error ? (
                /* Provider Error Card */
                <div className="bg-amber-950/30 border border-amber-800/60 rounded-md p-4 text-xs space-y-2">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-2 text-amber-200 font-semibold">
                      <AlertTriangle className="w-4 h-4 text-amber-400" />
                      <span>Inference Status: {fullResult.error.type || 'Provider Error'}</span>
                    </div>
                    <span className="font-mono text-amber-400 bg-amber-950/60 px-2 py-0.5 rounded border border-amber-800/60">
                      HTTP {fullResult.error.status_code || 400}
                    </span>
                  </div>
                  <p className="font-mono text-[#F1F5F9] bg-[#0E141C] p-3 rounded border border-[#293545]">
                    {fullResult.error.message}
                  </p>
                  <div className="flex items-center justify-between pt-1">
                    <span className="text-[#94A3B8]">Configure key in <code className="text-[#F1F5F9]">backend/.env</code></span>
                    <button
                      type="button"
                      onClick={() => handleAskAndRoute('demo')}
                      className="px-3 py-1 rounded bg-[#1A2431] hover:bg-[#293545] text-[#F1F5F9] border border-[#293545] text-xs font-mono"
                    >
                      Run in Demo Mode
                    </button>
                  </div>
                </div>
              ) : (
                /* Response Card */
                <div className="bg-[#121923] border border-[#293545] rounded-md overflow-hidden">
                  {/* Response Header */}
                  <div className="px-4 py-2.5 bg-[#0E141C] border-b border-[#293545] flex items-center justify-between text-xs">
                    <div className="flex items-center gap-2">
                      <span className="font-mono text-[11px] font-semibold text-[#F1F5F9] uppercase tracking-wider">
                        Generated Answer
                      </span>
                      <span className={`text-[10px] font-mono px-1.5 py-0.2 rounded border ${
                        fullResult.execution_mode === 'real'
                          ? 'bg-[#34D399]/15 text-[#34D399] border-[#34D399]/30'
                          : 'bg-[#1A2431] text-[#94A3B8] border-[#293545]'
                      }`}>
                        {fullResult.execution_mode === 'real' ? 'Live Inference' : 'Simulated'}
                      </span>
                    </div>

                    <button
                      type="button"
                      onClick={copyResponse}
                      className="flex items-center gap-1 text-[11px] font-mono text-[#94A3B8] hover:text-[#F1F5F9] transition-colors"
                      title="Copy response"
                    >
                      {copied ? <Check className="w-3.5 h-3.5 text-[#34D399]" /> : <Copy className="w-3.5 h-3.5" />}
                      <span>{copied ? 'Copied' : 'Copy'}</span>
                    </button>
                  </div>

                  {/* Response Content */}
                  <div className="p-5 bg-[#0E141C] text-[#F1F5F9] text-sm leading-relaxed whitespace-pre-wrap font-sans selection:bg-[#3B82F6]/30">
                    {fullResult.response || '(Empty response received)'}
                  </div>

                  {/* Telemetry Footer */}
                  <div className="px-4 py-2.5 bg-[#0E141C] border-t border-[#293545] flex flex-wrap items-center justify-between gap-3 text-[11px] font-mono text-[#94A3B8]">
                    <div className="flex items-center gap-4">
                      <span>Model: <strong className="text-[#F1F5F9]">{fullResult.model_id || targetModelId}</strong></span>
                      {fullResult.token_usage?.total_tokens > 0 && (
                        <span>
                          Tokens: <strong className="text-[#F1F5F9]">{fullResult.token_usage.total_tokens}</strong> ({fullResult.token_usage.prompt_tokens} in / {fullResult.token_usage.completion_tokens} out)
                        </span>
                      )}
                    </div>
                    {fullResult.comparison && (
                      <div className="flex items-center gap-3">
                        <span className="text-[#34D399] font-semibold">
                          Cost Δ: {fullResult.comparison.cost_reduction != null ? `${fullResult.comparison.cost_reduction >= 0 ? '+' : ''}${fullResult.comparison.cost_reduction.toFixed(1)}%` : '—'}
                        </span>
                        <span className="text-[#34D399] font-semibold">
                          Latency Δ: {fullResult.comparison.latency_reduction != null ? `${fullResult.comparison.latency_reduction >= 0 ? '+' : ''}${fullResult.comparison.latency_reduction.toFixed(1)}%` : '—'}
                        </span>
                      </div>
                    )}
                  </div>
                </div>
              )}
            </div>
          )}

          {/* ── Inspection Details (Probabilities & Linguistic Features) ── */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 pt-2">
            {/* Probability Distribution */}
            <div className="bg-[#121923] border border-[#293545] rounded-md p-4 space-y-3">
              <div className="flex items-center justify-between border-b border-[#293545] pb-2">
                <span className="text-[11px] font-mono font-semibold uppercase tracking-wider text-[#94A3B8]">
                  Classifier Probability Distribution
                </span>
                <span className="text-[10px] font-mono text-[#94A3B8]">Softmax outputs</span>
              </div>
              <div className="space-y-3 pt-1">
                {Object.entries(routingResult.probabilities || {})
                  .sort(([, a], [, b]) => b - a)
                  .map(([model, prob]) => (
                    <ProbabilityBar key={model} model={model} prob={prob} />
                  ))}
              </div>
            </div>

            {/* Linguistic Feature Extraction */}
            <div className="bg-[#121923] border border-[#293545] rounded-md p-4 space-y-3">
              <div className="flex items-center justify-between border-b border-[#293545] pb-2">
                <span className="text-[11px] font-mono font-semibold uppercase tracking-wider text-[#94A3B8]">
                  Extracted Linguistic Features
                </span>
                <span className="text-[10px] font-mono text-[#94A3B8]">Lexical Vector</span>
              </div>
              {routingResult.features && (
                <div className="grid grid-cols-3 gap-2 text-xs font-mono pt-1">
                  {[
                    ['Words', routingResult.features.word_count],
                    ['Chars', routingResult.features.query_length],
                    ['Sentences', routingResult.features.sentence_count],
                    ['Math Kw', routingResult.features.has_math_keywords],
                    ['Code Kw', routingResult.features.has_code_keywords],
                    ['Reason Kw', routingResult.features.has_reasoning_keywords],
                    ['Constraints', routingResult.features.num_constraints],
                    ['Multi-step', routingResult.features.has_multi_step],
                    ['Q-Type', routingResult.features.question_type],
                  ].map(([label, val]) => (
                    <div key={label} className="bg-[#0E141C] border border-[#293545] rounded px-2.5 py-1.5 flex flex-col justify-between">
                      <span className="text-[10px] text-[#94A3B8]">{label}</span>
                      <span className="text-[#F1F5F9] font-semibold">{String(val ?? '0')}</span>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
