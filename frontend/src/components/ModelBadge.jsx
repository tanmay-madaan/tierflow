import React from 'react';

export function ModelBadge({ model, size = 'sm', className = '' }) {
  const modelUpper = (model || '').toUpperCase();
  
  let badgeStyle = 'text-[#A0AEC0] border-[#263548] bg-[#141E2A]';
  let dotColor = 'bg-[#718096]';
  let displayName = modelUpper || 'UNKNOWN';

  if (modelUpper === 'SMALL') {
    badgeStyle = 'text-[#34D399] border-[#34D399]/40 bg-[#34D399]/10';
    dotColor = 'bg-[#34D399]';
    displayName = 'Small';
  } else if (modelUpper === 'MEDIUM') {
    badgeStyle = 'text-[#F59E0B] border-[#F59E0B]/40 bg-[#F59E0B]/10';
    dotColor = 'bg-[#F59E0B]';
    displayName = 'Medium';
  } else if (modelUpper === 'LARGE') {
    badgeStyle = 'text-[#818CF8] border-[#818CF8]/40 bg-[#818CF8]/10';
    dotColor = 'bg-[#818CF8]';
    displayName = 'Large';
  }

  const sizeClasses = size === 'lg'
    ? 'px-3 py-1 text-xs font-semibold'
    : 'px-2 py-0.5 text-[11px] font-medium';

  return (
    <span className={`inline-flex items-center gap-1.5 rounded border font-mono tracking-wider uppercase ${sizeClasses} ${badgeStyle} ${className}`}>
      <span className={`w-1.5 h-1.5 rounded-full ${dotColor}`} />
      <span>{displayName}</span>
    </span>
  );
}
