import React, { useState, useEffect } from 'react';
import { fetchDisputes, fetchEvaluationSummary } from '../api';
import StatusBadge from '../components/StatusBadge';
import { Search, Filter, ShieldCheck, AlertTriangle, ArrowRight, BarChart2, CheckCircle2, UserCheck, XCircle, Sparkles, RefreshCw } from 'lucide-react';

export default function DisputeList({ onSelectDispute }) {
  const [disputes, setDisputes] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [search, setSearch] = useState('');
  const [filterType, setFilterType] = useState('ALL');
  const [evalSummary, setEvalSummary] = useState(null);
  const [showEvalModal, setShowEvalModal] = useState(false);

  useEffect(() => {
    loadDisputes();
    loadEvalSummary();
  }, []);

  const loadDisputes = async () => {
    try {
      setLoading(true);
      const res = await fetchDisputes();
      setDisputes(res.data);
    } catch (err) {
      console.error(err);
      setError('Failed to connect to DisputeIQ backend API.');
    } finally {
      setLoading(false);
    }
  };

  const loadEvalSummary = async () => {
    try {
      const res = await fetchEvaluationSummary();
      if (res.data && res.data.status !== 'NOT_RUN') {
        setEvalSummary(res.data);
      }
    } catch (e) {
      console.log('Eval summary not loaded yet');
    }
  };

  const filtered = disputes.filter((d) => {
    const matchesSearch =
      d.dispute_id.toLowerCase().includes(search.toLowerCase()) ||
      d.payment_id.toLowerCase().includes(search.toLowerCase()) ||
      d.case_type.toLowerCase().includes(search.toLowerCase());

    const matchesFilter = filterType === 'ALL' || d.case_type === filterType;

    return matchesSearch && matchesFilter;
  });

  const caseTypes = ['ALL', 'STRONG_CASE', 'WEAK_CASE', 'CONTRADICTORY_CASE', 'MISSING_EVIDENCE_CASE', 'EDGE_CASE'];

  const stats = {
    total: disputes.length,
    strong: disputes.filter(d => d.case_type === 'STRONG_CASE').length,
    contradictory: disputes.filter(d => d.case_type === 'CONTRADICTORY_CASE').length,
    reviewNeeded: disputes.filter(d => d.status === 'HUMAN_REVIEW').length,
  };

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8">
      
      {/* Hero Banner */}
      <div className="relative glass-panel rounded-3xl p-8 shadow-2xl overflow-hidden border border-[#1b2a47]">
        <div className="absolute top-0 right-0 w-96 h-96 bg-gradient-to-bl from-blue-600/20 via-indigo-600/10 to-transparent rounded-full blur-3xl pointer-events-none" />

        <div className="flex flex-wrap items-center justify-between gap-6 relative z-10">
          <div className="space-y-2 max-w-3xl">
            <div className="inline-flex items-center space-x-2 px-3 py-1 rounded-full bg-blue-500/10 border border-blue-500/30 text-blue-400 font-mono text-xs">
              <Sparkles className="w-3.5 h-3.5" />
              <span>Razorpay Track 2 — AI Risk Manager</span>
            </div>
            <h1 className="text-3xl font-extrabold text-white tracking-tight sm:text-4xl">
              Dispute Investigation & Risk Intelligence
            </h1>
            <p className="text-sm text-slate-300 leading-relaxed font-sans">
              Automated evidence verification, lifecycle timeline reconstruction, and bounded AI decision policy for merchant chargebacks.
            </p>
          </div>

          {evalSummary && (
            <button
              onClick={() => setShowEvalModal(true)}
              className="flex items-center space-x-2.5 px-5 py-3 rounded-2xl bg-gradient-to-r from-blue-600 via-indigo-600 to-blue-700 text-white shadow-glow-blue hover:brightness-110 transition-all font-mono text-xs font-bold active:scale-95 shrink-0"
            >
              <BarChart2 className="w-4 h-4 text-blue-300" />
              <span>View Benchmark Evaluation ({evalSummary.metrics.recommendation_accuracy} Acc)</span>
            </button>
          )}
        </div>
      </div>

      {/* Metrics Summary Cards */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
        <div className="glass-panel p-5 rounded-2xl shadow-xl space-y-1">
          <div className="text-xs font-mono text-slate-400">Total Disputes</div>
          <div className="text-3xl font-extrabold text-white font-mono">{stats.total}</div>
          <div className="text-[11px] text-slate-500 font-mono">Synthetic Dataset (Seed 42)</div>
        </div>
        
        <div className="glass-panel p-5 rounded-2xl shadow-xl space-y-1 border-emerald-500/30 bg-emerald-950/10">
          <div className="text-xs font-mono text-emerald-400 flex items-center space-x-1.5 font-bold">
            <CheckCircle2 className="w-4 h-4" />
            <span>Strong Cases</span>
          </div>
          <div className="text-3xl font-extrabold text-emerald-300 font-mono">{stats.strong}</div>
          <div className="text-[11px] text-slate-400 font-mono">High Evidence Readiness</div>
        </div>

        <div className="glass-panel p-5 rounded-2xl shadow-xl space-y-1 border-rose-500/30 bg-rose-950/10">
          <div className="text-xs font-mono text-rose-400 flex items-center space-x-1.5 font-bold">
            <AlertTriangle className="w-4 h-4" />
            <span>Contradictions</span>
          </div>
          <div className="text-3xl font-extrabold text-rose-300 font-mono">{stats.contradictory}</div>
          <div className="text-[11px] text-slate-400 font-mono">Order ID / Amount Conflicts</div>
        </div>

        <div className="glass-panel p-5 rounded-2xl shadow-xl space-y-1 border-amber-500/30 bg-amber-950/10">
          <div className="text-xs font-mono text-amber-400 flex items-center space-x-1.5 font-bold">
            <UserCheck className="w-4 h-4" />
            <span>Human Review</span>
          </div>
          <div className="text-3xl font-extrabold text-amber-300 font-mono">{stats.reviewNeeded}</div>
          <div className="text-[11px] text-slate-400 font-mono">Auto Action Blocked</div>
        </div>
      </div>

      {/* Filter & Search Bar */}
      <div className="flex flex-wrap items-center justify-between gap-4 glass-panel p-4 rounded-2xl">
        <div className="relative flex-1 min-w-[260px]">
          <Search className="w-4 h-4 text-slate-400 absolute left-3.5 top-3" />
          <input
            type="text"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder="Search dispute ID, payment reference, or archetype..."
            className="w-full bg-[#070b14] border border-[#1b2a47] rounded-xl pl-10 pr-4 py-2.5 text-xs text-slate-200 focus:outline-none focus:border-blue-500 font-mono transition-all placeholder:text-slate-500"
          />
        </div>

        <div className="flex items-center space-x-1.5 overflow-x-auto py-1">
          {caseTypes.map((type) => (
            <button
              key={type}
              onClick={() => setFilterType(type)}
              className={`px-3.5 py-2 rounded-xl text-xs font-mono font-semibold transition-all ${
                filterType === type
                  ? 'bg-blue-600 text-white shadow-md shadow-blue-600/30 border border-blue-400/40'
                  : 'bg-[#070b14] text-slate-400 hover:bg-[#152238] hover:text-slate-200 border border-[#1b2a47]'
              }`}
            >
              {type.replace(/_/g, ' ')}
            </button>
          ))}
        </div>
      </div>

      {/* Disputes Table */}
      {loading ? (
        <div className="text-center py-20 glass-panel rounded-2xl">
          <div className="w-10 h-10 border-2 border-blue-500 border-t-transparent rounded-full animate-spin mx-auto mb-3"></div>
          <p className="text-xs font-mono text-slate-400">Loading dispute records...</p>
        </div>
      ) : error ? (
        <div className="p-6 bg-rose-950/30 border border-rose-500/40 rounded-2xl text-center text-rose-300 text-xs font-mono">
          {error}
        </div>
      ) : (
        <div className="glass-panel rounded-2xl shadow-2xl overflow-hidden">
          <div className="overflow-x-auto">
            <table className="w-full text-left border-collapse">
              <thead>
                <tr className="bg-[#070b14]/90 text-[11px] font-mono font-bold text-slate-400 uppercase tracking-wider border-b border-[#1b2a47]">
                  <th className="py-4 px-5">Dispute ID</th>
                  <th className="py-4 px-5">Payment Ref</th>
                  <th className="py-4 px-5">Claim Amount</th>
                  <th className="py-4 px-5">Dispute Category</th>
                  <th className="py-4 px-5">Archetype</th>
                  <th className="py-4 px-5">Status</th>
                  <th className="py-4 px-5 text-right">Action</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-[#1b2a47]/60 text-xs">
                {filtered.map((d) => (
                  <tr key={d.dispute_id} className="hover:bg-[#152238]/60 transition-colors group">
                    <td className="py-4 px-5 font-mono font-bold text-blue-400 group-hover:text-blue-300">
                      {d.dispute_id}
                    </td>
                    <td className="py-4 px-5 font-mono text-slate-300">
                      {d.payment_id}
                    </td>
                    <td className="py-4 px-5 font-mono font-semibold text-slate-100">
                      ₹{d.amount.toLocaleString('en-IN')}
                    </td>
                    <td className="py-4 px-5 text-slate-300 font-sans">
                      {d.reason}
                    </td>
                    <td className="py-4 px-5">
                      <span className={`px-2.5 py-1 rounded-lg text-[10px] font-mono font-bold border ${
                        d.case_type === 'STRONG_CASE' ? 'bg-emerald-500/10 text-emerald-300 border-emerald-500/30' :
                        d.case_type === 'CONTRADICTORY_CASE' ? 'bg-rose-500/10 text-rose-300 border-rose-500/30' :
                        'bg-amber-500/10 text-amber-300 border-amber-500/30'
                      }`}>
                        {d.case_type}
                      </span>
                    </td>
                    <td className="py-4 px-5">
                      <StatusBadge status={d.status} />
                    </td>
                    <td className="py-4 px-5 text-right">
                      <button
                        onClick={() => onSelectDispute(d.dispute_id)}
                        className="px-3.5 py-1.5 rounded-xl bg-blue-600/15 text-blue-300 border border-blue-500/30 hover:bg-blue-600 hover:text-white transition-all text-xs font-mono font-semibold inline-flex items-center space-x-1.5 shadow-sm"
                      >
                        <span>Investigate</span>
                        <ArrowRight className="w-3.5 h-3.5" />
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* Evaluation Modal */}
      {showEvalModal && evalSummary && (
        <div className="fixed inset-0 z-50 bg-black/80 backdrop-blur-md flex items-center justify-center p-4">
          <div className="glass-panel border border-[#1b2a47] rounded-3xl max-w-2xl w-full p-7 space-y-6 max-h-[90vh] overflow-y-auto shadow-2xl relative">
            <div className="flex items-center justify-between border-b border-[#1b2a47] pb-4">
              <h3 className="text-lg font-bold text-white font-mono flex items-center space-x-2.5">
                <BarChart2 className="w-5 h-5 text-blue-400" />
                <span>Held-Out Benchmark Evaluation Report</span>
              </h3>
              <button
                onClick={() => setShowEvalModal(false)}
                className="text-slate-400 hover:text-white font-mono text-sm px-2 py-1 rounded bg-[#070b14]"
              >
                ✕
              </button>
            </div>

            <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 text-center font-mono">
              <div className="bg-[#070b14] p-3.5 rounded-2xl border border-[#1b2a47]">
                <div className="text-[11px] text-slate-400 font-bold uppercase">Accuracy</div>
                <div className="text-2xl font-black text-emerald-400 mt-1">{evalSummary.metrics.recommendation_accuracy}</div>
              </div>
              <div className="bg-[#070b14] p-3.5 rounded-2xl border border-[#1b2a47]">
                <div className="text-[11px] text-slate-400 font-bold uppercase">False Contest</div>
                <div className="text-2xl font-black text-rose-400 mt-1">{evalSummary.metrics.false_contest_rate}</div>
              </div>
              <div className="bg-[#070b14] p-3.5 rounded-2xl border border-[#1b2a47]">
                <div className="text-[11px] text-slate-400 font-bold uppercase">False Acceptance</div>
                <div className="text-2xl font-black text-amber-400 mt-1">{evalSummary.metrics.false_acceptance_rate}</div>
              </div>
              <div className="bg-[#070b14] p-3.5 rounded-2xl border border-[#1b2a47]">
                <div className="text-[11px] text-slate-400 font-bold uppercase">Escalation</div>
                <div className="text-2xl font-black text-blue-400 mt-1">{evalSummary.metrics.human_escalation_rate}</div>
              </div>
            </div>

            <div className="bg-[#070b14] p-4 rounded-2xl border border-[#1b2a47] font-mono text-xs text-slate-300">
              <h4 className="font-bold text-slate-400 mb-2 uppercase text-[11px]">Confusion Matrix</h4>
              <pre className="text-blue-300">{JSON.stringify(evalSummary.confusion_matrix, null, 2)}</pre>
            </div>

            <div className="text-right">
              <button
                onClick={() => setShowEvalModal(false)}
                className="px-5 py-2.5 rounded-xl bg-[#152238] text-slate-200 text-xs font-mono font-bold hover:bg-slate-800"
              >
                Close Report
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
