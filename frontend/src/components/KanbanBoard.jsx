import React, { useState } from 'react';
import confetti from 'canvas-confetti';
import { 
  AlertTriangle, 
  CheckCircle2, 
  ChevronRight, 
  Clock, 
  DollarSign, 
  ShieldAlert, 
  UserCheck,
  Search,
  Filter,
  Sparkles,
  Layers
} from 'lucide-react';

const STAGES = [
  { key: 'New', label: 'New Lead', color: '#64748b' },
  { key: 'Discovery', label: 'Discovery / BANT', color: '#06b6d4' },
  { key: 'Proposal/Quote', label: 'Proposal / Quote', color: '#6366f1' },
  { key: 'Negotiation', label: 'Negotiation (HITL)', color: '#f59e0b' },
  { key: 'Closed Won', label: 'Closed Won', color: '#10b981' }
];

export default function KanbanBoard({ deals, onSelectDeal, onUpdateStage }) {
  const [searchQuery, setSearchQuery] = useState('');
  const [filterMode, setFilterMode] = useState('ALL'); // ALL, HITL, ENTERPRISE, HIGH_BANT

  const handleQuickAdvance = (e, deal) => {
    e.stopPropagation();
    const currentIndex = STAGES.findIndex(s => s.key === deal.stage);
    if (currentIndex < STAGES.length - 1) {
      const nextStage = STAGES[currentIndex + 1].key;
      onUpdateStage(deal.id, nextStage);

      if (nextStage === 'Closed Won') {
        confetti({
          particleCount: 80,
          spread: 70,
          origin: { y: 0.6 }
        });
      }
    }
  };

  // Filter deals based on search and pill selection
  const filteredDeals = deals.filter(deal => {
    const matchesSearch = 
      deal.title?.toLowerCase().includes(searchQuery.toLowerCase()) ||
      deal.account_name?.toLowerCase().includes(searchQuery.toLowerCase()) ||
      deal.contact_name?.toLowerCase().includes(searchQuery.toLowerCase());

    if (!matchesSearch) return false;

    if (filterMode === 'HITL') {
      return deal.governance?.requires_approval && deal.governance?.approval_status === 'PENDING';
    }
    if (filterMode === 'ENTERPRISE') {
      return (deal.amount || 0) >= 50000;
    }
    if (filterMode === 'HIGH_BANT') {
      return (deal.bant?.total_score || 0) >= 80;
    }
    return true;
  });

  const calculateStageARR = (stageKey) => {
    return filteredDeals
      .filter(d => d.stage === stageKey)
      .reduce((sum, d) => sum + (d.amount || 0), 0);
  };

  const getInitials = (name) => {
    if (!name) return '??';
    return name.split(' ').map(n => n[0]).join('').substring(0, 2).toUpperCase();
  };

  return (
    <div>
      {/* Attio/Refero Inspired Filter & Search Ribbon */}
      <div className="crm-filter-bar">
        <div className="search-input-box">
          <Search size={15} />
          <input
            type="text"
            placeholder="Search deals, accounts, or contacts..."
            value={searchQuery}
            onChange={e => setSearchQuery(e.target.value)}
          />
        </div>

        <div className="filter-pills-group">
          <button
            className={`filter-pill-btn ${filterMode === 'ALL' ? 'active' : ''}`}
            onClick={() => setFilterMode('ALL')}
          >
            All Deals ({deals.length})
          </button>
          <button
            className={`filter-pill-btn ${filterMode === 'HITL' ? 'active' : ''}`}
            onClick={() => setFilterMode('HITL')}
            style={{ color: filterMode === 'HITL' ? '#fda4af' : undefined }}
          >
            <ShieldAlert size={13} />
            Needs Review
          </button>
          <button
            className={`filter-pill-btn ${filterMode === 'ENTERPRISE' ? 'active' : ''}`}
            onClick={() => setFilterMode('ENTERPRISE')}
          >
            💎 Enterprise &gt; $50k
          </button>
          <button
            className={`filter-pill-btn ${filterMode === 'HIGH_BANT' ? 'active' : ''}`}
            onClick={() => setFilterMode('HIGH_BANT')}
          >
            🎯 High BANT (80+)
          </button>
        </div>
      </div>

      {/* Kanban Grid */}
      <div className="kanban-grid">
        {STAGES.map(stage => {
          const stageDeals = filteredDeals.filter(d => d.stage === stage.key);
          const stageTotalARR = calculateStageARR(stage.key);

          return (
            <div key={stage.key} className="kanban-column">
              <div className="column-header">
                <div>
                  <div className="column-title" style={{ color: stage.color }}>
                    <span>{stage.label}</span>
                  </div>
                  <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginTop: '0.2rem' }}>
                    ${stageTotalARR.toLocaleString()} ARR
                  </div>
                </div>
                <span className="column-count">{stageDeals.length}</span>
              </div>

              <div className="column-body">
                {stageDeals.length === 0 ? (
                  <div style={{ 
                    padding: '2.5rem 1rem', 
                    textAlign: 'center', 
                    color: 'var(--text-muted)',
                    fontSize: '0.8rem',
                    border: '1px dashed rgba(255,255,255,0.06)',
                    borderRadius: 'var(--radius-sm)'
                  }}>
                    No active deals in this stage
                  </div>
                ) : (
                  stageDeals.map(deal => {
                    const isFlagged = deal.governance?.requires_approval && deal.governance?.approval_status === 'PENDING';
                    const isHighFit = deal.bant?.total_score >= 80;

                    return (
                      <div
                        key={deal.id}
                        className={`deal-card ${isFlagged ? 'flagged' : (isHighFit ? 'high-fit' : '')}`}
                        onClick={() => onSelectDeal(deal)}
                      >
                        <div className="deal-top">
                          <div style={{ display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
                            <span className="deal-chip">#{String(deal.id).padStart(3, '0')}</span>
                            <span className="deal-account">{deal.account_name}</span>
                          </div>
                          {isFlagged ? (
                            <span className="badge badge-approval">
                              <ShieldAlert size={12} />
                              HITL
                            </span>
                          ) : (
                            <span className="badge badge-bant">
                              BANT: {deal.bant?.total_score || 0}
                            </span>
                          )}
                        </div>

                        <h3 className="deal-title">{deal.title}</h3>

                        <div className="contact-pill">
                          <span className="contact-avatar">{getInitials(deal.contact_name)}</span>
                          <span>{deal.contact_name}</span>
                        </div>

                        {/* Mini BANT Progress Track */}
                        <div className="mini-progress-track" title={`BANT Score: ${deal.bant?.total_score || 0}/100`}>
                          <div 
                            className="mini-progress-fill" 
                            style={{ 
                              width: `${deal.bant?.total_score || 0}%`,
                              background: isFlagged ? 'var(--accent-rose)' : undefined
                            }} 
                          />
                        </div>

                        {deal.governance?.discount_requested > 0 && (
                          <div style={{ 
                            fontSize: '0.72rem', 
                            color: deal.governance.discount_requested > 20 ? '#fda4af' : 'var(--text-muted)',
                            marginBottom: '0.4rem',
                            display: 'flex',
                            alignItems: 'center',
                            gap: '0.3rem'
                          }}>
                            <AlertTriangle size={11} />
                            Discount: <strong>{deal.governance.discount_requested}%</strong>
                          </div>
                        )}

                        <div className="deal-metrics">
                          <div className="deal-amount">
                            ${deal.amount?.toLocaleString()}
                          </div>

                          {stage.key !== 'Closed Won' && (
                            <button
                              title="Advance to next stage"
                              style={{
                                background: 'rgba(255, 255, 255, 0.06)',
                                border: '1px solid rgba(255, 255, 255, 0.1)',
                                color: 'var(--text-primary)',
                                borderRadius: 'var(--radius-sm)',
                                padding: '0.3rem 0.65rem',
                                fontSize: '0.72rem',
                                cursor: 'pointer',
                                display: 'flex',
                                alignItems: 'center',
                                gap: '0.2rem',
                                transition: 'all 0.15s ease'
                              }}
                              onClick={(e) => handleQuickAdvance(e, deal)}
                            >
                              <span>Next</span>
                              <ChevronRight size={12} />
                            </button>
                          )}
                        </div>
                      </div>
                    );
                  })
                )}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
