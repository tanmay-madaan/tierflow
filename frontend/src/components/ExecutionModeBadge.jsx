import React from 'react';
import { Activity, ShieldCheck, AlertTriangle } from 'lucide-react';

export function ExecutionModeBadge({ mode, className = '' }) {
  const m = (mode || '').toLowerCase();
  const isReal = m === 'real' || m === 'live';
  const isEstimated = m === 'estimated';
  const isError = m === 'error' || m === 'failed';

  let badgeClass = 'bg-[#141E2A] text-[#A0AEC0] border-[#263548]';
  let dotClass = 'bg-[#718096]';
  let label = 'Simulated (Demo)';

  if (isReal) {
    badgeClass = 'bg-[#34D399]/10 text-[#34D399] border-[#34D399]/30';
    dotClass = 'bg-[#34D399] animate-pulse';
    label = 'Live API';
  } else if (isEstimated) {
    badgeClass = 'bg-[#F59E0B]/10 text-[#F59E0B] border-[#F59E0B]/30';
    dotClass = 'bg-[#F59E0B]';
    label = 'Projected Est.';
  } else if (isError) {
    badgeClass = 'bg-[#EF4444]/10 text-[#EF4444] border-[#EF4444]/30';
    dotClass = 'bg-[#EF4444]';
    label = 'Failed';
  }

  return (
    <span className={`inline-flex items-center gap-1.5 px-2 py-0.5 rounded border text-[10px] font-mono font-medium tracking-wide ${badgeClass} ${className}`}>
      <span className={`w-1.5 h-1.5 rounded-full ${dotClass}`} />
      <span>{label}</span>
    </span>
  );
}
