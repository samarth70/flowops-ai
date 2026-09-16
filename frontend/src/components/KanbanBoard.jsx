import React from 'react';
import confetti from 'canvas-confetti';
import { 
  AlertTriangle, 
  CheckCircle2, 
  ChevronRight, 
  Clock, 
  DollarSign, 
  ShieldAlert, 
  UserCheck 
} from 'lucide-react';

const STAGES = [
  { key: 'New', label: 'New Lead', color: '#64748b' },
  { key: 'Discovery', label: 'Discovery / BANT', color: '#06b6d4' },
  { key: 'Proposal/Quote', label: 'Proposal / Quote', color: '#6366f1' },
  { key: 'Negotiation', label: 'Negotiation (HITL)', color: '#f59e0b' },
  { key: 'Closed Won', label: 'Closed Won', color: '#10b981' }
];

export default function KanbanBoard({ deals, onSelectDeal, onUpdateStage }) {
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

  const calculateStageARR = (stageKey) => {
    return deals
      .filter(d => d.stage === stageKey)
      .reduce((sum, d) => sum + (d.amount || 0), 0);
  };

  return (
    <div>
      <div className="kanban-grid">
        {STAGES.map(stage => {
          const stageDeals = deals.filter(d => d.stage === stage.key);
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
                    padding: '2rem 1rem', 
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
                          <span className="deal-account">{deal.account_name}</span>
                          {isFlagged ? (
                            <span className="badge badge-approval">
                              <ShieldAlert size={12} />
                              HITL Review
                            </span>
                          ) : (
                            <span className="badge badge-bant">
                              BANT: {deal.bant?.total_score || 0}
                            </span>
                          )}
                        </div>

                        <h3 className="deal-title">{deal.title}</h3>

                        <div style={{ fontSize: '0.78rem', color: 'var(--text-secondary)', marginBottom: '0.6rem' }}>
                          👤 {deal.contact_name}
                        </div>

                        {deal.governance?.discount_requested > 0 && (
                          <div style={{ 
                            fontSize: '0.72rem', 
                            color: deal.governance.discount_requested > 20 ? '#fda4af' : 'var(--text-muted)',
                            marginBottom: '0.5rem',
                            display: 'flex',
                            alignItems: 'center',
                            gap: '0.3rem'
                          }}>
                            <AlertTriangle size={11} />
                            Discount Requested: <strong>{deal.governance.discount_requested}%</strong>
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
                                padding: '0.3rem 0.6rem',
                                fontSize: '0.72rem',
                                cursor: 'pointer',
                                display: 'flex',
                                alignItems: 'center',
                                gap: '0.2rem'
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
