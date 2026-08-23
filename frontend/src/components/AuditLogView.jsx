import React from 'react';
import { Terminal, Shield, Clock, AlertTriangle, CheckCircle2, UserCheck, RefreshCw } from 'lucide-react';

export default function AuditLogView({ auditEvents }) {
  const getEventBadgeClass = (type) => {
    switch (type) {
      case 'EVIDENCE_CONFLICT':
      case 'API_FAILURE':
        return 'text-rose-400 bg-rose-500/10 border-rose-500/30';
      case 'EVIDENCE_VERIFIED':
      case 'HUMAN_APPROVED':
        return 'text-emerald-400 bg-emerald-500/10 border-emerald-500/30';
      case 'RETRY_ATTEMPT':
      case 'HUMAN_REVIEW_REQUESTED':
      case 'ESCALATED':
        return 'text-amber-400 bg-amber-500/10 border-amber-500/30';
      default:
        return 'text-blue-400 bg-blue-500/10 border-blue-500/30';
    }
  };

  return (
    <div className="bg-slate-900 border border-slate-800 rounded-xl p-5 shadow-xl">
      <div className="flex items-center justify-between mb-4">
        <div>
          <h3 className="text-base font-bold text-slate-100 flex items-center space-x-2">
            <Terminal className="w-5 h-5 text-emerald-400" />
            <span>Immutable Audit Trail</span>
          </h3>
          <p className="text-xs text-slate-400 font-mono mt-0.5">
            Full compliance audit log recorded in database
          </p>
        </div>
        <span className="text-xs font-mono px-2.5 py-1 rounded bg-slate-800 text-slate-300 border border-slate-700">
          {auditEvents.length} Events Logged
        </span>
      </div>

      <div className="space-y-2.5 max-h-72 overflow-y-auto pr-1">
        {auditEvents.map((evt) => (
          <div
            key={evt.event_id}
            className="p-3 rounded-lg bg-slate-950/70 border border-slate-800/80 text-xs font-mono space-y-1"
          >
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-2">
                <span className={`px-2 py-0.5 rounded text-[10px] font-bold border ${getEventBadgeClass(evt.event_type)}`}>
                  {evt.event_type}
                </span>
                <span className="text-slate-500 text-[10px]">{evt.event_id}</span>
              </div>
              <span className="text-slate-400 text-[11px]">{evt.timestamp}</span>
            </div>
            
            <p className="text-slate-300 font-sans text-xs pt-0.5">{evt.description}</p>
            
            {evt.metadata && Object.keys(evt.metadata).length > 0 && (
              <div className="text-[10px] text-slate-400 bg-slate-900/60 p-1.5 rounded border border-slate-800/50 mt-1">
                <pre>{JSON.stringify(evt.metadata)}</pre>
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}
