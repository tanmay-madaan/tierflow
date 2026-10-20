import React from 'react';

export function StatCard({ title, value, icon: Icon, subtitle, trend, badge }) {
  return (
    <div className="bg-[#121923] border border-[#293545] rounded-md p-4 flex flex-col justify-between hover:border-[#3B82F6]/50 transition-colors">
      <div className="flex items-center justify-between mb-2">
        <span className="text-[11px] font-semibold tracking-wider uppercase text-[#94A3B8]">{title}</span>
        {badge && (
          <span className="text-[10px] font-mono px-1.5 py-0.5 rounded bg-[#1A2431] text-[#94A3B8] border border-[#293545]">
            {badge}
          </span>
        )}
        {Icon && !badge && <Icon className="w-3.5 h-3.5 text-[#94A3B8]" />}
      </div>
      <div>
        <div className="text-2xl font-mono font-semibold text-[#F1F5F9] tracking-tight">{value}</div>
        {subtitle && (
          <div className="flex items-center gap-1.5 mt-1.5 text-xs text-[#94A3B8]">
            {trend && (
              <span className={`font-mono font-medium ${trend === 'up' ? 'text-[#34D399]' : trend === 'down' ? 'text-amber-400' : 'text-[#94A3B8]'}`}>
                {trend === 'up' ? '↑' : trend === 'down' ? '↓' : '•'}
              </span>
            )}
            <span className="truncate">{subtitle}</span>
          </div>
        )}
      </div>
    </div>
  );
}
