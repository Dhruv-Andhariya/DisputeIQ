import React from 'react';
import { Gauge, Info } from 'lucide-react';

export default function ReadinessGauge({ readinessScore }) {
  const { total_score, components, summary } = readinessScore;

  let gaugeColor = 'text-emerald-400 border-emerald-500/40 bg-emerald-500/10';
  if (total_score < 55) {
    gaugeColor = 'text-rose-400 border-rose-500/40 bg-rose-500/10';
  } else if (total_score < 75) {
    gaugeColor = 'text-amber-400 border-amber-500/40 bg-amber-500/10';
  }

  return (
    <div className="bg-slate-900 border border-slate-800 rounded-xl p-5 shadow-xl">
      <div className="flex items-center justify-between mb-4">
        <div>
          <h3 className="text-base font-bold text-slate-100 flex items-center space-x-2">
            <Gauge className="w-5 h-5 text-blue-400" />
            <span>Evidence Readiness Score</span>
          </h3>
          <p className="text-xs text-slate-400 font-mono mt-0.5">
            Decomposable strength metric for merchant defense package
          </p>
        </div>
        <div className={`px-4 py-1.5 rounded-xl border font-mono font-black text-xl ${gaugeColor}`}>
          {total_score}<span className="text-xs font-normal text-slate-400">/100</span>
        </div>
      </div>

      <p className="text-xs font-medium text-slate-300 bg-slate-950 p-3 rounded-lg border border-slate-800/80 mb-4">
        {summary}
      </p>

      {/* Breakdown progress bars */}
      <div className="space-y-3.5">
        {components.map((comp, idx) => {
          const pct = Math.round((comp.score / comp.max_score) * 100);
          let barColor = 'bg-emerald-500';
          if (pct < 50) barColor = 'bg-rose-500';
          else if (pct < 75) barColor = 'bg-amber-500';

          return (
            <div key={idx} className="space-y-1">
              <div className="flex items-center justify-between text-xs font-mono">
                <span className="text-slate-300 font-medium">{comp.name}</span>
                <span className="text-slate-400">
                  <strong className="text-white">{comp.score}</strong> / {comp.max_score} pts ({pct}%)
                </span>
              </div>
              
              <div className="w-full h-2 rounded-full bg-slate-950 overflow-hidden border border-slate-800">
                <div
                  className={`h-full rounded-full transition-all duration-500 ${barColor}`}
                  style={{ width: `${pct}%` }}
                />
              </div>
              
              <p className="text-[11px] text-slate-400 font-sans">{comp.explanation}</p>
            </div>
          );
        })}
      </div>
    </div>
  );
}
