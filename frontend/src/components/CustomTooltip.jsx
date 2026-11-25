import React from 'react';

export function CustomTooltip({ active, payload, label }) {
  if (active && payload && payload.length) {
    return (
      <div className="bg-[#141E2A] border border-[#263548] rounded-md px-3 py-2 text-xs font-mono shadow-xl z-50">
        <p className="text-[#A0AEC0] mb-1 font-semibold">{label || payload[0]?.name}</p>
        {payload.map((entry, idx) => (
          <p key={idx} className="font-semibold text-[#F1F5F9] text-[11px] flex items-center gap-1.5">
            <span 
              className="w-2 h-2 rounded-full inline-block shrink-0" 
              style={{ backgroundColor: entry.color || entry.fill || '#3B82F6' }} 
            />
            <span className="text-[#A0AEC0]">{entry.name}:</span>
            <span className="text-[#F1F5F9]">{entry.value}</span>
          </p>
        ))}
      </div>
    );
  }
  return null;
}
