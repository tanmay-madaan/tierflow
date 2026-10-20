import React from 'react';

export function ModelBadge({ model, className = '' }) {
  const modelUpper = (model || '').toUpperCase();
  let badgeStyle = 'text-[#94A3B8] border-[#293545] bg-[#121923]';
  let dotColor = 'bg-[#94A3B8]';

  if (modelUpper === 'SMALL') {
    badgeStyle = 'text-[#34D399] border-[#34D399]/40 bg-[#34D399]/10';
    dotColor = 'bg-[#34D399]';
  } else if (modelUpper === 'MEDIUM') {
    badgeStyle = 'text-amber-400 border-amber-500/40 bg-amber-500/10';
    dotColor = 'bg-amber-400';
  } else if (modelUpper === 'LARGE') {
    badgeStyle = 'text-indigo-400 border-indigo-500/40 bg-indigo-500/10';
    dotColor = 'bg-indigo-400';
  }

  return (
    <span className={`inline-flex items-center gap-1.5 px-2 py-0.5 rounded border text-[11px] font-mono font-semibold tracking-wider uppercase ${badgeStyle} ${className}`}>
      <span className={`w-1.5 h-1.5 rounded-full ${dotColor}`} />
      {modelUpper}
    </span>
  );
}
