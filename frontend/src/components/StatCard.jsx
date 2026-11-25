import React from 'react';

export function StatCard({ 
  title, 
  value, 
  icon: Icon, 
  subtitle, 
  trend, 
  trendValue,
  badge, 
  badgeColor = 'default',
  dataSource,
  className = ''
}) {
  // If value is null, undefined, or empty, render N/A
  const isAvailable = value !== null && value !== undefined && value !== '' && value !== 'N/A' && value !== '—';
  const displayValue = isAvailable ? value : 'N/A';

  const badgeStyles = {
    default: 'bg-[#192536] text-[#A0AEC0] border-[#263548]',
    success: 'bg-[#34D399]/10 text-[#34D399] border-[#34D399]/30',
    warning: 'bg-[#F59E0B]/10 text-[#F59E0B] border-[#F59E0B]/30',
    blue: 'bg-[#3B82F6]/10 text-[#3B82F6] border-[#3B82F6]/30',
  };

  return (
    <div className={`bg-[#141E2A] border border-[#263548] rounded-md p-4 flex flex-col justify-between hover:border-[#3B82F6]/40 transition-colors ${className}`}>
      <div className="flex items-center justify-between mb-2">
        <span className="text-[11px] font-mono font-semibold tracking-wider uppercase text-[#A0AEC0] truncate">
          {title}
        </span>
        <div className="flex items-center gap-1.5 shrink-0">
          {dataSource && (
            <span className="text-[9px] font-mono px-1.5 py-0.5 rounded bg-[#101722] text-[#718096] border border-[#1E2A39]">
              {dataSource}
            </span>
          )}
          {badge && (
            <span className={`text-[10px] font-mono px-1.5 py-0.5 rounded border ${badgeStyles[badgeColor] || badgeStyles.default}`}>
              {badge}
            </span>
          )}
          {Icon && !badge && <Icon className="w-3.5 h-3.5 text-[#718096]" />}
        </div>
      </div>

      <div>
        <div className="text-2xl font-mono font-semibold text-[#F1F5F9] tracking-tight">
          {displayValue}
        </div>
        {subtitle && (
          <div className="flex items-center gap-1.5 mt-2 text-xs text-[#A0AEC0] font-sans">
            {isAvailable && trend && (
              <span className={`font-mono font-medium ${trend === 'up' ? 'text-[#34D399]' : trend === 'down' ? 'text-[#F59E0B]' : 'text-[#718096]'}`}>
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
