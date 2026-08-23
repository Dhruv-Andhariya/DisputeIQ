import React from 'react';
import { Cpu, CheckCircle, AlertTriangle, ShieldAlert, Sparkles, HelpCircle, Layers } from 'lucide-react';
import StatusBadge from './StatusBadge';

export default function AIReasoningCard({ aiAnalysis, decision }) {
  if (!aiAnalysis) {
    return (
      <div className="glass-panel rounded-2xl p-6 shadow-2xl text-center">
        <Cpu className="w-8 h-8 text-slate-600 mx-auto mb-2 animate-pulse" />
        <p className="text-sm text-slate-400 font-mono">AI Investigation pending or unavailable.</p>
      </div>
    );
  }

  const { recommendation, confidence, case_summary, reasoning, supporting_evidence, missing_evidence, risk_flags } = aiAnalysis;
  const confPct = Math.round(confidence * 100);

  return (
    <div className="glass-panel rounded-2xl p-6 shadow-2xl space-y-5 relative overflow-hidden">
      
      {/* Accent Background Glow */}
      <div className="absolute -bottom-24 -left-24 w-60 h-60 rounded-full bg-indigo-600/10 blur-3xl pointer-events-none" />

      {/* Header */}
      <div className="flex flex-wrap items-center justify-between gap-4 border-b border-[#1b2a47] pb-4">
        <div className="flex items-center space-x-3">
          <div className="p-2.5 rounded-xl bg-gradient-to-tr from-indigo-600 via-purple-600 to-pink-500 text-white shadow-lg shadow-indigo-500/20">
            <Sparkles className="w-5 h-5" />
          </div>
          <div>
            <h3 className="text-base font-bold text-white flex items-center space-x-2">
              <span>AI Evidence Investigation & Reasoning</span>
            </h3>
            <p className="text-xs text-slate-400 font-mono mt-0.5">
              Structured LLM Synthesis over Verified Context
            </p>
          </div>
        </div>

        <div className="flex items-center space-x-4">
          <div className="text-right font-mono bg-[#070b14]/80 px-3.5 py-1.5 rounded-xl border border-[#1b2a47]">
            <div className="text-[10px] uppercase text-slate-400 font-bold">AI Confidence</div>
            <div className="text-base font-black text-blue-400">{confPct}%</div>
          </div>
          <StatusBadge status={recommendation} type="recommendation" />
        </div>
      </div>

      {/* Case Summary Box */}
      <div className="bg-[#070b14]/90 p-4.5 rounded-xl border border-[#1b2a47]">
        <h4 className="text-[11px] font-bold uppercase tracking-wider text-slate-400 font-mono mb-1.5 flex items-center space-x-1.5">
          <Layers className="w-3.5 h-3.5 text-blue-400" />
          <span>Executive Case Summary</span>
        </h4>
        <p className="text-xs text-slate-200 leading-relaxed font-sans font-normal">{case_summary}</p>
      </div>

      {/* Grid: Reasoning vs Evidence/Risk */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        
        {/* Reasoning Points */}
        <div className="bg-[#070b14]/70 p-4 rounded-xl border border-[#1b2a47]">
          <h4 className="text-[11px] font-bold uppercase tracking-wider text-slate-400 font-mono mb-3 flex items-center space-x-1.5">
            <Cpu className="w-3.5 h-3.5 text-indigo-400" />
            <span>AI Reasoning Logic</span>
          </h4>
          <ul className="space-y-2 text-xs text-slate-300">
            {reasoning.map((point, idx) => (
              <li key={idx} className="flex items-start space-x-2">
                <span className="text-indigo-400 font-bold">•</span>
                <span className="leading-relaxed">{point}</span>
              </li>
            ))}
          </ul>
        </div>

        {/* Risk Flags & Missing Evidence */}
        <div className="space-y-3">
          {risk_flags.length > 0 && (
            <div className="bg-rose-950/20 p-4 rounded-xl border border-rose-500/30">
              <h4 className="text-[11px] font-bold uppercase tracking-wider text-rose-400 font-mono mb-2 flex items-center space-x-1.5">
                <ShieldAlert className="w-3.5 h-3.5" />
                <span>Detected Risk Flags</span>
              </h4>
              <ul className="space-y-1.5 text-xs text-rose-300 font-medium">
                {risk_flags.map((flag, idx) => (
                  <li key={idx} className="flex items-start space-x-1.5">
                    <span className="text-rose-400">•</span>
                    <span>{flag}</span>
                  </li>
                ))}
              </ul>
            </div>
          )}

          {missing_evidence.length > 0 && (
            <div className="bg-amber-950/20 p-3.5 rounded-xl border border-amber-500/30">
              <h4 className="text-[11px] font-bold uppercase tracking-wider text-amber-400 font-mono mb-2 flex items-center space-x-1.5">
                <HelpCircle className="w-3.5 h-3.5" />
                <span>Missing Evidence Items</span>
              </h4>
              <ul className="space-y-1 text-xs text-amber-300">
                {missing_evidence.map((item, idx) => (
                  <li key={idx}>• {item}</li>
                ))}
              </ul>
            </div>
          )}

          {supporting_evidence.length > 0 && (
            <div className="bg-emerald-950/20 p-3.5 rounded-xl border border-emerald-500/20">
              <h4 className="text-[11px] font-bold uppercase tracking-wider text-emerald-400 font-mono mb-2 flex items-center space-x-1.5">
                <CheckCircle className="w-3.5 h-3.5" />
                <span>Supporting Evidence</span>
              </h4>
              <ul className="space-y-1 text-xs text-emerald-300">
                {supporting_evidence.map((ev, idx) => (
                  <li key={idx}>• {ev}</li>
                ))}
              </ul>
            </div>
          )}
        </div>

      </div>
    </div>
  );
}
