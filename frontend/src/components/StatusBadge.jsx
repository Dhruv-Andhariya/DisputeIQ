import React from 'react';
import { CheckCircle2, AlertTriangle, XCircle, ShieldAlert, Clock, UserCheck, Zap } from 'lucide-react';

export default function StatusBadge({ status, type = 'status' }) {
  let colorClass = 'bg-slate-800/80 text-slate-300 border-slate-700';
  let Icon = Clock;
  let label = status;

  if (type === 'verification') {
    switch (status) {
      case 'PASSED':
        colorClass = 'bg-emerald-500/10 text-emerald-300 border-emerald-500/30 shadow-sm shadow-emerald-500/10';
        Icon = CheckCircle2;
        break;
      case 'FAILED':
        colorClass = 'bg-rose-500/10 text-rose-300 border-rose-500/40 shadow-sm shadow-rose-500/10';
        Icon = XCircle;
        break;
      case 'WARNING':
        colorClass = 'bg-amber-500/10 text-amber-300 border-amber-500/40 shadow-sm shadow-amber-500/10';
        Icon = AlertTriangle;
        break;
      default:
        colorClass = 'bg-slate-800/80 text-slate-400 border-slate-700';
        break;
    }
  } else if (type === 'decision' || type === 'recommendation') {
    switch (status) {
      case 'CONTEST':
        colorClass = 'bg-gradient-to-r from-emerald-500/20 to-teal-500/20 text-emerald-300 border-emerald-500/50 shadow-md shadow-emerald-500/20 font-bold';
        Icon = CheckCircle2;
        break;
      case 'DO_NOT_CONTEST':
        colorClass = 'bg-gradient-to-r from-rose-500/20 to-red-500/20 text-rose-300 border-rose-500/50 shadow-md shadow-rose-500/20 font-bold';
        Icon = XCircle;
        break;
      case 'HUMAN_REVIEW':
        colorClass = 'bg-gradient-to-r from-amber-500/20 to-orange-500/20 text-amber-300 border-amber-500/50 shadow-md shadow-amber-500/20 font-bold';
        Icon = UserCheck;
        label = 'HUMAN REVIEW REQUIRED';
        break;
      default:
        break;
    }
  } else if (type === 'evidence') {
    switch (status) {
      case 'VERIFIED':
        colorClass = 'bg-emerald-500/10 text-emerald-300 border-emerald-500/30';
        Icon = CheckCircle2;
        break;
      case 'CONTRADICTED':
        colorClass = 'bg-rose-500/15 text-rose-300 border-rose-500/50 font-bold shadow-sm shadow-rose-500/20 animate-pulse';
        Icon = ShieldAlert;
        break;
      case 'MISSING':
        colorClass = 'bg-rose-500/10 text-rose-300 border-rose-500/30';
        Icon = XCircle;
        break;
      case 'PARTIALLY_VERIFIED':
        colorClass = 'bg-amber-500/10 text-amber-300 border-amber-500/30';
        Icon = AlertTriangle;
        break;
      default:
        colorClass = 'bg-slate-800/80 text-slate-400 border-slate-700';
        break;
    }
  } else {
    // Dispute Status
    switch (status) {
      case 'OPEN':
        colorClass = 'bg-blue-500/10 text-blue-300 border-blue-500/30';
        Icon = Clock;
        break;
      case 'INVESTIGATING':
        colorClass = 'bg-indigo-500/15 text-indigo-300 border-indigo-500/40';
        Icon = Zap;
        break;
      case 'HUMAN_REVIEW':
        colorClass = 'bg-amber-500/15 text-amber-300 border-amber-500/50 font-bold shadow-sm shadow-amber-500/20';
        Icon = UserCheck;
        label = 'HUMAN REVIEW';
        break;
      case 'CONTESTED':
        colorClass = 'bg-emerald-500/15 text-emerald-300 border-emerald-500/40 font-bold';
        Icon = CheckCircle2;
        break;
      case 'REJECTED':
        colorClass = 'bg-slate-800 text-slate-400 border-slate-700';
        Icon = XCircle;
        break;
      default:
        break;
    }
  }

  return (
    <span className={`inline-flex items-center space-x-1.5 px-3 py-1 rounded-lg text-xs font-mono font-semibold border ${colorClass}`}>
      <Icon className="w-3.5 h-3.5 shrink-0" />
      <span>{label}</span>
    </span>
  );
}
