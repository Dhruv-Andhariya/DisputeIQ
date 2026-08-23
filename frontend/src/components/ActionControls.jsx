import React, { useState } from 'react';
import { UserCheck, ShieldAlert, CheckCircle, XCircle, Lock, ArrowRight, ShieldCheck, AlertOctagon } from 'lucide-react';
import StatusBadge from './StatusBadge';

export default function ActionControls({ decision, disputeStatus, onApprove, onReject }) {
  const [notes, setNotes] = useState('');
  const [loading, setLoading] = useState(false);

  const { final_decision, recommended_action, safety_override_triggered, override_reason, reasoning_summary } = decision;

  const handleApprove = async () => {
    setLoading(true);
    await onApprove(notes);
    setLoading(false);
  };

  const handleReject = async () => {
    setLoading(true);
    await onReject(notes);
    setLoading(false);
  };

  const isClosed = disputeStatus === 'CONTESTED' || disputeStatus === 'REJECTED';

  return (
    <div className="glass-panel rounded-2xl p-6 shadow-2xl space-y-6 relative overflow-hidden">
      
      {/* Accent Background Glow */}
      <div className="absolute -top-24 -right-24 w-60 h-60 rounded-full bg-blue-600/10 blur-3xl pointer-events-none" />

      {/* Decision Header */}
      <div className="flex flex-wrap items-center justify-between gap-4 border-b border-[#1b2a47] pb-5">
        <div>
          <div className="flex items-center space-x-2.5">
            <div className="p-2 rounded-xl bg-amber-500/10 border border-amber-500/30 text-amber-400">
              <UserCheck className="w-5 h-5" />
            </div>
            <h3 className="text-lg font-bold text-white tracking-tight">Decision Engine & Human Control Point</h3>
          </div>
          <p className="text-xs text-slate-400 font-mono mt-1">
            Bounded AI Decision Policy + Merchant Analyst Control Interface
          </p>
        </div>
        
        <div className="flex items-center space-x-3 bg-[#070b14]/80 px-4 py-2 rounded-xl border border-[#1b2a47]">
          <span className="text-xs font-mono text-slate-400">System Recommendation:</span>
          <StatusBadge status={final_decision} type="decision" />
        </div>
      </div>

      {/* Safety Override Alert (PRIMARY DEMO MOMENT CARD) */}
      {safety_override_triggered && (
        <div className="p-5 rounded-2xl bg-gradient-to-r from-rose-950/40 via-red-950/30 to-rose-950/40 border border-rose-500/60 shadow-glow-rose space-y-3 relative overflow-hidden">
          <div className="absolute top-0 right-0 px-3 py-1 bg-rose-500 text-white font-mono font-bold text-[10px] uppercase tracking-widest rounded-bl-xl shadow-md">
            AUTO-CONTEST BLOCKED
          </div>

          <div className="flex items-start space-x-3.5">
            <div className="p-2.5 rounded-xl bg-rose-500/20 text-rose-400 border border-rose-500/40 shrink-0">
              <ShieldAlert className="w-6 h-6 animate-pulse" />
            </div>
            <div className="space-y-1">
              <h4 className="text-sm font-bold text-rose-200 uppercase font-mono tracking-wider flex items-center space-x-2">
                <span>Deterministic Safety Override Triggered</span>
              </h4>
              <p className="text-xs text-rose-300 font-semibold leading-relaxed">{override_reason}</p>
              <p className="text-xs text-slate-300 font-sans leading-relaxed pt-1">
                Deterministic rules detected a critical data conflict. Even if the AI model suggests contesting, the safety rule overrides the final decision to <strong className="text-amber-300 font-mono">HUMAN_REVIEW</strong>.
              </p>
            </div>
          </div>
        </div>
      )}

      {/* Action Recommendation Box */}
      <div className="bg-[#070b14]/90 p-4.5 rounded-xl border border-[#1b2a47] space-y-2">
        <h4 className="text-[11px] font-bold uppercase tracking-wider text-slate-400 font-mono">
          Recommended Action Policy
        </h4>
        <p className="text-sm font-semibold text-slate-200">{recommended_action}</p>
        
        {reasoning_summary && reasoning_summary.length > 0 && (
          <div className="mt-3 pt-3 border-t border-[#1b2a47] space-y-1">
            {reasoning_summary.map((line, idx) => (
              <p key={idx} className="font-mono text-[11px] text-slate-400">{line}</p>
            ))}
          </div>
        )}
      </div>

      {/* Human Action Input */}
      {!isClosed ? (
        <div className="space-y-4 pt-2">
          <div>
            <label className="block text-xs font-mono font-semibold text-slate-300 mb-2">
              Human Analyst Case Notes & Audit Rationale
            </label>
            <textarea
              rows={2}
              value={notes}
              onChange={(e) => setNotes(e.target.value)}
              placeholder="Enter notes regarding evidence review, customer history, or approval rationale..."
              className="w-full bg-[#070b14] border border-[#1b2a47] rounded-xl p-3.5 text-xs text-slate-200 focus:outline-none focus:border-blue-500 font-sans transition-all placeholder:text-slate-600"
            />
          </div>

          <div className="flex flex-wrap items-center justify-between gap-4 pt-2">
            <div className="flex items-center space-x-2 text-xs font-mono text-slate-400">
              <Lock className="w-4 h-4 text-amber-400 shrink-0" />
              <span>Human approval required for financial submission</span>
            </div>

            <div className="flex items-center space-x-3">
              <button
                disabled={loading}
                onClick={handleReject}
                className="px-4 py-2.5 rounded-xl text-xs font-bold font-mono bg-[#152238] text-slate-300 border border-[#1b2a47] hover:bg-slate-800 hover:text-white transition-all disabled:opacity-50 flex items-center space-x-2 shadow-lg"
              >
                <XCircle className="w-4 h-4 text-slate-400" />
                <span>Reject / Accept Dispute</span>
              </button>

              <button
                disabled={loading}
                onClick={handleApprove}
                className="px-5 py-2.5 rounded-xl text-xs font-bold font-mono bg-gradient-to-r from-blue-600 via-indigo-600 to-blue-700 text-white shadow-glow-blue hover:brightness-110 transition-all disabled:opacity-50 flex items-center space-x-2 active:scale-95"
              >
                <CheckCircle className="w-4 h-4" />
                <span>Approve & Submit Contest</span>
                <ArrowRight className="w-4 h-4" />
              </button>
            </div>
          </div>
        </div>
      ) : (
        <div className="p-4 rounded-xl bg-emerald-500/10 border border-emerald-500/30 text-emerald-300 text-xs font-mono flex items-center justify-between shadow-lg">
          <div className="flex items-center space-x-2.5">
            <CheckCircle className="w-5 h-5 text-emerald-400" />
            <span>Human Analyst Action Completed. Status: <strong className="text-white">{disputeStatus}</strong></span>
          </div>
          <span className="text-[11px] text-slate-400 px-2.5 py-1 rounded bg-[#070b14] border border-[#1b2a47]">
            Mock Razorpay Logged
          </span>
        </div>
      )}
    </div>
  );
}
