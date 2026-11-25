import React from 'react';
import { ArrowRight, CheckCircle2, ChevronRight, Cpu, Database, Sparkles, Terminal, Circle, Loader2 } from 'lucide-react';

export function PipelineFlow({ selectedTier, inFlight = false, hasResponse = false }) {
  const tierColor = {
    SMALL: '#34D399',
    MEDIUM: '#F59E0B',
    LARGE: '#818CF8'
  }[selectedTier] || '#3B82F6';

  // Determine stage status: 'completed' | 'active' | 'pending'
  const getStageStatus = (stageId) => {
    if (stageId === 1) {
      // 01 USER QUERY
      return selectedTier ? 'completed' : 'active';
    }
    if (stageId === 2) {
      // 02 FEATURE EXTRACTION
      return selectedTier ? 'completed' : 'pending';
    }
    if (stageId === 3) {
      // 03 ML CLASSIFIER
      return selectedTier ? 'completed' : 'pending';
    }
    if (stageId === 4) {
      // 04 TIER SELECTION
      if (!selectedTier) return 'pending';
      return (inFlight || hasResponse) ? 'completed' : 'active';
    }
    if (stageId === 5) {
      // 05 LLM INFERENCE
      if (inFlight) return 'active';
      if (hasResponse) return 'completed';
      return 'pending';
    }
    if (stageId === 6) {
      // 06 RESPONSE
      if (hasResponse) return 'completed';
      return 'pending';
    }
    return 'pending';
  };

  const steps = [
    { id: 1, label: 'USER QUERY', sub: 'Input Prompt', status: getStageStatus(1) },
    { id: 2, label: 'FEATURE EXTRACTION', sub: selectedTier ? 'Lexical Extracted' : 'Standby', status: getStageStatus(2) },
    { id: 3, label: 'ML CLASSIFIER', sub: selectedTier ? 'Softmax Logits' : 'Standby', status: getStageStatus(3) },
    { 
      id: 4, 
      label: 'TIER SELECTION', 
      sub: selectedTier ? `${selectedTier} Tier` : 'Awaiting Route', 
      status: getStageStatus(4),
      isTierNode: true
    },
    { 
      id: 5, 
      label: 'LLM INFERENCE', 
      sub: inFlight ? 'Generating...' : (hasResponse ? 'Executed' : 'Standby'), 
      status: getStageStatus(5) 
    },
    { 
      id: 6, 
      label: 'RESPONSE', 
      sub: hasResponse ? 'Output Formatted' : 'Standby', 
      status: getStageStatus(6) 
    }
  ];

  return (
    <div className="bg-[#101722] border border-[#263548] rounded-md p-4 overflow-hidden">
      <div className="flex flex-wrap items-center justify-between gap-2 mb-3 text-[10px] font-mono uppercase tracking-wider text-[#718096]">
        <div className="flex items-center gap-2">
          <span>Adaptive Routing Pipeline</span>
          <span className="text-[#3E4F63]">|</span>
          <span className="text-[#A0AEC0]">Multi-Tier Execution Trace</span>
        </div>
        <div className="flex items-center gap-3 text-[10px]">
          <span className="flex items-center gap-1.5">
            <span className="w-2 h-2 rounded-full bg-[#34D399]" />
            <span className="text-[#A0AEC0]">Completed</span>
          </span>
          <span className="flex items-center gap-1.5">
            <span className="w-2 h-2 rounded-full bg-[#3B82F6] animate-pulse" />
            <span className="text-[#A0AEC0]">Active</span>
          </span>
          <span className="flex items-center gap-1.5">
            <span className="w-2 h-2 rounded-full bg-[#263548]" />
            <span className="text-[#718096]">Pending</span>
          </span>
        </div>
      </div>

      {/* Pipeline Grid: 2 cols on mobile, 3 cols on tablet, 6 cols on desktop */}
      <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-2 text-xs font-mono">
        {steps.map((step) => {
          const isCompleted = step.status === 'completed';
          const isActive = step.status === 'active';
          const isPending = step.status === 'pending';
          const isTierNode = step.isTierNode && selectedTier;

          return (
            <div
              key={step.id}
              className={`relative flex flex-col justify-between p-2.5 rounded border transition-all ${
                isTierNode
                  ? 'border-opacity-90 bg-opacity-20 shadow-sm'
                  : isCompleted
                  ? 'bg-[#141E2A] border-[#34D399]/40 text-[#F1F5F9]'
                  : isActive
                  ? 'bg-[#141E2A] border-[#3B82F6] text-[#F1F5F9] shadow-sm'
                  : 'bg-[#0D141D] border-[#1E2A39] text-[#718096] opacity-60'
              }`}
              style={isTierNode ? {
                borderColor: tierColor,
                backgroundColor: `${tierColor}18`,
                color: tierColor
              } : {}}
            >
              <div className="flex items-center justify-between mb-1.5">
                <span className="text-[9px] font-semibold text-[#718096]">{`0${step.id}`}</span>
                
                {/* Status indicator icon */}
                {isCompleted && (
                  <CheckCircle2 className="w-3 h-3 text-[#34D399]" />
                )}
                {isActive && (
                  inFlight && step.id === 5 
                    ? <Loader2 className="w-3 h-3 text-[#3B82F6] animate-spin" />
                    : <span className="w-2 h-2 rounded-full bg-[#3B82F6] animate-pulse" 
                        style={isTierNode ? { backgroundColor: tierColor } : {}} 
                      />
                )}
                {isPending && (
                  <span className="w-1.5 h-1.5 rounded-full bg-[#263548]" />
                )}
              </div>

              <div>
                <div className={`font-semibold text-[10px] tracking-tight truncate ${
                  isCompleted ? 'text-[#F1F5F9]' : isActive ? 'text-white' : 'text-[#718096]'
                }`}>
                  {step.label}
                </div>
                <div className={`text-[10px] truncate ${
                  isTierNode ? 'font-bold' : isCompleted ? 'text-[#34D399]' : isActive ? 'text-[#3B82F6]' : 'text-[#718096]'
                }`}>
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
