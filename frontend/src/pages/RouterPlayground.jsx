import React, { useState, useEffect, useRef } from 'react';
import { 
  Send, 
  RefreshCw, 
  AlertCircle, 
  Zap, 
  Brain, 
  Shield, 
  ChevronRight, 
  Info, 
  CheckCircle, 
  Sparkles, 
  Key, 
  AlertTriangle, 
  Copy, 
  Check,
  RotateCcw,
  Sliders,
  Layers,
  Terminal,
  Activity
} from 'lucide-react';
import { api } from '../services/api';
import { ModelBadge } from '../components/ModelBadge';
import { ExecutionModeBadge } from '../components/ExecutionModeBadge';
import { PipelineFlow } from '../components/PipelineFlow';
import { EmptyState } from '../components/EmptyState';

const SAMPLE_QUERIES = [
  { tag: 'Factual', label: 'Capital QA', query: 'What is the capital of India?' },
  { tag: 'Math', label: 'Prime Proof', query: 'Prove that there are infinitely many prime numbers using Euclid\'s classical argument.' },
  { tag: 'Optimization', label: 'Gradient Descent', query: 'Why does gradient descent sometimes fail to converge on non-convex loss surfaces?' },
  { tag: 'Systems', label: 'TCP vs UDP', query: 'Explain the fundamental trade-offs between TCP and UDP in real-time multimedia streaming.' },
  { tag: 'Coding', label: 'Python Palindrome', query: 'Write an optimal Python function to verify if a given string is a palindrome, ignoring punctuation and whitespace.' },
  { tag: 'Architecture', label: 'Fraud Detection Pipeline', query: 'Design an end-to-end machine learning system for real-time fraud detection with extreme class imbalance and sub-50ms latency constraints.' },
];

function ProbabilityBar({ model, prob }) {
  const barColors = {
    SMALL: 'bg-[#34D399]',
    MEDIUM: 'bg-[#F59E0B]',
    LARGE: 'bg-[#818CF8]'
  };

  return (
    <div className="space-y-1">
      <div className="flex justify-between items-center text-xs font-mono">
        <span className="text-[#A0AEC0] uppercase text-[11px] font-medium">{model}</span>
        <span className="text-[#F1F5F9] font-semibold tabular-nums">{(prob * 100).toFixed(1)}%</span>
      </div>
      <div className="w-full bg-[#0D141D] border border-[#263548] rounded h-2 overflow-hidden">
        <div
          className={`h-full rounded transition-all duration-300 ${barColors[model] || 'bg-[#3B82F6]'}`}
          style={{ width: `${Math.max(2, prob * 100)}%` }}
        />
      </div>
    </div>
  );
}

export default function RouterPlayground() {
  const [query, setQuery] = useState('');
  const [executionMode, setExecutionMode] = useState('demo'); // 'real' or 'demo'
  const [backendHealth, setBackendHealth] = useState(null);
  const [routingResult, setRoutingResult] = useState(null);
  const [fullResult, setFullResult] = useState(null);
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
        // Default to real mode only if API key is confirmed; otherwise demo
        setExecutionMode(data.has_api_key ? 'real' : 'demo');
      }
    });
  }, []);

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
      setError(err.message || 'Failed to predict route.');
    } finally {
      setRoutingLoading(false);
    }
  };

  const handleRunInference = async (modeOverride = null) => {
    const q = query.trim();
    if (!q) return;

    const mode = modeOverride || executionMode;
    setError(null);
    setFullLoading(true);
    setFullResult(null);

    try {
      // First predict route for immediate UI feedback
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

  const selectSample = (sampleQuery) => {
    setQuery(sampleQuery);
    setRoutingResult(null);
    setFullResult(null);
    setError(null);
    textareaRef.current?.focus();
  };

  const handleReset = () => {
    setQuery('');
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
    <div className="p-4 sm:p-6 lg:p-8 max-w-7xl mx-auto space-y-6 pb-24">
      {/* ── Page Header ────────────────────────────────────────────── */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-4 border-b border-[#263548]">
        <div>
          <div className="flex items-center gap-2.5 mb-1">
            <h1 className="text-xl font-bold tracking-tight text-[#F1F5F9]">
              TIERFLOW <span className="text-[#3B82F6] font-medium">Playground</span>
            </h1>
            <span className="text-[10px] font-mono uppercase px-2 py-0.5 rounded bg-[#192536] text-[#A0AEC0] border border-[#263548]">
              Interactive Lab
            </span>
          </div>
          <p className="text-xs text-[#A0AEC0] font-sans">
            Submit custom queries to test confidence-based multi-tier classification and benchmark real vs simulated LLM inference.
          </p>
        </div>

        {/* Execution Mode Selector */}
        <div className="flex items-center gap-1 bg-[#141E2A] p-1 rounded-md border border-[#263548] shrink-0">
          <button
            type="button"
            onClick={() => { setExecutionMode('real'); setFullResult(null); }}
            className={`flex items-center gap-1.5 px-3 py-1.5 rounded text-xs font-mono font-medium transition-colors ${
              executionMode === 'real'
                ? 'bg-[#192536] text-[#F1F5F9] border border-[#263548] shadow-xs'
                : 'text-[#A0AEC0] hover:text-[#F1F5F9]'
            }`}
          >
            <span className={`w-2 h-2 rounded-full ${hasApiKey ? 'bg-[#34D399] animate-pulse' : 'bg-[#F59E0B]'}`} />
            <span>Real LLM Inference</span>
          </button>
          <button
            type="button"
            onClick={() => { setExecutionMode('demo'); setFullResult(null); }}
            className={`flex items-center gap-1.5 px-3 py-1.5 rounded text-xs font-mono font-medium transition-colors ${
              executionMode === 'demo'
                ? 'bg-[#192536] text-[#F1F5F9] border border-[#263548] shadow-xs'
                : 'text-[#A0AEC0] hover:text-[#F1F5F9]'
            }`}
          >
            <span className="w-2 h-2 rounded-full bg-[#3B82F6]" />
            <span>Demo Mode (Offline)</span>
          </button>
        </div>
      </div>

      {/* Mode Status Callout */}
      {executionMode === 'real' && !hasApiKey && (
        <div className="flex items-start gap-2.5 bg-amber-950/20 border border-amber-800/50 rounded-md p-3.5 text-xs text-amber-300 font-mono">
          <Key className="w-4 h-4 text-amber-400 shrink-0 mt-0.5" />
          <div className="leading-relaxed font-sans text-xs">
            <strong className="font-mono text-amber-200">API Key Required for Live Provider Calls:</strong> Configure{' '}
            <code className="font-mono bg-amber-950/80 px-1.5 py-0.5 rounded text-amber-300 border border-amber-800/60">
              GEMINI_API_KEY
            </code>{' '}
            in your environment to route live queries to Google Gemini. Real mode will report provider authentication errors until key is verified. Switch to <strong>Demo Mode</strong> to evaluate simulated inference without external dependencies.
          </div>
        </div>
      )}

      {/* ── Interactive Multi-Stage Pipeline Visualization ───────────── */}
      <PipelineFlow 
        selectedTier={routingResult?.selected_model} 
        inFlight={fullLoading}
        hasResponse={Boolean(fullResult?.response)}
      />

      {/* ── Two-Part Layout: Left Editor / Right Decisions ───────────── */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 items-start">
        {/* LEFT COLUMN: Prompt Editor & Controls (7 Cols) */}
        <div className="lg:col-span-7 space-y-4">
          <div className="bg-[#141E2A] border border-[#263548] rounded-md overflow-hidden focus-within:border-[#3B82F6] transition-colors">
            {/* Editor Toolbar Header */}
            <div className="flex items-center justify-between px-4 py-2.5 bg-[#101722] border-b border-[#263548] text-xs font-mono text-[#A0AEC0]">
              <span className="font-semibold text-[#F1F5F9] text-[11px] tracking-wider uppercase">
                Prompt / Task Input
              </span>
              <div className="flex items-center gap-3 text-[11px]">
                <span>{wordCount} words</span>
                <span className="text-[#718096]">•</span>
                <span>{query.length} chars</span>
                {query.length > 0 && (
                  <>
                    <span className="text-[#718096]">•</span>
                    <button
                      type="button"
                      onClick={handleReset}
                      className="text-[#718096] hover:text-[#F1F5F9] flex items-center gap-1 transition-colors"
                      title="Clear prompt"
                    >
                      <RotateCcw className="w-3 h-3" />
                      <span>Reset</span>
                    </button>
                  </>
                )}
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
              placeholder="Enter any prompt, query or technical task to test routing (e.g. 'What is the capital of India?' or 'Design a distributed fault-tolerant key-value store')..."
              className="w-full bg-[#0D141D] p-4 text-xs font-sans text-[#F1F5F9] placeholder:text-[#718096] focus:outline-none resize-y min-h-[140px] leading-relaxed selection:bg-[#3B82F6]/30"
              rows={5}
              onKeyDown={(e) => {
                if (e.key === 'Enter' && (e.ctrlKey || e.metaKey)) {
                  e.preventDefault();
                  handleRunInference();
                }
              }}
            />

            {/* Bottom Actions & Sample Chips */}
            <div className="p-3 bg-[#101722] border-t border-[#263548] space-y-3">
              {/* Sample Chips */}
              <div className="flex items-center gap-1.5 overflow-x-auto pb-1 text-xs">
                <span className="text-[10px] font-mono text-[#718096] uppercase tracking-wider shrink-0 mr-1">
                  Samples:
                </span>
                {SAMPLE_QUERIES.map((s) => (
                  <button
                    key={s.label}
                    type="button"
                    onClick={() => selectSample(s.query)}
                    className="text-[11px] font-mono px-2 py-0.5 rounded bg-[#192536] hover:bg-[#263548] text-[#A0AEC0] hover:text-[#F1F5F9] border border-[#263548] transition-colors shrink-0"
                    title={s.query}
                  >
                    {s.label}
                  </button>
                ))}
              </div>

              {/* Action Buttons */}
              <div className="flex items-center justify-between pt-1">
                <span className="text-[10px] font-mono text-[#718096] hidden sm:inline">
                  Shortcut: ⌘/Ctrl+Enter
                </span>

                <div className="flex items-center gap-2 ml-auto">
                  <button
                    type="button"
                    onClick={handleRouteOnly}
                    disabled={routingLoading || fullLoading || !query.trim()}
                    className="flex items-center gap-1.5 px-3 py-1.5 rounded-md text-xs font-mono font-medium text-[#F1F5F9] bg-[#192536] hover:bg-[#263548] border border-[#263548] disabled:opacity-40 disabled:cursor-not-allowed transition-colors"
                  >
                    {routingLoading ? <RefreshCw className="w-3.5 h-3.5 animate-spin text-[#A0AEC0]" /> : <Brain className="w-3.5 h-3.5 text-[#3B82F6]" />}
                    <span>Predict Route</span>
                  </button>

                  <button
                    type="button"
                    onClick={() => handleRunInference()}
                    disabled={fullLoading || !query.trim()}
                    className="flex items-center gap-1.5 px-4 py-1.5 rounded-md text-xs font-mono font-medium text-white bg-[#3B82F6] hover:bg-[#2563EB] shadow-xs disabled:opacity-40 disabled:cursor-not-allowed transition-colors"
                  >
                    {fullLoading ? <RefreshCw className="w-3.5 h-3.5 animate-spin" /> : <Send className="w-3.5 h-3.5" />}
                    <span>{executionMode === 'real' ? 'Run Real Inference' : 'Run Demo Inference'}</span>
                  </button>
                </div>
              </div>
            </div>
          </div>

          {/* Global Error Banner */}
          {error && (
            <div className="flex items-start gap-2.5 bg-red-950/30 border border-red-800/60 rounded-md p-3 text-xs text-red-300 font-mono">
              <AlertCircle className="w-4 h-4 text-red-400 shrink-0 mt-0.5" />
              <div>
                <strong className="text-red-200">Execution Error:</strong> {error}
              </div>
            </div>
          )}

          {/* Response Viewer Panel */}
          {fullLoading && (
            <div className="bg-[#141E2A] border border-[#3B82F6]/40 rounded-md p-5 space-y-3 animate-pulse">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2 text-xs font-mono text-[#F1F5F9]">
                  <RefreshCw className="w-3.5 h-3.5 text-[#3B82F6] animate-spin" />
                  <span>Executing inference on <strong className="text-white">{targetModelId || 'selected tier'}</strong>...</span>
                </div>
                <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-[#192536] text-[#3B82F6] border border-[#263548] uppercase">
                  In Flight
                </span>
              </div>
              <div className="space-y-2 pt-2">
                <div className="h-3 bg-[#192536] rounded w-5/6"></div>
                <div className="h-3 bg-[#192536] rounded w-4/6"></div>
                <div className="h-3 bg-[#192536] rounded w-3/6"></div>
              </div>
            </div>
          )}

          {fullResult && !fullLoading && (
            <div className="space-y-3">
              {fullResult.error ? (
                /* Provider Error Card */
                <div className="bg-amber-950/30 border border-amber-800/60 rounded-md p-4 text-xs space-y-2 font-mono">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-2 text-amber-200 font-semibold">
                      <AlertTriangle className="w-4 h-4 text-amber-400" />
                      <span>Provider Status: {fullResult.error.type || 'Error'}</span>
                    </div>
                    <span className="text-[10px] text-amber-400 bg-amber-950/60 px-2 py-0.5 rounded border border-amber-800/60">
                      HTTP {fullResult.error.status_code || 400}
                    </span>
                  </div>
                  <p className="text-[#F1F5F9] bg-[#0D141D] p-3 rounded border border-[#263548] leading-relaxed">
                    {fullResult.error.message}
                  </p>
                  <div className="flex items-center justify-between pt-1 text-[11px]">
                    <span className="text-[#718096]">Check API credentials or quota limits</span>
                    <button
                      type="button"
                      onClick={() => handleRunInference('demo')}
                      className="px-3 py-1 rounded bg-[#192536] hover:bg-[#263548] text-[#F1F5F9] border border-[#263548] text-xs font-mono"
                    >
                      Run in Demo Mode
                    </button>
                  </div>
                </div>
              ) : (
                /* Response Card */
                <div className="bg-[#141E2A] border border-[#263548] rounded-md overflow-hidden">
                  <div className="px-4 py-2.5 bg-[#101722] border-b border-[#263548] flex items-center justify-between text-xs">
                    <div className="flex items-center gap-2">
                      <Terminal className="w-3.5 h-3.5 text-[#34D399]" />
                      <span className="font-mono text-[11px] font-semibold text-[#F1F5F9] uppercase tracking-wider">
                        Generated Response
                      </span>
                      <ExecutionModeBadge mode={fullResult.execution_mode} />
                    </div>

                    <button
                      type="button"
                      onClick={copyResponse}
                      className="flex items-center gap-1 text-[11px] font-mono text-[#A0AEC0] hover:text-[#F1F5F9] transition-colors"
                      title="Copy response"
                    >
                      {copied ? <Check className="w-3.5 h-3.5 text-[#34D399]" /> : <Copy className="w-3.5 h-3.5" />}
                      <span>{copied ? 'Copied' : 'Copy'}</span>
                    </button>
                  </div>

                  <div className="p-4 bg-[#0D141D] text-[#F1F5F9] text-xs leading-relaxed whitespace-pre-wrap font-sans selection:bg-[#3B82F6]/30 max-h-80 overflow-y-auto">
                    {fullResult.response || '(Empty response returned)'}
                  </div>

                  <div className="px-4 py-2 bg-[#101722] border-t border-[#263548] flex flex-wrap items-center justify-between gap-3 text-[11px] font-mono text-[#A0AEC0]">
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
                        <span className="text-[#34D399]">
                          Cost Δ: {fullResult.comparison.cost_reduction != null ? `${fullResult.comparison.cost_reduction >= 0 ? '+' : ''}${fullResult.comparison.cost_reduction.toFixed(1)}%` : 'N/A'}
                        </span>
                        <span className="text-[#34D399]">
                          Latency Δ: {fullResult.comparison.latency_reduction != null ? `${fullResult.comparison.latency_reduction >= 0 ? '+' : ''}${fullResult.comparison.latency_reduction.toFixed(1)}%` : 'N/A'}
                        </span>
                      </div>
                    )}
                  </div>
                </div>
              )}
            </div>
          )}
        </div>

        {/* RIGHT COLUMN: Routing Decision & Telemetry (5 Cols) */}
        <div className="lg:col-span-5 space-y-4">
          {routingResult ? (
            <div ref={resultsRef} className="space-y-4">
              {/* Routing Decision Panel */}
              <div className="bg-[#141E2A] border border-[#263548] rounded-md p-4 space-y-3 font-mono">
                <div className="flex items-center justify-between border-b border-[#263548] pb-2.5">
                  <span className="text-[11px] font-semibold uppercase tracking-wider text-[#F1F5F9]">
                    Routing Decision
                  </span>
                  <ExecutionModeBadge mode={fullResult ? fullResult.execution_mode : (executionMode === 'real' ? 'real' : 'demo')} />
                </div>

                <div className="grid grid-cols-2 gap-3 text-xs">
                  <div className="p-2.5 rounded bg-[#101722] border border-[#263548] space-y-1">
                    <span className="text-[10px] text-[#718096] uppercase tracking-wider block">Selected Tier</span>
                    <ModelBadge model={routingResult.selected_model} size="lg" />
                  </div>

                  <div className="p-2.5 rounded bg-[#101722] border border-[#263548] space-y-1 truncate">
                    <span className="text-[10px] text-[#718096] uppercase tracking-wider block">Model ID</span>
                    <span className="font-semibold text-[#F1F5F9] truncate block text-[11px]" title={targetModelId}>
                      {targetModelId}
                    </span>
                  </div>

                  <div className="p-2.5 rounded bg-[#101722] border border-[#263548] space-y-1">
                    <span className="text-[10px] text-[#718096] uppercase tracking-wider block">Confidence</span>
                    <span className="font-semibold text-[#F1F5F9] tabular-nums">
                      {((routingResult.confidence ?? 0) * 100).toFixed(1)}%
                    </span>
                  </div>

                  <div className="p-2.5 rounded bg-[#101722] border border-[#263548] space-y-1">
                    <span className="text-[10px] text-[#718096] uppercase tracking-wider block">Complexity</span>
                    <span className="font-semibold text-[#F1F5F9] uppercase">
                      {routingResult.complexity || 'LOW'}
                    </span>
                  </div>

                  <div className="p-2.5 rounded bg-[#101722] border border-[#263548] space-y-1">
                    <span className="text-[10px] text-[#718096] uppercase tracking-wider block">Latency</span>
                    <span className="font-semibold text-[#F1F5F9] tabular-nums">
                      {fullResult?.metrics?.latency != null ? `${fullResult.metrics.latency.toFixed(3)}s` : 'Standby'}
                    </span>
                  </div>

                  <div className="p-2.5 rounded bg-[#101722] border border-[#263548] space-y-1">
                    <span className="text-[10px] text-[#718096] uppercase tracking-wider block">Cost</span>
                    <span className="font-semibold text-[#F1F5F9] tabular-nums">
                      {fullResult?.metrics?.estimated_cost != null ? `$${fullResult.metrics.estimated_cost.toFixed(5)}` : 'Standby'}
                    </span>
                  </div>
                </div>

                {routingResult.reasoning && (
                  <div className="pt-2 border-t border-[#263548] text-xs font-sans text-[#A0AEC0] leading-relaxed">
                    <strong className="text-[#F1F5F9] font-mono text-[10px] uppercase block mb-0.5">Rationale:</strong>
                    {routingResult.reasoning}
                  </div>
                )}
              </div>

              {/* Probability Distribution */}
              <div className="bg-[#141E2A] border border-[#263548] rounded-md p-4 space-y-3 font-mono">
                <div className="flex items-center justify-between border-b border-[#263548] pb-2">
                  <span className="text-[11px] font-semibold uppercase tracking-wider text-[#F1F5F9]">
                    Classifier Softmax Probabilities
                  </span>
                  <span className="text-[10px] text-[#718096]">Logits</span>
                </div>
                <div className="space-y-3 pt-1">
                  {Object.entries(routingResult.probabilities || {})
                    .sort(([, a], [, b]) => b - a)
                    .map(([model, prob]) => (
                      <ProbabilityBar key={model} model={model} prob={prob} />
                    ))}
                </div>
              </div>

              {/* Extracted Linguistic Features */}
              {routingResult.features && (
                <div className="bg-[#141E2A] border border-[#263548] rounded-md p-4 space-y-3 font-mono">
                  <div className="flex items-center justify-between border-b border-[#263548] pb-2">
                    <span className="text-[11px] font-semibold uppercase tracking-wider text-[#F1F5F9]">
                      Extracted Linguistic Vector
                    </span>
                    <span className="text-[10px] text-[#718096]">Features</span>
                  </div>
                  <div className="grid grid-cols-3 gap-2 text-xs">
                    {[
                      ['Words', routingResult.features.word_count],
                      ['Chars', routingResult.features.query_length],
                      ['Sentences', routingResult.features.sentence_count],
                      ['Math Kw', routingResult.features.has_math_keywords],
                      ['Code Kw', routingResult.features.has_code_keywords],
                      ['Reason Kw', routingResult.features.has_reasoning_keywords],
                      ['Constraints', routingResult.features.num_constraints],
                      ['Multi-step', routingResult.features.has_multi_step],
                      ['Question', routingResult.features.question_type],
                    ].map(([lbl, val]) => (
                      <div key={lbl} className="bg-[#101722] border border-[#263548] rounded px-2.5 py-1.5 flex flex-col justify-between">
                        <span className="text-[9px] text-[#718096] uppercase">{lbl}</span>
                        <span className="text-[#F1F5F9] font-semibold text-[11px] truncate">{String(val ?? '0')}</span>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          ) : (
            /* Idle Right Column State */
            <EmptyState
              title="Awaiting Route Inspection"
              message="Enter a prompt on the left and click 'Predict Route' or 'Run Inference' to view the routing decision, model tier allocation, probability distribution, and telemetry."
              icon={Brain}
              className="py-16"
            />
          )}
        </div>
      </div>
    </div>
  );
}
