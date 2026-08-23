import React from 'react';
import { ShieldCheck, AlertTriangle, XCircle, CheckCircle2, Terminal } from 'lucide-react';
import StatusBadge from './StatusBadge';

export default function VerificationList({ verificationResults }) {
  return (
    <div className="glass-panel rounded-2xl p-6 shadow-2xl space-y-5">
      <div className="flex items-center justify-between border-b border-[#1b2a47] pb-4">
        <div>
          <h3 className="text-base font-bold text-white flex items-center space-x-2.5">
            <div className="p-2 rounded-xl bg-emerald-500/10 border border-emerald-500/30 text-emerald-400">
              <ShieldCheck className="w-5 h-5" />
            </div>
            <span>Deterministic Verification Engine Output</span>
          </h3>
          <p className="text-xs text-slate-400 font-mono mt-1">
            Hard factual consistency checks executed prior to AI reasoning
          </p>
        </div>
        <span className="text-xs font-mono px-3 py-1 rounded-full bg-[#070b14] text-slate-300 border border-[#1b2a47]">
          9 Deterministic Rules Executed
        </span>
      </div>

      <div className="space-y-3.5">
        {verificationResults.map((item, idx) => {
          const isFailed = item.status === 'FAILED';
          const isWarning = item.status === 'WARNING';
          const isCritical = item.severity === 'CRITICAL' || item.severity === 'HIGH';

          return (
            <div
              key={idx}
              className={`p-4 rounded-xl border transition-all ${
                isFailed
                  ? 'bg-rose-950/20 border-rose-500/50 shadow-glow-rose'
                  : isWarning
                  ? 'bg-amber-950/20 border-amber-500/40 shadow-glow-amber'
                  : 'bg-[#070b14]/70 border-[#1b2a47] hover:border-slate-700'
              }`}
            >
              <div className="flex flex-wrap items-center justify-between gap-2">
                <div className="flex items-center space-x-3">
                  {isFailed ? (
                    <XCircle className="w-5 h-5 text-rose-400 shrink-0" />
                  ) : isWarning ? (
                    <AlertTriangle className="w-5 h-5 text-amber-400 shrink-0" />
                  ) : (
                    <CheckCircle2 className="w-5 h-5 text-emerald-400 shrink-0" />
                  )}
                  <div>
                    <h4 className="text-xs font-bold font-mono text-slate-200 uppercase tracking-wider">
                      {item.check.replace(/_/g, ' ')}
                    </h4>
                    <span className="text-[11px] font-mono text-slate-400">
                      Severity: <strong className={isCritical ? 'text-rose-400' : 'text-slate-300'}>{item.severity}</strong>
                    </span>
                  </div>
                </div>
                <StatusBadge status={item.status} type="verification" />
              </div>

              <p className={`mt-2.5 text-xs ${isFailed ? 'text-rose-300 font-semibold' : isWarning ? 'text-amber-300 font-medium' : 'text-slate-300'}`}>
                {item.message}
              </p>

              {/* Expected vs Actual Comparison Pills */}
              <div className="mt-3 pt-2.5 border-t border-[#1b2a47]/60 flex flex-wrap items-center gap-3 text-xs font-mono">
                <div className="bg-[#070b14] px-3 py-1 rounded-lg border border-[#1b2a47]">
                  <span className="text-slate-500">Expected: </span>
                  <span className="text-emerald-400 font-semibold">{String(item.expected)}</span>
                </div>
                <div className="bg-[#070b14] px-3 py-1 rounded-lg border border-[#1b2a47]">
                  <span className="text-slate-500">Actual: </span>
                  <span className={isFailed ? 'text-rose-400 font-semibold' : isWarning ? 'text-amber-400 font-semibold' : 'text-slate-200'}>
                    {String(item.actual)}
                  </span>
                </div>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
