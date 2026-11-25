import React, { useState, useEffect } from 'react';
import { Routes, Route, NavLink, useLocation } from 'react-router-dom';
import { 
  LayoutDashboard, 
  FlaskConical, 
  BarChart3, 
  Cpu, 
  Menu, 
  X, 
  ShieldCheck, 
  Layers,
  ChevronRight,
  Sparkles,
  ExternalLink
} from 'lucide-react';
import Dashboard from './pages/Dashboard';
import Experiments from './pages/Experiments';
import ResearchResults from './pages/ResearchResults';
import RouterPlayground from './pages/RouterPlayground';
import { api } from './services/api';

function App() {
  const [health, setHealth] = useState(null);
  const [mobileNavOpen, setMobileNavOpen] = useState(false);
  const location = useLocation();

  useEffect(() => {
    api.getHealth().then(data => {
      if (data) setHealth(data);
    });
  }, []);

  // Close mobile nav drawer whenever route changes
  useEffect(() => {
    setMobileNavOpen(false);
  }, [location.pathname]);

  const isDemo = health ? health.demo_mode : true;

  const navLinks = [
    { to: '/', label: 'Overview', icon: LayoutDashboard },
    { to: '/playground', label: 'Playground', icon: Cpu, badge: health?.has_api_key ? 'Live' : 'Demo' },
    { to: '/experiments', label: 'Experiment Log', icon: FlaskConical },
    { to: '/research', label: 'Benchmark & Eval', icon: BarChart3 },
  ];

  const sidebarContent = (
    <div className="p-5 flex flex-col h-full bg-[#101722] text-[#F1F5F9]">
      {/* Brand Header */}
      <div className="flex items-center justify-between pb-4 mb-4 border-b border-[#263548]">
        <div className="flex items-center gap-3">
          <div className="w-8 h-8 rounded-md bg-[#192536] border border-[#263548] flex items-center justify-center text-[#3B82F6] font-mono font-bold text-xs shadow-xs">
            <Cpu className="w-4 h-4 text-[#3B82F6]" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <span className="font-bold text-sm tracking-wider uppercase text-[#F1F5F9]">TIERFLOW</span>
              <span className="text-[9px] font-mono px-1.5 py-0.2 rounded bg-[#192536] text-[#A0AEC0] border border-[#263548]">v2.1</span>
            </div>
            <p className="text-[11px] text-[#718096] font-mono tracking-tight">Adaptive LLM Inference</p>
          </div>
        </div>

        {/* Mobile close button */}
        <button
          onClick={() => setMobileNavOpen(false)}
          className="lg:hidden p-1.5 rounded-md text-[#A0AEC0] hover:text-[#F1F5F9] hover:bg-[#192536] transition-colors"
          aria-label="Close navigation"
        >
          <X className="w-5 h-5" />
        </button>
      </div>

      {/* Brand Tagline Banner */}
      <div className="mb-5 px-3 py-1.5 rounded bg-[#141E2A] border border-[#263548] text-[10px] font-mono text-[#A0AEC0] text-center">
        Route smarter. Measure everything.
      </div>

      {/* Navigation section */}
      <div className="mb-2">
        <span className="text-[10px] font-mono font-semibold uppercase tracking-wider text-[#718096] px-3">
          Navigation
        </span>
      </div>
      <nav className="space-y-1 flex-1">
        {navLinks.map(({ to, label, icon: Icon, badge }) => (
          <NavLink
            key={to}
            to={to}
            end={to === '/'}
            className={({ isActive }) =>
              `flex items-center gap-2.5 px-3 py-2 rounded-md transition-all text-xs font-medium ${
                isActive
                  ? 'bg-[#192536] text-[#F1F5F9] border border-[#263548] shadow-xs'
                  : 'text-[#A0AEC0] hover:text-[#F1F5F9] hover:bg-[#141E2A]'
              }`
            }
          >
            <Icon className="w-3.5 h-3.5 text-[#A0AEC0]" />
            <span>{label}</span>
            {badge && (
              <span className={`ml-auto text-[9px] font-mono font-semibold px-1.5 py-0.5 rounded uppercase tracking-wider border ${
                badge === 'Live'
                  ? 'bg-[#34D399]/15 text-[#34D399] border-[#34D399]/30'
                  : 'bg-[#192536] text-[#A0AEC0] border-[#263548]'
              }`}>
                {badge}
              </span>
            )}
          </NavLink>
        ))}
      </nav>

      {/* Infrastructure status footer */}
      <div className="mt-auto pt-4 border-t border-[#263548] space-y-2">
        <div className="bg-[#141E2A] border border-[#263548] rounded-md p-3 text-xs">
          <div className="flex items-center justify-between mb-1.5">
            <div className="flex items-center gap-1.5">
              <span className={`w-2 h-2 rounded-full ${health?.has_api_key ? 'bg-[#34D399] animate-pulse' : 'bg-[#F59E0B]'}`} />
              <span className="font-mono text-[11px] font-semibold text-[#F1F5F9] uppercase tracking-wide">
                {health?.has_api_key ? 'Live Inference' : 'Demo Mode'}
              </span>
            </div>
            <span className="text-[10px] font-mono text-[#A0AEC0]">{health?.provider || 'Gemini'}</span>
          </div>
          <p className="text-[11px] text-[#A0AEC0] leading-snug font-sans">
            {health?.has_api_key
              ? 'Multi-tier routing connected to real Gemini API.'
              : 'Offline simulation mode: mock latencies & costs.'}
          </p>
          <div className="mt-2.5 pt-2 border-t border-[#263548] flex items-center justify-between text-[10px] font-mono text-[#718096]">
            <span>Classifier:</span>
            <span className={health?.model_trained ? 'text-[#34D399]' : 'text-[#F59E0B]'}>
              {health?.model_trained ? 'Trained (TF-IDF+LR)' : 'Untrained'}
            </span>
          </div>
        </div>
      </div>
    </div>
  );

  return (
    <div className="flex h-screen bg-[#0B0F14] text-[#F1F5F9] overflow-hidden font-sans selection:bg-[#3B82F6]/30">
      {/* Desktop Sidebar (Permanent on lg screens) */}
      <aside className="hidden lg:flex w-64 border-r border-[#263548] bg-[#101722] flex-col flex-shrink-0">
        {sidebarContent}
      </aside>

      {/* Mobile Drawer (Visible when mobileNavOpen is true) */}
      {mobileNavOpen && (
        <div className="fixed inset-0 z-50 lg:hidden flex">
          {/* Backdrop */}
          <div 
            className="fixed inset-0 bg-black/70 backdrop-blur-xs transition-opacity"
            onClick={() => setMobileNavOpen(false)}
            aria-hidden="true"
          />
          {/* Off-canvas sidebar */}
          <div className="relative w-72 max-w-[85vw] h-full z-10 border-r border-[#263548] shadow-2xl">
            {sidebarContent}
          </div>
        </div>
      )}

      {/* Main Canvas Area */}
      <div className="flex-1 flex flex-col h-screen overflow-hidden">
        {/* Top Navbar for mobile & tablet (displays brand and hamburger) */}
        <header className="lg:hidden flex items-center justify-between px-4 py-3 bg-[#101722] border-b border-[#263548] shrink-0">
          <div className="flex items-center gap-2.5">
            <button
              onClick={() => setMobileNavOpen(true)}
              className="p-1.5 rounded-md text-[#A0AEC0] hover:text-[#F1F5F9] hover:bg-[#192536] transition-colors"
              aria-label="Open navigation menu"
            >
              <Menu className="w-5 h-5" />
            </button>
            <div className="flex items-center gap-2">
              <span className="font-bold text-sm tracking-wider uppercase text-[#F1F5F9]">TIERFLOW</span>
              <span className="text-[9px] font-mono px-1 py-0.2 rounded bg-[#192536] text-[#A0AEC0] border border-[#263548]">v2.1</span>
            </div>
          </div>

          <div className="flex items-center gap-2">
            <span className={`inline-flex items-center gap-1 px-2 py-0.5 rounded text-[10px] font-mono border ${
              health?.has_api_key 
                ? 'bg-[#34D399]/10 text-[#34D399] border-[#34D399]/30' 
                : 'bg-[#192536] text-[#A0AEC0] border-[#263548]'
            }`}>
              <span className={`w-1.5 h-1.5 rounded-full ${health?.has_api_key ? 'bg-[#34D399]' : 'bg-[#F59E0B]'}`} />
              <span>{health?.has_api_key ? 'Live' : 'Demo'}</span>
            </span>
          </div>
        </header>

        {/* Scrollable Viewport */}
        <main className="flex-1 overflow-y-auto bg-[#0B0F14] text-[#F1F5F9]">
          <Routes>
            <Route path="/" element={<Dashboard demoMode={isDemo} />} />
            <Route path="/playground" element={<RouterPlayground />} />
            <Route path="/experiments" element={<Experiments />} />
            <Route path="/research" element={<ResearchResults />} />
          </Routes>
        </main>
      </div>
    </div>
  );
}

export default App;
