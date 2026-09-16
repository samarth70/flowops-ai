import React from 'react';
import { 
  Sparkles, 
  Kanban, 
  Terminal, 
  BarChart3, 
  Activity, 
  PlusCircle, 
  ShieldCheck,
  Zap
} from 'lucide-react';

export default function Navbar({ activeTab, setActiveTab, onNewInboundClick, hitlPendingCount = 0 }) {
  return (
    <nav className="navbar">
      <div className="nav-brand">
        <div className="brand-icon">
          <Sparkles size={22} />
        </div>
        <div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            <span className="brand-title">FlowOps AI</span>
            <span className="brand-badge">CRM Deal Desk</span>
          </div>
          <p style={{ fontSize: '0.72rem', color: 'var(--text-muted)' }}>
            Autonomous Multi-Agent Workflow &amp; Evaluation Suite
          </p>
        </div>
      </div>

      <div className="nav-tabs">
        <button
          className={`nav-tab-btn ${activeTab === 'kanban' ? 'active' : ''}`}
          onClick={() => setActiveTab('kanban')}
        >
          <Kanban size={16} />
          Pipeline CRM
          {hitlPendingCount > 0 && (
            <span style={{
              background: 'var(--accent-rose)',
              color: '#fff',
              fontSize: '0.65rem',
              fontWeight: 700,
              padding: '0.1rem 0.45rem',
              borderRadius: '9999px',
              marginLeft: '0.2rem'
            }}>
              {hitlPendingCount}
            </span>
          )}
        </button>

        <button
          className={`nav-tab-btn ${activeTab === 'terminal' ? 'active' : ''}`}
          onClick={() => setActiveTab('terminal')}
        >
          <Terminal size={16} />
          Live Agent Desk
        </button>

        <button
          className={`nav-tab-btn ${activeTab === 'eval' ? 'active' : ''}`}
          onClick={() => setActiveTab('eval')}
        >
          <BarChart3 size={16} />
          Evaluation Scorecard
        </button>

        <button
          className={`nav-tab-btn ${activeTab === 'observability' ? 'active' : ''}`}
          onClick={() => setActiveTab('observability')}
        >
          <Activity size={16} />
          Observability Waterfall
        </button>
      </div>

      <div className="nav-actions">
        <div style={{
          display: 'flex',
          alignItems: 'center',
          gap: '0.4rem',
          padding: '0.35rem 0.75rem',
          background: 'rgba(16, 185, 129, 0.1)',
          border: '1px solid rgba(16, 185, 129, 0.25)',
          borderRadius: 'var(--radius-full)',
          fontSize: '0.75rem',
          color: '#34d399',
          fontWeight: 600
        }}>
          <Zap size={13} />
          <span>100% Free Tier</span>
        </div>

        <button className="btn-primary" onClick={onNewInboundClick}>
          <PlusCircle size={16} />
          <span>Ingest Inbound Lead</span>
        </button>
      </div>
    </nav>
  );
}
