import React from 'react';
import { ArrowRight, CheckCircle2, ChevronRight, Cpu, Database, Sparkles, Terminal } from 'lucide-react';

export function PipelineFlow({ selectedTier, inFlight = false, hasResponse = false }) {
  const tierColor = {
    SMALL: '#34D399',
    MEDIUM: '#F59E0B',
    LARGE: '#818CF8'
  }[selectedTier] || '#3B82F6';

  const steps = [
    { id: 1, label: 'USER QUERY', sub: 'Input Prompt', active: true },
    { id: 2, label: 'FEATURE EXTRACTION', sub: 'Lexical & Syntax', active: Boolean(selectedTier) },
    { id: 3, label: 'ML CLASSIFIER', sub: 'Confidence / Logits', active: Boolean(selectedTier) },
    { 
      id: 4, 
      label: 'TIER SELECTION', 
      sub: selectedTier ? selectedTier : 'Awaiting Route', 
      active: Boolean(selectedTier),
      highlight: true
    },
    { id: 5, label: 'LLM INFERENCE', sub: inFlight ? 'In Flight...' : (hasResponse ? 'Executed' : 'Standby'), active: inFlight || hasResponse },
    { id: 6, label: 'RESPONSE', sub: hasResponse ? 'Output Formatted' : 'Standby', active: hasResponse }
  ];

  return (
    <div className="bg-[#101722] border border-[#263548] rounded-md p-4 overflow-hidden">
      <div className="flex items-center justify-between mb-3 text-[10px] font-mono uppercase tracking-wider text-[#718096]">
        <span>Adaptive Routing Pipeline</span>
        <span className="flex items-center gap-1.5">
          <span className="w-1.5 h-1.5 rounded-full bg-[#3B82F6]" />
          <span>Multi-Tier Architecture</span>
        </span>
      </div>

      {/* Pipeline Container (Horizontal desktop, wrap/vertical mobile) */}
      <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-2 text-xs font-mono">
        {steps.map((step, idx) => {
          const isHighlighted = step.highlight && selectedTier;
          return (
            <div
              key={step.id}
              className={`relative flex flex-col justify-between p-2.5 rounded border transition-all ${
                isHighlighted
                  ? 'border-opacity-80 bg-opacity-15 shadow-sm'
                  : step.active
                  ? 'bg-[#141E2A] border-[#263548] text-[#F1F5F9]'
                  : 'bg-[#0D141D] border-[#1E2A39] text-[#718096] opacity-60'
              }`}
              style={isHighlighted ? {
                borderColor: tierColor,
                backgroundColor: `${tierColor}15`,
                color: tierColor
              } : {}}
            >
              <div className="flex items-center justify-between mb-1.5">
                <span className="text-[9px] font-semibold text-[#718096]">{`0${step.id}`}</span>
                {step.active && (
                  <span className={`w-1.5 h-1.5 rounded-full ${isHighlighted ? 'animate-pulse' : 'bg-[#3B82F6]'}`} 
                    style={isHighlighted ? { backgroundColor: tierColor } : {}}
                  />
                )}
              </div>
              <div>
                <div className="font-semibold text-[10px] tracking-tight truncate">
                  {step.label}
                </div>
                <div className={`text-[10px] truncate ${isHighlighted ? 'font-bold' : 'text-[#A0AEC0]'}`}>
                  {step.sub}
                </div>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
