import React from 'react';
import { GitCommit, ShoppingBag, CreditCard, Receipt, Truck, CheckCircle2, MessageSquare, AlertOctagon } from 'lucide-react';
import StatusBadge from './StatusBadge';

export default function TimelineView({ timeline }) {
  const getEventIcon = (eventType) => {
    switch (eventType) {
      case 'ORDER_PLACED': return ShoppingBag;
      case 'PAYMENT_CAPTURED': return CreditCard;
      case 'INVOICE_GENERATED': return Receipt;
      case 'SHIPMENT_DISPATCHED': return Truck;
      case 'DELIVERY_COMPLETED': return CheckCircle2;
      case 'CUSTOMER_COMMUNICATION': return MessageSquare;
      case 'DISPUTE_FILED': return AlertOctagon;
      default: return GitCommit;
    }
  };

  return (
    <div className="bg-slate-900 border border-slate-800 rounded-xl p-5 shadow-xl">
      <div className="flex items-center justify-between mb-6">
        <div>
          <h3 className="text-base font-bold text-slate-100 flex items-center space-x-2">
            <GitCommit className="w-5 h-5 text-indigo-400" />
            <span>Transaction Lifecycle Timeline</span>
          </h3>
          <p className="text-xs text-slate-400 font-mono mt-0.5">
            Chronological reconstruction derived exclusively from verified system records
          </p>
        </div>
        <span className="text-xs font-mono px-2.5 py-1 rounded bg-slate-800 text-slate-300 border border-slate-700">
          Deterministic Timeline
        </span>
      </div>

      <div className="relative border-l-2 border-slate-800 ml-4 space-y-6">
        {timeline.map((evt, idx) => {
          const Icon = getEventIcon(evt.event_type);
          const isContradicted = evt.verification_state === 'CONTRADICTED';
          const isDispute = evt.event_type === 'DISPUTE_FILED';

          return (
            <div key={idx} className="relative pl-7 group">
              {/* Timeline node icon */}
              <div
                className={`absolute -left-3 top-0 w-6 h-6 rounded-full flex items-center justify-center border text-xs ${
                  isContradicted
                    ? 'bg-rose-900 text-rose-300 border-rose-500 ring-4 ring-rose-500/10'
                    : isDispute
                    ? 'bg-amber-900 text-amber-300 border-amber-500 ring-4 ring-amber-500/10'
                    : 'bg-slate-800 text-blue-400 border-slate-700 group-hover:border-blue-500'
                }`}
              >
                <Icon className="w-3.5 h-3.5" />
              </div>

              {/* Event card */}
              <div
                className={`p-3.5 rounded-lg border transition-all ${
                  isContradicted
                    ? 'bg-rose-950/20 border-rose-500/40'
                    : isDispute
                    ? 'bg-amber-950/20 border-amber-500/30'
                    : 'bg-slate-950/50 border-slate-800 hover:border-slate-700'
                }`}
              >
                <div className="flex flex-wrap items-center justify-between gap-2">
                  <div className="flex items-center space-x-2">
                    <span className="text-xs font-bold font-mono text-slate-200 uppercase tracking-wider">
                      {evt.event_type.replace(/_/g, ' ')}
                    </span>
                    <span className="text-[11px] font-mono px-2 py-0.5 rounded bg-slate-900 text-slate-400 border border-slate-800">
                      {evt.source}
                    </span>
                  </div>
                  <div className="flex items-center space-x-2">
                    <span className="text-xs font-mono text-slate-400">{evt.timestamp}</span>
                    <StatusBadge status={evt.verification_state} type="evidence" />
                  </div>
                </div>

                <p className="mt-2 text-xs text-slate-300 font-sans">{evt.description}</p>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
