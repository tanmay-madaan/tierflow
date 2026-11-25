import React from 'react';

export function PageHeader({ 
  title, 
  subtitle, 
  badge = 'Adaptive LLM Inference',
  statusPill,
  actions 
}) {
  return (
    <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-4 border-b border-[#263548]">
      <div>
        <div className="flex items-center gap-2.5 mb-1.5">
          <h1 className="text-xl font-bold tracking-tight text-[#F1F5F9]">
            {title}
          </h1>
          {badge && (
            <span className="text-[10px] font-mono uppercase px-2 py-0.5 rounded bg-[#192536] text-[#A0AEC0] border border-[#263548]">
              {badge}
            </span>
          )}
        </div>
        {subtitle && (
          <p className="text-xs text-[#A0AEC0] leading-relaxed max-w-2xl font-sans">
            {subtitle}
          </p>
        )}
      </div>

      <div className="flex flex-wrap items-center gap-2.5 shrink-0">
        {statusPill}
        {actions}
      </div>
    </div>
  );
}
