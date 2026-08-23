import React, { useState, useEffect } from 'react';
import {
  fetchDisputeById,
  triggerInvestigation,
  fetchEvidence,
  fetchTimeline,
  fetchAuditEvents,
  approveDispute,
  rejectDispute
} from '../api';
import StatusBadge from '../components/StatusBadge';
import EvidenceMatrix from '../components/EvidenceMatrix';
import VerificationList from '../components/VerificationList';
import TimelineView from '../components/TimelineView';
import ReadinessGauge from '../components/ReadinessGauge';
import AIReasoningCard from '../components/AIReasoningCard';
import ActionControls from '../components/ActionControls';
import AuditLogView from '../components/AuditLogView';
import { ArrowLeft, RefreshCw, AlertOctagon, ShieldCheck, Terminal, FileText, GitCommit, UserCheck, Layers } from 'lucide-react';

export default function InvestigationDetail({ disputeId, onBack, failureModeTriggered }) {
  const [dispute, setDispute] = useState(null);
  const [investigation, setInvestigation] = useState(null);
  const [evidenceList, setEvidenceList] = useState([]);
  const [timeline, setTimeline] = useState([]);
  const [auditEvents, setAuditEvents] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    loadInvestigationData();
  }, [disputeId, failureModeTriggered]);

  const loadInvestigationData = async () => {
    try {
      setLoading(true);
      setError(null);
      
      const dispRes = await fetchDisputeById(disputeId);
      setDispute(dispRes.data);

      const invRes = await triggerInvestigation(disputeId);
      setInvestigation(invRes.data);

      const evRes = await fetchEvidence(disputeId);
      setEvidenceList(evRes.data);

      const timeRes = await fetchTimeline(disputeId);
      setTimeline(timeRes.data);

      const auditRes = await fetchAuditEvents(disputeId);
      setAuditEvents(auditRes.data);
    } catch (err) {
      console.error(err);
      setError('Failed to complete dispute investigation pipeline.');
    } finally {
      setLoading(false);
    }
  };

  const handleApprove = async (notes) => {
    try {
      await approveDispute(disputeId, notes);
      await loadInvestigationData();
    } catch (err) {
      alert('Failed to approve dispute submission.');
    }
  };

  const handleReject = async (notes) => {
    try {
      await rejectDispute(disputeId, notes);
      await loadInvestigationData();
    } catch (err) {
      alert('Failed to reject dispute.');
    }
  };

  if (loading) {
    return (
      <div className="max-w-7xl mx-auto px-4 py-24 text-center">
        <div className="w-12 h-12 border-3 border-blue-500 border-t-transparent rounded-full animate-spin mx-auto mb-4"></div>
        <h3 className="text-base font-bold text-white font-mono">Running DisputeIQ Investigation Pipeline...</h3>
        <p className="text-xs text-slate-400 font-mono mt-1">Executing deterministic checks, evidence matrix analysis & AI reasoning</p>
      </div>
    );
  }

  if (error || !dispute || !investigation) {
    return (
      <div className="max-w-7xl mx-auto px-4 py-12">
        <button onClick={onBack} className="text-xs font-mono text-slate-400 hover:text-white mb-4 flex items-center space-x-1.5">
          <ArrowLeft className="w-4 h-4" />
          <span>Back to Dispute Dashboard</span>
        </button>
        <div className="p-6 bg-rose-950/30 border border-rose-500/40 rounded-2xl text-center text-rose-300 font-mono text-xs shadow-2xl">
          {error || 'Dispute investigation data unavailable.'}
        </div>
      </div>
    );
  }

  const { verification_results, readiness_score, ai_analysis, decision } = investigation;

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-6">
      
      {/* Top Navigation Bar */}
      <div className="flex items-center justify-between">
        <button
          onClick={onBack}
          className="px-4 py-2 rounded-xl bg-[#0e1626] border border-[#1b2a47] text-slate-300 hover:text-white text-xs font-mono font-semibold inline-flex items-center space-x-2 transition-all shadow-md"
        >
          <ArrowLeft className="w-4 h-4" />
          <span>Back to Dashboard</span>
        </button>

        <div className="flex items-center space-x-3">
          <button
            onClick={loadInvestigationData}
            className="px-4 py-2 rounded-xl bg-[#0e1626] border border-[#1b2a47] text-slate-300 hover:text-white text-xs font-mono font-semibold inline-flex items-center space-x-2 transition-all shadow-md"
          >
            <RefreshCw className="w-3.5 h-3.5" />
            <span>Re-run Pipeline</span>
          </button>
        </div>
      </div>

      {/* Hero Header Card */}
      <div className="glass-panel rounded-3xl p-7 shadow-2xl space-y-5 relative overflow-hidden border border-[#1b2a47]">
        <div className="flex flex-wrap items-center justify-between gap-6 border-b border-[#1b2a47] pb-5">
          <div>
            <div className="flex items-center space-x-3">
              <h1 className="text-2xl font-black text-white font-mono tracking-tight sm:text-3xl">{dispute.dispute_id}</h1>
              <StatusBadge status={dispute.status} />
              <span className="text-xs font-mono font-bold px-3 py-1 rounded-xl bg-[#070b14] text-slate-300 border border-[#1b2a47]">
                {dispute.case_type}
              </span>
            </div>
            <p className="text-xs text-slate-400 font-mono mt-1.5">
              Dispute Reason: <strong className="text-slate-200">{dispute.reason}</strong>
            </p>
          </div>

          <div className="flex items-center space-x-8 font-mono">
            <div className="bg-[#070b14]/80 px-4 py-2 rounded-2xl border border-[#1b2a47] text-right">
              <div className="text-[10px] text-slate-400 font-bold uppercase">Claim Amount</div>
              <div className="text-2xl font-black text-emerald-400">₹{dispute.amount.toLocaleString('en-IN')}</div>
            </div>
            <div className="bg-[#070b14]/80 px-4 py-2 rounded-2xl border border-[#1b2a47] text-right">
              <div className="text-[10px] text-slate-400 font-bold uppercase">Payment ID</div>
              <div className="text-sm font-bold text-slate-200 mt-1">{dispute.payment_id}</div>
            </div>
          </div>
        </div>

        {/* Header Metadata Pills */}
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 text-xs font-mono">
          <div className="bg-[#070b14] p-3 rounded-xl border border-[#1b2a47]">
            <span className="text-slate-500">Merchant ID: </span>
            <span className="text-slate-300 font-semibold">{dispute.merchant_id}</span>
          </div>
          <div className="bg-[#070b14] p-3 rounded-xl border border-[#1b2a47]">
            <span className="text-slate-500">Dispute Filed: </span>
            <span className="text-slate-300 font-semibold">{dispute.dispute_date}</span>
          </div>
          <div className="bg-[#070b14] p-3 rounded-xl border border-[#1b2a47]">
            <span className="text-slate-500">Readiness Score: </span>
            <span className="text-blue-400 font-bold">{readiness_score.total_score}/100</span>
          </div>
          <div className="bg-[#070b14] p-3 rounded-xl border border-[#1b2a47]">
            <span className="text-slate-500">System Recommendation: </span>
            <span className="text-amber-400 font-bold">{decision.final_decision}</span>
          </div>
        </div>
      </div>

      {/* Main Investigation Split Layout */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        
        {/* Left Column (2 Cols): Decision Policy, AI Reasoning, Verification Checks, Evidence Matrix */}
        <div className="lg:col-span-2 space-y-6">
          
          {/* Decision Controls Panel */}
          <ActionControls
            decision={decision}
            disputeStatus={dispute.status}
            onApprove={handleApprove}
            onReject={handleReject}
          />

          {/* AI Investigation Reasoning Card */}
          <AIReasoningCard
            aiAnalysis={ai_analysis}
            decision={decision}
          />

          {/* Deterministic Verification Results */}
          <VerificationList verificationResults={verification_results} />

          {/* Evidence Documents Matrix */}
          <EvidenceMatrix evidenceList={evidenceList} />

        </div>

        {/* Right Column (1 Col): Readiness Gauge, Lifecycle Timeline, Audit Trail */}
        <div className="space-y-6">
          
          {/* Evidence Readiness Score Gauge */}
          <ReadinessGauge readinessScore={readiness_score} />

          {/* Transaction Lifecycle Timeline */}
          <TimelineView timeline={timeline} />

          {/* Immutable Audit Log Trail */}
          <AuditLogView auditEvents={auditEvents} />

        </div>

      </div>

    </div>
  );
}
