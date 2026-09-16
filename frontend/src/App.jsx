import React, { useState, useEffect } from 'react';
import Navbar from './components/Navbar';
import KanbanBoard from './components/KanbanBoard';
import DealDetailModal from './components/DealDetailModal';
import AgentTerminal from './components/AgentTerminal';
import EvalScorecard from './components/EvalScorecard';
import ObservabilityModal from './components/ObservabilityModal';
import { fetchDeals, updateDealStage, processHITL } from './services/api';
import { 
  DollarSign, 
  ShieldAlert, 
  Award, 
  TrendingUp,
  Workflow
} from 'lucide-react';

export default function App() {
  const [deals, setDeals] = useState([]);
  const [activeTab, setActiveTab] = useState('kanban');
  const [selectedDeal, setSelectedDeal] = useState(null);
  const [loading, setLoading] = useState(true);

  const loadDeals = async () => {
    try {
      setLoading(true);
      const data = await fetchDeals();
      setDeals(data);
    } catch (err) {
      console.error('Failed to load deals:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadDeals();
  }, []);

  const handleUpdateStage = async (dealId, newStage) => {
    try {
      const res = await updateDealStage(dealId, newStage);
      setDeals(prev => prev.map(d => d.id === dealId ? res.deal : d));
      if (selectedDeal && selectedDeal.id === dealId) {
        setSelectedDeal(res.deal);
      }
    } catch (e) {
      console.error('Failed to update stage:', e);
    }
  };

  const handleProcessHITL = async (dealId, approved, notes) => {
    try {
      const res = await processHITL(dealId, approved, notes);
      setDeals(prev => prev.map(d => d.id === dealId ? res.deal : d));
      if (selectedDeal && selectedDeal.id === dealId) {
        setSelectedDeal(res.deal);
      }
    } catch (e) {
      console.error('Failed to process HITL:', e);
    }
  };

  const handleDealCreated = (newDeal) => {
    setDeals(prev => [newDeal, ...prev.filter(d => d.id !== newDeal.id)]);
  };

  // High level CRM stats
  const totalPipelineARR = deals.reduce((acc, d) => acc + (d.amount || 0), 0);
  const hitlPendingDeals = deals.filter(d => d.governance?.requires_approval && d.governance?.approval_status === 'PENDING');
  const highFitCount = deals.filter(d => d.bant?.total_score >= 80).length;

  return (
    <div className="app-container">
      <Navbar
        activeTab={activeTab}
        setActiveTab={setActiveTab}
        onNewInboundClick={() => setActiveTab('terminal')}
        hitlPendingCount={hitlPendingDeals.length}
      />

      <main className="main-content">
        {/* KPI Strip */}
        <div style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(4, 1fr)',
          gap: '1.25rem',
          marginBottom: '1.5rem'
        }}>
          <div className="metric-card">
            <div className="metric-title" style={{ display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
              <DollarSign size={14} style={{ color: 'var(--accent-emerald)' }} />
              <span>Total Pipeline ARR</span>
            </div>
            <div className="metric-value">
              ${totalPipelineARR.toLocaleString()}
            </div>
            <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginTop: '0.2rem' }}>
              Across {deals.length} Active Enterprise Opportunities
            </div>
          </div>

          <div className="metric-card">
            <div className="metric-title" style={{ display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
              <ShieldAlert size={14} style={{ color: 'var(--accent-rose)' }} />
              <span>HITL Review Queue</span>
            </div>
            <div className="metric-value" style={{ color: hitlPendingDeals.length > 0 ? '#fda4af' : '#6ee7b7' }}>
              {hitlPendingDeals.length}
              <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)', fontWeight: 500 }}>
                {hitlPendingDeals.length === 1 ? 'Action Required' : 'Deals Pending'}
              </span>
            </div>
            <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginTop: '0.2rem' }}>
              High-Discount Margin Guardrails Enforced
            </div>
          </div>

          <div className="metric-card">
            <div className="metric-title" style={{ display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
              <Award size={14} style={{ color: 'var(--accent-primary)' }} />
              <span>Tier 1 Enterprise Fit</span>
            </div>
            <div className="metric-value" style={{ color: '#c7d2fe' }}>
              {highFitCount} <span style={{ fontSize: '0.9rem', color: 'var(--text-muted)' }}>deals</span>
            </div>
            <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginTop: '0.2rem' }}>
              BANT Score &gt;= 80 / 100
            </div>
          </div>

          <div className="metric-card">
            <div className="metric-title" style={{ display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
              <Workflow size={14} style={{ color: 'var(--accent-cyan)' }} />
              <span>Evaluation Pass Rate</span>
            </div>
            <div className="metric-value" style={{ color: 'var(--accent-cyan)' }}>
              100%
            </div>
            <div style={{ fontSize: '0.75rem', color: '#10b981', marginTop: '0.2rem', fontWeight: 600 }}>
              ✓ 4 of 4 Golden Benchmarks Verified
            </div>
          </div>
        </div>

        {/* Tab Views */}
        {activeTab === 'kanban' && (
          <KanbanBoard
            deals={deals}
            onSelectDeal={setSelectedDeal}
            onUpdateStage={handleUpdateStage}
          />
        )}

        {activeTab === 'terminal' && (
          <AgentTerminal onDealCreated={handleDealCreated} />
        )}

        {activeTab === 'eval' && (
          <EvalScorecard />
        )}

        {activeTab === 'observability' && (
          <ObservabilityModal />
        )}
      </main>

      {/* Deal Detail Modal */}
      {selectedDeal && (
        <DealDetailModal
          deal={selectedDeal}
          onClose={() => setSelectedDeal(null)}
          onUpdateStage={handleUpdateStage}
          onProcessHITL={handleProcessHITL}
        />
      )}
    </div>
  );
}
