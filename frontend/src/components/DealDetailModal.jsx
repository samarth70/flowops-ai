import React, { useState } from 'react';
import { 
  X, 
  Check, 
  AlertOctagon, 
  Copy, 
  Send, 
  ShieldCheck, 
  Activity, 
  Sparkles, 
  CheckCircle2, 
  Ban 
} from 'lucide-react';

export default function DealDetailModal({ deal, onClose, onUpdateStage, onProcessHITL }) {
  const [copied, setCopied] = useState(false);
  const [hitlNotes, setHitlNotes] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);

  if (!deal) return null;

  const handleCopyPitch = () => {
    if (deal.ai_insights?.pitch_draft) {
      navigator.clipboard.writeText(deal.ai_insights.pitch_draft);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    }
  };

  const handleDecision = async (approved) => {
    setIsSubmitting(true);
    try {
      await onProcessHITL(deal.id, approved, hitlNotes || (approved ? 'Approved by Sales Director.' : 'Discount rejected by Sales Director.'));
      onClose();
    } finally {
      setIsSubmitting(false);
    }
  };

  const isPendingApproval = deal.governance?.requires_approval && deal.governance?.approval_status === 'PENDING';

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-card" onClick={e => e.stopPropagation()}>
        <div className="modal-header">
          <div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.6rem' }}>
              <span style={{ fontSize: '0.8rem', color: 'var(--accent-cyan)', fontWeight: 600 }}>
                {deal.account_name}
              </span>
              <span style={{ color: 'var(--text-muted)' }}>•</span>
              <span style={{ fontSize: '0.8rem', color: 'var(--text-secondary)' }}>
                Deal #{deal.id}
              </span>
            </div>
            <h2 style={{ fontSize: '1.35rem', marginTop: '0.2rem' }}>{deal.title}</h2>
          </div>

          <button 
            onClick={onClose}
            style={{
              background: 'rgba(255, 255, 255, 0.06)',
              border: 'none',
              color: 'var(--text-secondary)',
              cursor: 'pointer',
              padding: '0.4rem',
              borderRadius: 'var(--radius-sm)'
            }}
          >
            <X size={20} />
          </button>
        </div>

        <div className="modal-body">
          {/* HITL Review Alert if Pending */}
          {isPendingApproval && (
            <div style={{
              background: 'rgba(244, 63, 94, 0.12)',
              border: '1px solid rgba(244, 63, 94, 0.35)',
              borderRadius: 'var(--radius-md)',
              padding: '1.25rem',
              marginBottom: '1.5rem',
              display: 'flex',
              flexDirection: 'column',
              gap: '0.85rem'
            }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', color: '#fda4af', fontWeight: 600 }}>
                <AlertOctagon size={18} />
                <span>Human-in-the-Loop Governance: Approval Required</span>
              </div>
              <p style={{ fontSize: '0.85rem', color: '#fecdd3' }}>
                This deal requests a <strong>{deal.governance?.discount_requested}% discount</strong> on a ${deal.amount?.toLocaleString()} contract value, which breaches autonomous automated limits.
              </p>

              <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
                <input
                  type="text"
                  placeholder="Sales Director review comments or conditions..."
                  value={hitlNotes}
                  onChange={e => setHitlNotes(e.target.value)}
                  style={{
                    background: 'rgba(0, 0, 0, 0.4)',
                    border: '1px solid rgba(244, 63, 94, 0.3)',
                    color: '#fff',
                    padding: '0.6rem 0.85rem',
                    borderRadius: 'var(--radius-sm)',
                    fontSize: '0.85rem',
                    outline: 'none'
                  }}
                />
                <div style={{ display: 'flex', gap: '0.75rem', marginTop: '0.25rem' }}>
                  <button
                    className="btn-primary"
                    style={{ background: 'linear-gradient(135deg, #10b981, #059669)' }}
                    onClick={() => handleDecision(true)}
                    disabled={isSubmitting}
                  >
                    <Check size={15} />
                    Approve Discount ({deal.governance?.discount_requested}%)
                  </button>
                  <button
                    className="btn-secondary"
                    style={{ color: '#fda4af', borderColor: 'rgba(244, 63, 94, 0.4)' }}
                    onClick={() => handleDecision(false)}
                    disabled={isSubmitting}
                  >
                    <Ban size={15} />
                    Reject Discount (Retain Base Pricing)
                  </button>
                </div>
              </div>
            </div>
          )}

          {/* Key Deal Metrics Row */}
          <div style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(4, 1fr)',
            gap: '1rem',
            marginBottom: '1.5rem'
          }}>
            <div className="metric-card">
              <div className="metric-title">Deal Amount</div>
              <div style={{ fontSize: '1.4rem', fontWeight: 700, color: '#fff' }}>
                ${deal.amount?.toLocaleString()}
              </div>
              <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginTop: '0.2rem' }}>
                Stage: {deal.stage}
              </div>
            </div>

            <div className="metric-card">
              <div className="metric-title">BANT Qualification</div>
              <div style={{ fontSize: '1.4rem', fontWeight: 700, color: '#818cf8' }}>
                {deal.bant?.total_score || 0}<span style={{ fontSize: '0.9rem', color: 'var(--text-muted)' }}>/100</span>
              </div>
              <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginTop: '0.2rem' }}>
                B:{deal.bant?.budget} A:{deal.bant?.authority} N:{deal.bant?.need} T:{deal.bant?.timeline}
              </div>
            </div>

            <div className="metric-card">
              <div className="metric-title">Risk &amp; Governance</div>
              <div style={{ 
                fontSize: '1.2rem', 
                fontWeight: 700, 
                color: deal.governance?.risk_level === 'HIGH' ? '#f43f5e' : '#10b981' 
              }}>
                {deal.governance?.risk_level || 'LOW'}
              </div>
              <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginTop: '0.2rem' }}>
                Status: {deal.governance?.approval_status}
              </div>
            </div>

            <div className="metric-card">
              <div className="metric-title">Inference Telemetry</div>
              <div style={{ fontSize: '1.2rem', fontWeight: 700, color: 'var(--accent-cyan)' }}>
                {deal.telemetry?.latency_ms || 850} ms
              </div>
              <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginTop: '0.2rem' }}>
                {deal.telemetry?.total_tokens || 1200} tokens
              </div>
            </div>
          </div>

          {/* AI Strategy & Analysis */}
          <div style={{ display: 'flex', flexDirection: 'column', gap: '1.25rem', marginBottom: '1.5rem' }}>
            <div style={{
              background: 'rgba(255, 255, 255, 0.02)',
              border: '1px solid var(--border-subtle)',
              borderRadius: 'var(--radius-md)',
              padding: '1.25rem'
            }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.4rem', color: 'var(--accent-primary)', fontWeight: 600, marginBottom: '0.5rem', fontSize: '0.9rem' }}>
                <Sparkles size={16} />
                <span>AI Deal Strategist Assessment</span>
              </div>
              <p style={{ fontSize: '0.9rem', color: 'var(--text-primary)', lineHeight: 1.6 }}>
                {deal.ai_insights?.summary || 'No AI summary recorded.'}
              </p>
              {deal.ai_insights?.recommended_strategy && (
                <div style={{ marginTop: '0.75rem', padding: '0.75rem', background: 'rgba(99, 102, 241, 0.08)', borderRadius: 'var(--radius-sm)', borderLeft: '3px solid var(--accent-primary)', fontSize: '0.85rem' }}>
                  <strong>Recommended Playbook:</strong> {deal.ai_insights.recommended_strategy}
                </div>
              )}
            </div>

            {/* AI Pitch Draft */}
            {deal.ai_insights?.pitch_draft && (
              <div style={{
                background: 'rgba(255, 255, 255, 0.02)',
                border: '1px solid var(--border-subtle)',
                borderRadius: 'var(--radius-md)',
                padding: '1.25rem'
              }}>
                <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '0.5rem' }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '0.4rem', color: 'var(--accent-cyan)', fontWeight: 600, fontSize: '0.9rem' }}>
                    <Send size={15} />
                    <span>Generated Executive Outreach Draft</span>
                  </div>
                  <button
                    onClick={handleCopyPitch}
                    style={{
                      background: 'rgba(255, 255, 255, 0.06)',
                      border: '1px solid var(--border-subtle)',
                      color: copied ? '#10b981' : 'var(--text-secondary)',
                      padding: '0.3rem 0.6rem',
                      borderRadius: 'var(--radius-sm)',
                      fontSize: '0.75rem',
                      cursor: 'pointer',
                      display: 'flex',
                      alignItems: 'center',
                      gap: '0.3rem'
                    }}
                  >
                    {copied ? <Check size={12} /> : <Copy size={12} />}
                    {copied ? 'Copied!' : 'Copy Draft'}
                  </button>
                </div>
                <pre style={{
                  background: 'rgba(0, 0, 0, 0.35)',
                  padding: '1rem',
                  borderRadius: 'var(--radius-sm)',
                  fontSize: '0.85rem',
                  color: '#e2e8f0',
                  whiteSpace: 'pre-wrap',
                  fontFamily: 'inherit',
                  lineHeight: 1.6
                }}>
                  {deal.ai_insights.pitch_draft}
                </pre>
              </div>
            )}
          </div>

          {/* Change Stage Controls */}
          <div style={{
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
            paddingTop: '1.25rem',
            borderTop: '1px solid var(--border-subtle)'
          }}>
            <div style={{ fontSize: '0.85rem', color: 'var(--text-secondary)' }}>
              Move Stage:
            </div>
            <div style={{ display: 'flex', gap: '0.5rem' }}>
              {['New', 'Discovery', 'Proposal/Quote', 'Negotiation', 'Closed Won'].map(stg => (
                <button
                  key={stg}
                  onClick={() => {
                    onUpdateStage(deal.id, stg);
                    onClose();
                  }}
                  style={{
                    background: deal.stage === stg ? 'var(--accent-primary)' : 'rgba(255, 255, 255, 0.05)',
                    color: deal.stage === stg ? '#fff' : 'var(--text-secondary)',
                    border: '1px solid ' + (deal.stage === stg ? 'var(--accent-primary)' : 'var(--border-subtle)'),
                    padding: '0.4rem 0.75rem',
                    borderRadius: 'var(--radius-sm)',
                    fontSize: '0.75rem',
                    cursor: 'pointer'
                  }}
                >
                  {stg}
                </button>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
