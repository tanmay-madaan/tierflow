import React, { useState, useEffect } from 'react';
import { Routes, Route, NavLink } from 'react-router-dom';
import { LayoutDashboard, FlaskConical, BarChart3, Activity, Cpu, AlertCircle, CheckCircle } from 'lucide-react';
import Dashboard from './pages/Dashboard';
import Experiments from './pages/Experiments';
import ResearchResults from './pages/ResearchResults';
import RouterPlayground from './pages/RouterPlayground';
import { api } from './services/api';

function App() {
  const [health, setHealth] = useState(null);

  useEffect(() => {
    api.getHealth().then(data => {
      if (data) setHealth(data);
    });
  }, []);

  const isDemo = health ? health.demo_mode : true;

  return (
    <div className="flex h-screen bg-[#0B0F14] text-[#F1F5F9] overflow-hidden font-sans selection:bg-[#3B82F6]/30">
      {/* Sidebar */}
      <aside className="w-64 border-r border-[#293545] bg-[#121923] flex flex-col flex-shrink-0">
        <div className="p-5 flex flex-col h-full">
          {/* Brand Header */}
          <div className="flex items-center gap-3 mb-4 pb-4 border-b border-[#293545]">
            <div className="w-8 h-8 rounded-md bg-[#1A2431] border border-[#293545] flex items-center justify-center text-[#3B82F6] font-mono font-bold text-xs shadow-xs">
              <Cpu className="w-4 h-4 text-[#3B82F6]" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <h1 className="font-bold text-sm tracking-wider uppercase text-[#F1F5F9]">TIERFLOW</h1>
                <span className="text-[9px] font-mono px-1.5 py-0.2 rounded bg-[#1A2431] text-[#94A3B8] border border-[#293545]">v2.1</span>
              </div>
              <p className="text-[11px] text-[#94A3B8] font-mono tracking-tight">Adaptive LLM Inference</p>
            </div>
          </div>

          {/* Brand Tagline Banner */}
          <div className="mb-4 px-2.5 py-1.5 rounded bg-[#1A2431]/70 border border-[#293545] text-[10px] font-mono text-[#94A3B8] text-center">
            Route smarter. Measure everything.
          </div>

          {/* Navigation */}
          <div className="mb-2">
            <span className="text-[10px] font-mono font-semibold uppercase tracking-wider text-[#94A3B8] px-3">Navigation</span>
          </div>
          <nav className="space-y-1 flex-1">
            <NavLink
              to="/"
              end
              className={({ isActive }) =>
                `flex items-center gap-2.5 px-3 py-2 rounded-md transition-all text-xs font-medium ${
                  isActive
                    ? 'bg-[#1A2431] text-[#F1F5F9] border border-[#293545] shadow-xs'
                    : 'text-[#94A3B8] hover:text-[#F1F5F9] hover:bg-[#1A2431]/60'
                }`
              }
            >
              <LayoutDashboard className="w-3.5 h-3.5 text-[#94A3B8]" />
              <span>Overview</span>
            </NavLink>

            <NavLink
              to="/playground"
              className={({ isActive }) =>
                `flex items-center gap-2.5 px-3 py-2 rounded-md transition-all text-xs font-medium ${
                  isActive
                    ? 'bg-[#1A2431] text-[#F1F5F9] border border-[#293545] shadow-xs'
                    : 'text-[#94A3B8] hover:text-[#F1F5F9] hover:bg-[#1A2431]/60'
                }`
              }
            >
              <Cpu className="w-3.5 h-3.5 text-[#3B82F6]" />
              <span>Playground</span>
              <span className={`ml-auto text-[9px] font-mono font-semibold px-1.5 py-0.5 rounded uppercase tracking-wider border ${
                health?.has_api_key
                  ? 'bg-[#34D399]/15 text-[#34D399] border-[#34D399]/30'
                  : 'bg-[#1A2431] text-[#94A3B8] border-[#293545]'
              }`}>
                {health?.has_api_key ? 'Live API' : 'Demo'}
              </span>
            </NavLink>

            <NavLink
              to="/experiments"
              className={({ isActive }) =>
                `flex items-center gap-2.5 px-3 py-2 rounded-md transition-all text-xs font-medium ${
                  isActive
                    ? 'bg-[#1A2431] text-[#F1F5F9] border border-[#293545] shadow-xs'
                    : 'text-[#94A3B8] hover:text-[#F1F5F9] hover:bg-[#1A2431]/60'
                }`
              }
            >
              <FlaskConical className="w-3.5 h-3.5 text-[#94A3B8]" />
              <span>Experiment Log</span>
            </NavLink>

            <NavLink
              to="/research"
              className={({ isActive }) =>
                `flex items-center gap-2.5 px-3 py-2 rounded-md transition-all text-xs font-medium ${
                  isActive
                    ? 'bg-[#1A2431] text-[#F1F5F9] border border-[#293545] shadow-xs'
                    : 'text-[#94A3B8] hover:text-[#F1F5F9] hover:bg-[#1A2431]/60'
                }`
              }
            >
              <BarChart3 className="w-3.5 h-3.5 text-[#94A3B8]" />
              <span>Benchmark &amp; Eval</span>
            </NavLink>
          </nav>

          {/* Infrastructure status footer */}
          <div className="mt-auto pt-4 border-t border-[#293545] space-y-2">
            <div className="bg-[#1A2431] border border-[#293545] rounded-md p-3 text-xs">
              <div className="flex items-center justify-between mb-1.5">
                <div className="flex items-center gap-1.5">
                  <span className={`w-2 h-2 rounded-full ${health?.has_api_key ? 'bg-[#34D399] animate-pulse' : 'bg-amber-400'}`} />
                  <span className="font-mono text-[11px] font-semibold text-[#F1F5F9] uppercase tracking-wide">
                    {health?.has_api_key ? 'Live Inference' : 'Demo Mode'}
                  </span>
                </div>
                <span className="text-[10px] font-mono text-[#94A3B8]">{health?.provider || 'Gemini'}</span>
              </div>
              <p className="text-[11px] text-[#94A3B8] leading-snug">
                {health?.has_api_key
                  ? 'Queries routed to real Gemini tier models.'
                  : 'Offline mode: simulated latencies & costs.'}
              </p>
              <div className="mt-2 pt-2 border-t border-[#293545] flex items-center justify-between text-[10px] font-mono text-[#94A3B8]">
                <span>Classifier:</span>
                <span className={health?.model_trained ? 'text-[#34D399]' : 'text-amber-400'}>
                  {health?.model_trained ? 'Trained (TF-IDF+LR)' : 'Untrained'}
                </span>
              </div>
            </div>
          </div>
        </div>
      </aside>

      {/* Main Canvas */}
      <main className="flex-1 flex flex-col h-screen overflow-y-auto bg-[#0B0F14] text-[#F1F5F9]">
        <div className="w-full h-full">
          <Routes>
            <Route path="/" element={<Dashboard demoMode={isDemo} />} />
            <Route path="/playground" element={<RouterPlayground />} />
            <Route path="/experiments" element={<Experiments />} />
            <Route path="/research" element={<ResearchResults />} />
          </Routes>
        </div>
      </main>
    </div>
  );
}

export default App;
