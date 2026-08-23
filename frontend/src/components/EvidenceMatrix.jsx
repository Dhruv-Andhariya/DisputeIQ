import React from 'react';
import { FileText, Package, Receipt, MessageSquare, ShieldCheck, AlertOctagon } from 'lucide-react';
import StatusBadge from './StatusBadge';

export default function EvidenceMatrix({ evidenceList }) {
  const getCategoryIcon = (category) => {
    switch (category) {
      case 'PROOF_OF_DELIVERY': return Package;
      case 'INVOICE': return Receipt;
      case 'ORDER_CONFIRMATION': return FileText;
      case 'CUSTOMER_COMMUNICATION': return MessageSquare;
      case 'TERMS_AND_CONDITIONS': return ShieldCheck;
      default: return FileText;
    }
  };

  return (
    <div className="bg-slate-900 border border-slate-800 rounded-xl p-5 shadow-xl">
      <div className="flex items-center justify-between mb-4">
        <div>
          <h3 className="text-base font-bold text-slate-100 flex items-center space-x-2">
            <FileText className="w-5 h-5 text-blue-400" />
            <span>Evidence Matrix & Document Verification</span>
          </h3>
          <p className="text-xs text-slate-400 font-mono mt-0.5">
            Retrieved records with deterministic status verification
          </p>
        </div>
        <span className="text-xs font-mono px-2.5 py-1 rounded bg-slate-800 text-slate-300 border border-slate-700">
          {evidenceList.length} Documents Attached
        </span>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-3.5">
        {evidenceList.map((item) => {
          const Icon = getCategoryIcon(item.category);
          const isContradiction = item.verification_status === 'CONTRADICTED';

          return (
            <div
              key={item.evidence_id}
              className={`p-4 rounded-lg border transition-all ${
                isContradiction
                  ? 'bg-rose-950/20 border-rose-500/40 shadow-lg shadow-rose-950/20'
                  : 'bg-slate-950/50 border-slate-800/80 hover:border-slate-700'
              }`}
            >
              <div className="flex items-start justify-between">
                <div className="flex items-center space-x-3">
                  <div className={`p-2 rounded-lg ${isContradiction ? 'bg-rose-500/20 text-rose-400' : 'bg-slate-800 text-blue-400'}`}>
                    <Icon className="w-5 h-5" />
                  </div>
                  <div>
                    <h4 className="text-sm font-semibold text-slate-200">{item.category.replace(/_/g, ' ')}</h4>
                    <p className="text-xs text-slate-400 font-mono mt-0.5">{item.file_name}</p>
                  </div>
                </div>
                <StatusBadge status={item.verification_status} type="evidence" />
              </div>

              {isContradiction && (
                <div className="mt-3 p-2.5 rounded bg-rose-500/10 border border-rose-500/30 flex items-start space-x-2">
                  <AlertOctagon className="w-4 h-4 text-rose-400 mt-0.5 shrink-0" />
                  <p className="text-xs text-rose-300 font-medium">
                    Evidence Contradiction: Data in this document conflicts with payment or carrier records.
                  </p>
                </div>
              )}

              {/* JSON preview */}
              <div className="mt-3 p-2.5 rounded bg-slate-900 border border-slate-800/60 font-mono text-[11px] text-slate-300 max-h-24 overflow-y-auto">
                <pre>{JSON.stringify(item.content, null, 2)}</pre>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
