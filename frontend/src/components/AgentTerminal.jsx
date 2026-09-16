import React, { useState } from 'react';
import { 
  Play, 
  RotateCcw, 
  CheckCircle2, 
  AlertCircle, 
  Terminal, 
  Sparkles, 
  ExternalLink,
  ShieldAlert,
  ArrowRight
} from 'lucide-react';
import { streamAgentExecution } from '../services/api';

const PRESETS = [
  {
    label: '🔥 High-Discount Enterprise Trap (Triggers HITL)',
    inquiry: 'We are FinTech Velocity Ltd. We are looking to implement an AI deal qualification desk across 65 enterprise reps. Our budget is $125,000, but our VP requires a 26% upfront volume discount before month-end.'
  },
  {
    label: '✨ Standard Enterprise Migration (Auto-Approved)',
    inquiry: 'Acme Global Logistics needs to migrate 400 dispatch agents to an automated CRM workflow. Budget allocated: $90k. Looking for a standard 12% multi-year discount.'
  },
  {
    label: '🛡️ Early Stage Discovery (Low Budget/No Timeline)',
    inquiry: 'Apex Health Systems is exploring modernizing its CRM pipeline. Currently using legacy spreadsheets and no timeline committed yet. Looking for pricing models.'
  }
];

export default function AgentTerminal({ onDealCreated }) {
  const [inquiryText, setInquiryText] = useState(PRESETS[0].inquiry);
  const [isRunning, setIsRunning] = useState(false);
  const [events, setEvents] = useState([]);
  const [completedDeal, setCompletedDeal] = useState(null);

  const handleStartRun = () => {
    if (!inquiryText.trim() || isRunning) return;
    setIsRunning(true);
    setEvents([]);
    setCompletedDeal(null);

    streamAgentExecution(
      inquiryText,
      (event) => {
        setEvents(prev => [...prev, event]);
        if (event.type === 'workflow_completed') {
          setCompletedDeal(event.opportunity);
          if (onDealCreated) onDealCreated(event.opportunity);
        }
      },
      (error) => {
        console.error('SSE execution error:', error);
        setIsRunning(false);
      },
      () => {
        setIsRunning(false);
      }
    );
  };

  return (
    <div style={{ display: 'grid', gridTemplateColumns: '1fr 1.3fr', gap: '1.5rem', alignItems: 'start' }}>
      {/* Left Input Box */}
      <div className="glass-panel" style={{ padding: '1.5rem' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '1rem' }}>
          <Sparkles size={18} style={{ color: 'var(--accent-primary)' }} />
          <h2 style={{ fontSize: '1.15rem' }}>Inbound Prospect Ingestion</h2>
        </div>

        <p style={{ fontSize: '0.85rem', color: 'var(--text-secondary)', marginBottom: '1rem' }}>
          Feed raw sales emails, meeting transcripts, or RFP requests into the multi-agent state graph.
        </p>

        {/* Preset Selectors */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem', marginBottom: '1.25rem' }}>
          <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.05em' }}>
            Quick Benchmark Presets:
          </span>
          {PRESETS.map((p, idx) => (
            <button
              key={idx}
              onClick={() => setInquiryText(p.inquiry)}
              style={{
                background: inquiryText === p.inquiry ? 'rgba(99, 102, 241, 0.15)' : 'rgba(255, 255, 255, 0.03)',
                border: '1px solid ' + (inquiryText === p.inquiry ? 'var(--accent-primary)' : 'var(--border-subtle)'),
                color: inquiryText === p.inquiry ? '#fff' : 'var(--text-secondary)',
                padding: '0.5rem 0.75rem',
                borderRadius: 'var(--radius-sm)',
                fontSize: '0.78rem',
                textAlign: 'left',
                cursor: 'pointer',
                transition: 'all 0.15s ease'
              }}
            >
              {p.label}
            </button>
          ))}
        </div>

        {/* Custom Textarea */}
        <textarea
          rows={6}
          value={inquiryText}
          onChange={e => setInquiryText(e.target.value)}
          placeholder="Paste prospect inquiry or email here..."
          style={{
            width: '100%',
            background: 'rgba(0, 0, 0, 0.4)',
            border: '1px solid var(--border-subtle)',
            borderRadius: 'var(--radius-md)',
            color: '#fff',
            padding: '0.85rem',
            fontSize: '0.85rem',
            fontFamily: 'inherit',
            lineHeight: 1.5,
            resize: 'vertical',
            marginBottom: '1rem',
            outline: 'none'
          }}
        />

        <div style={{ display: 'flex', gap: '0.75rem' }}>
          <button
            className="btn-primary"
            style={{ flex: 1 }}
            onClick={handleStartRun}
            disabled={isRunning}
          >
            {isRunning ? (
              <>
                <div style={{
                  width: '14px',
                  height: '14px',
                  border: '2px solid #fff',
                  borderTopColor: 'transparent',
                  borderRadius: '50%',
                  animation: 'spin 1s linear infinite'
                }} />
                <span>Executing State Graph...</span>
              </>
            ) : (
              <>
                <Play size={16} />
                <span>Run Autonomous Deal Desk</span>
              </>
            )}
          </button>

          <button
            className="btn-secondary"
            onClick={() => setEvents([])}
            disabled={isRunning}
            title="Clear Console"
          >
            <RotateCcw size={16} />
          </button>
        </div>
      </div>

      {/* Right Terminal Console */}
      <div className="terminal-window">
        <div className="terminal-header">
          <div className="terminal-dots">
            <span className="dot dot-red"></span>
            <span className="dot dot-yellow"></span>
            <span className="dot dot-green"></span>
          </div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', color: 'var(--text-secondary)', fontSize: '0.75rem' }}>
            <Terminal size={14} />
            <span>Agent Orchestration Console (SSE Stream)</span>
          </div>
          <span style={{ fontSize: '0.7rem', color: isRunning ? 'var(--accent-cyan)' : 'var(--accent-emerald)', fontWeight: 600 }}>
            {isRunning ? '● LIVE STREAMING' : (events.length > 0 ? '✓ COMPLETE' : 'IDLE')}
          </span>
        </div>

        <div className="terminal-content">
          {events.length === 0 ? (
            <div style={{ textAlign: 'center', color: 'var(--text-muted)', marginTop: '5rem' }}>
              Select a preset on the left and click "Run Autonomous Deal Desk" to stream live multi-agent execution.
            </div>
          ) : (
            events.map((ev, index) => {
              if (ev.type === 'workflow_started') {
                return (
                  <div key={index} style={{ color: 'var(--accent-primary)', fontWeight: 600 }}>
                    ⚡ [SYSTEM] {ev.message} (Trace: {ev.trace_id})
                  </div>
                );
              }

              if (ev.type === 'agent_step') {
                return (
                  <div key={index} className="terminal-step">
                    <div className="step-agent">
                      <span>🤖 {ev.agent}</span>
                      {ev.status === 'completed' && (
                        <span style={{ fontSize: '0.7rem', color: 'var(--text-muted)' }}>
                          {ev.model} • {ev.latency_ms}ms
                        </span>
                      )}
                    </div>
                    {ev.status === 'processing' ? (
                      <div style={{ color: 'var(--text-secondary)', display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
                        <span style={{ animation: 'pulse 1.5s infinite' }}>{ev.message}</span>
                      </div>
                    ) : (
                      <pre style={{
                        marginTop: '0.4rem',
                        fontSize: '0.75rem',
                        color: '#cbd5e1',
                        background: 'rgba(0,0,0,0.3)',
                        padding: '0.5rem',
                        borderRadius: '4px',
                        overflowX: 'auto'
                      }}>
                        {JSON.stringify(ev.output, null, 2)}
                      </pre>
                    )}
                  </div>
                );
              }

              if (ev.type === 'hitl_flag') {
                return (
                  <div key={index} style={{
                    padding: '0.75rem',
                    background: 'rgba(244, 63, 94, 0.15)',
                    border: '1px solid var(--accent-rose)',
                    borderRadius: 'var(--radius-sm)',
                    color: '#fda4af',
                    display: 'flex',
                    alignItems: 'center',
                    gap: '0.5rem',
                    fontWeight: 600
                  }}>
                    <ShieldAlert size={16} />
                    <span>{ev.message}</span>
                  </div>
                );
              }

              if (ev.type === 'workflow_completed') {
                return (
                  <div key={index} style={{
                    padding: '1rem',
                    background: 'rgba(16, 185, 129, 0.12)',
                    border: '1px solid var(--accent-emerald)',
                    borderRadius: 'var(--radius-sm)',
                    color: '#6ee7b7'
                  }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', fontWeight: 600, marginBottom: '0.3rem' }}>
                      <CheckCircle2 size={16} />
                      <span>{ev.message}</span>
                    </div>
                    <div style={{ fontSize: '0.75rem', color: '#a7f3d0' }}>
                      Total Tokens: {ev.total_tokens} • Latency: {ev.total_latency_ms}ms • Trace: {ev.trace_id}
                    </div>
                  </div>
                );
              }

              return null;
            })
          )}
        </div>
      </div>
    </div>
  );
}
