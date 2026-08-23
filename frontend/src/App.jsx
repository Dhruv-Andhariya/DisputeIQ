import React, { useState } from 'react';
import Navbar from './components/Navbar';
import DisputeList from './pages/DisputeList';
import InvestigationDetail from './pages/InvestigationDetail';
import { triggerDemoFailure } from './api';

export default function App() {
  const [activePage, setActivePage] = useState('list');
  const [selectedDisputeId, setSelectedDisputeId] = useState(null);
  const [failureTriggeredCount, setFailureTriggeredCount] = useState(0);

  const handleSelectDispute = (disputeId) => {
    setSelectedDisputeId(disputeId);
    setActivePage('detail');
  };

  const handleTriggerFailure = async (disputeId) => {
    try {
      await triggerDemoFailure(disputeId);
      setFailureTriggeredCount((prev) => prev + 1);
      setActivePage('detail');
    } catch (err) {
      alert('Failed to simulate system failure scenario.');
    }
  };

  return (
    <div className="min-h-screen bg-[#0b132b] text-slate-100 font-sans flex flex-col">
      <Navbar
        activePage={activePage}
        setActivePage={setActivePage}
        onTriggerFailure={handleTriggerFailure}
        currentDisputeId={selectedDisputeId}
      />

      <main className="flex-1">
        {activePage === 'list' ? (
          <DisputeList onSelectDispute={handleSelectDispute} />
        ) : (
          <InvestigationDetail
            disputeId={selectedDisputeId}
            onBack={() => setActivePage('list')}
            failureModeTriggered={failureTriggeredCount}
          />
        )}
      </main>

      <footer className="border-t border-slate-800 bg-slate-950 py-4 text-center text-xs font-mono text-slate-400">
        DisputeIQ AI Risk Manager • Razorpay Internship 2027 Track 2 • Powered by FastAPI & Gemini
      </footer>
    </div>
  );
}
