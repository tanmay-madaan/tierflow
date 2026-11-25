import React from 'react';
import { Inbox, AlertCircle, RefreshCw } from 'lucide-react';

export function EmptyState({ 
  title = "No data available", 
  message = "No records or metrics have been recorded yet.", 
  actionLabel, 
  onAction,
  icon: Icon = Inbox,
  className = "" 
}) {
  return (
    <div className={`flex flex-col items-center justify-center p-8 text-center bg-[#101722] border border-[#263548] rounded-md ${className}`}>
      <div className="w-10 h-10 rounded-full bg-[#141E2A] border border-[#263548] flex items-center justify-center text-[#718096] mb-3">
        <Icon className="w-5 h-5 text-[#A0AEC0]" />
      </div>
      <h3 className="text-sm font-semibold font-mono text-[#F1F5F9] mb-1">
        {title}
      </h3>
      <p className="text-xs text-[#718096] max-w-md font-sans mb-4">
        {message}
      </p>
      {actionLabel && onAction && (
        <button
          onClick={onAction}
          className="px-3 py-1.5 rounded-md text-xs font-mono font-medium text-[#F1F5F9] bg-[#192536] hover:bg-[#263548] border border-[#263548] transition-colors"
        >
          {actionLabel}
        </button>
      )}
    </div>
  );
}
