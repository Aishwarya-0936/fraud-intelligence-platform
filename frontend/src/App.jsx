import { useState } from 'react';
import { Activity, ShieldAlert, Zap } from 'lucide-react';
import Dashboard from './components/Dashboard';
import ReviewQueue from './components/ReviewQueue';
import SimulatePanel from './components/SimulatePanel';
import { Toaster } from 'react-hot-toast';
import './App.css';

function App() {
  const [activeView, setActiveView] = useState('dashboard');
  const [simulateOpen, setSimulateOpen] = useState(false);

  return (
    <div className="app-shell">
      <header className="topbar">
        <div className="topbar-brand">
          <div className="brand-mark">
            <Activity size={20} strokeWidth={2.5} />
          </div>
          <span className="brand-name">FRAUD INTELLIGENCE</span>
          <span className="live-indicator">
            <span className="live-dot" />
            LIVE
          </span>
        </div>

        <nav className="topbar-nav">
          <button
            className={`nav-btn ${activeView === 'dashboard' ? 'active' : ''}`}
            onClick={() => setActiveView('dashboard')}
          >
            <Activity size={16} />
            Dashboard
          </button>
          <button
            className={`nav-btn ${activeView === 'review' ? 'active' : ''}`}
            onClick={() => setActiveView('review')}
          >
            <ShieldAlert size={16} />
            Review Queue
          </button>
        </nav>

        <button className="simulate-btn" onClick={() => setSimulateOpen(true)}>
          <Zap size={16} />
          Simulate Transaction
        </button>
      </header>

      <Toaster
        position="bottom-left"
        toastOptions={{
          style: {
            background: '#1a2540',
            color: '#e2e8f0',
            border: '1px solid rgba(255,56,96,0.4)',
            fontFamily: 'var(--font-mono)',
            fontSize: '13px',
          },
        }}
      />

      <main className="main-content">
        {activeView === 'dashboard' && <Dashboard />}
        {activeView === 'review' && <ReviewQueue />}
      </main>

      <SimulatePanel isOpen={simulateOpen} onClose={() => setSimulateOpen(false)} />
    </div>
  );
}

export default App;