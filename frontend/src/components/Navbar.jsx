import React from 'react';
import { ShieldCheck, Cpu, Terminal, AlertTriangle, Zap, Sparkles, Layers } from 'lucide-react';

export default function Navbar({ activePage, setActivePage, onTriggerFailure, currentDisputeId }) {
  return (
    <nav className="sticky top-0 z-50 bg-[#070b14]/85 backdrop-blur-xl border-b border-[#1b2a47]/80 shadow-2xl">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          
          {/* Logo & Brand Identity */}
          <div 
            className="flex items-center space-x-3 cursor-pointer group" 
            onClick={() => setActivePage('list')}
          >
            <div className="relative w-10 h-10 rounded-xl bg-gradient-to-tr from-blue-600 via-indigo-600 to-cyan-500 p-0.5 shadow-lg shadow-blue-600/30 group-hover:shadow-blue-500/50 transition-all duration-300">
              <div className="w-full h-full bg-[#070b14] rounded-[10px] flex items-center justify-center">
                <ShieldCheck className="w-5 h-5 text-blue-400 group-hover:scale-110 transition-transform duration-300" />
              </div>
            </div>
            <div>
              <div className="flex items-center space-x-2">
                <span className="font-extrabold text-xl tracking-tight text-white group-hover:text-blue-400 transition-colors">
                  DisputeIQ
                </span>
                <span className="text-[10px] font-mono font-bold tracking-widest uppercase px-2 py-0.5 rounded-full bg-blue-500/10 text-blue-400 border border-blue-500/30">
                  AI Risk Manager
                </span>
              </div>
              <p className="text-[11px] text-slate-400 font-mono tracking-tight">
                Razorpay Evidence Intelligence Layer
              </p>
            </div>
          </div>

          {/* Architecture Philosophy Pill */}
          <div className="hidden lg:flex items-center space-x-2 px-3.5 py-1.5 rounded-full bg-[#0e1626] border border-[#1b2a47] text-xs font-mono shadow-inner">
            <span className="flex items-center space-x-1 text-emerald-400 font-semibold">
              <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse" />
              <span>CODE</span>
            </span>
            <span className="text-slate-600">=</span>
            <span className="text-slate-300">Correctness</span>
            <span className="text-slate-600">•</span>
            <span className="text-blue-400 font-semibold">AI</span>
            <span className="text-slate-600">=</span>
            <span className="text-slate-300">Reasoning</span>
            <span className="text-slate-600">•</span>
            <span className="text-amber-400 font-semibold">HUMAN</span>
            <span className="text-slate-600">=</span>
            <span className="text-slate-300">Judgment</span>
          </div>

          {/* Navigation & Action Controls */}
          <div className="flex items-center space-x-3">
            <button
              onClick={() => setActivePage('list')}
              className={`px-4 py-2 rounded-xl text-xs font-semibold font-mono tracking-wide transition-all ${
                activePage === 'list'
                  ? 'bg-gradient-to-r from-blue-600 to-indigo-600 text-white shadow-lg shadow-blue-600/30 border border-blue-400/30'
                  : 'text-slate-300 hover:bg-[#152238] hover:text-white border border-transparent'
              }`}
            >
              Dispute Dashboard
            </button>

            {currentDisputeId && (
              <button
                onClick={() => onTriggerFailure(currentDisputeId)}
                className="flex items-center space-x-1.5 px-3.5 py-2 rounded-xl text-xs font-semibold font-mono bg-rose-500/10 text-rose-300 border border-rose-500/40 hover:bg-rose-500/20 hover:border-rose-500/60 shadow-lg shadow-rose-950/40 transition-all active:scale-95"
                title="Demonstrate Scenario 3: External Carrier Logistics API Failure"
              >
                <AlertTriangle className="w-3.5 h-3.5 text-rose-400 animate-pulse" />
                <span>Simulate System Failure</span>
              </button>
            )}
          </div>

        </div>
      </div>
    </nav>
  );
}
