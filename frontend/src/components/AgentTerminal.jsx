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

const DEMO_SCENARIOS = [
  {
    id: 'demo_1',
    badge: 'HITL Trigger',
    label: '🔥 High-Discount Enterprise Trap',
    description: 'Triggers Sales Director approval guardrail (>20% discount on $125k deal)',
    inquiry: 'We are FinTech Velocity Ltd. We are looking to implement an AI deal qualification desk across 65 enterprise reps. Our budget is $125,000, but our VP requires a 26% upfront volume discount before month-end.'
  },
  {
    id: 'demo_2',
    badge: 'Auto-Approved',
    label: '⚡ Urgent Fortune 500 Fast-Track',
    description: 'Auto-progresses to Proposal ($180k budget, 0% discount, high BANT)',
    inquiry: 'From Enterprise Architecture at Nexus Telecommunications: Immediate RFP for AI-driven deal routing. Budget is $180,000 pre-allocated from Digital Transformation fund. Requires ISO27001 and SOC2 compliance. No discount requested, full price.'
  },
  {
    id: 'demo_3',
    badge: 'Anti-Hallucination',
    label: '🛡️ Early-Stage Vague Inquiry',
    description: 'Tests anti-hallucination defense; routes to Discovery without false commitments',
    inquiry: 'Apex Health Systems is exploring modernizing its CRM pipeline. Currently using legacy spreadsheets and no timeline committed yet. Looking for pricing models.'
  },
  {
    id: 'demo_4',
    badge: 'Reflexion Critic',
    label: '🏦 Compliance & Custom SLA Check',
    description: 'Critic agent verifies SLA feasibility and self-corrects proposal language',
    inquiry: 'We are CyberShield Security Corp. We want to deploy autonomous deal routing for 150 sales engineers. Budget is $95,000 with a 15% discount. We require a 99.999% SLA and dedicated VPC deployment.'
  },
  {
    id: 'demo_5',
    badge: 'SMB Velocity',
    label: '🚀 High-Velocity SMB Pilot',
    description: 'Fast SMB tier qualification ($18k deal size, self-serve onboarding playbook)',
    inquiry: 'Hi, I run Nordic Scaleups Inc. We have 12 SDRs handling inbound leads and want an automated triage agent. Budget is $18,000 and we want to start a 14-day proof of concept.'
  }
];

export default function AgentTerminal({ onDealCreated }) {
  const [inquiryText, setInquiryText] = useState(DEMO_SCENARIOS[0].inquiry);
  const [activeScenarioId, setActiveScenarioId] = useState(DEMO_SCENARIOS[0].id);
  const [isRunning, setIsRunning] = useState(false);
  const [events, setEvents] = useState([]);
  const [completedDeal, setCompletedDeal] = useState(null);

  const handleSelectScenario = (scenario) => {
    setInquiryText(scenario.inquiry);
    setActiveScenarioId(scenario.id);
  };

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
    <div style={{ display: 'grid', gridTemplateColumns: '1.1fr 1.35fr', gap: '1.5rem', alignItems: 'start' }}>
      {/* Left Input Box */}
      <div className="glass-panel" style={{ padding: '1.5rem' }}>
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '0.75rem' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            <Sparkles size={18} style={{ color: 'var(--accent-primary)' }} />
            <h2 style={{ fontSize: '1.15rem' }}>Inbound Prospect Ingestion</h2>
          </div>
          <span style={{ fontSize: '0.72rem', background: 'rgba(99,102,241,0.15)', color: '#a5b4fc', padding: '0.2rem 0.5rem', borderRadius: 'var(--radius-full)' }}>
            5 Demo Scenarios
          </span>
        </div>

        <p style={{ fontSize: '0.85rem', color: 'var(--text-secondary)', marginBottom: '1rem' }}>
          Test the multi-agent graph with curated enterprise scenarios or type any custom sales email.
        </p>

        {/* Demo Scenario Cards */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem', marginBottom: '1.25rem' }}>
          <span style={{ fontSize: '0.72rem', color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.05em' }}>
            Select Demo Case:
          </span>
          {DEMO_SCENARIOS.map((scenario) => {
            const isSelected = activeScenarioId === scenario.id;
            return (
              <button
                key={scenario.id}
                onClick={() => handleSelectScenario(scenario)}
                style={{
                  background: isSelected ? 'rgba(99, 102, 241, 0.15)' : 'rgba(255, 255, 255, 0.03)',
                  border: '1px solid ' + (isSelected ? 'var(--accent-primary)' : 'var(--border-subtle)'),
                  color: isSelected ? '#fff' : 'var(--text-secondary)',
                  padding: '0.65rem 0.85rem',
                  borderRadius: 'var(--radius-sm)',
                  textAlign: 'left',
                  cursor: 'pointer',
                  transition: 'all 0.15s ease',
                  display: 'flex',
                  flexDirection: 'column',
                  gap: '0.2rem'
                }}
              >
                <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                  <span style={{ fontWeight: 600, fontSize: '0.82rem', color: isSelected ? '#fff' : '#e2e8f0' }}>
                    {scenario.label}
                  </span>
                  <span style={{
                    fontSize: '0.65rem',
                    padding: '0.1rem 0.4rem',
                    borderRadius: '4px',
                    background: scenario.badge === 'HITL Trigger' ? 'rgba(244,63,94,0.2)' : 'rgba(16,185,129,0.2)',
                    color: scenario.badge === 'HITL Trigger' ? '#fda4af' : '#6ee7b7',
                    fontWeight: 600
                  }}>
                    {scenario.badge}
                  </span>
                </div>
                <div style={{ fontSize: '0.72rem', color: 'var(--text-muted)' }}>
                  {scenario.description}
                </div>
              </button>
            );
          })}
        </div>

        {/* Custom Textarea */}
        <div style={{ marginBottom: '0.5rem', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <span style={{ fontSize: '0.72rem', color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.05em' }}>
            Inbound Payload (Editable):
          </span>
          <span style={{ fontSize: '0.7rem', color: 'var(--text-muted)' }}>
            Supports any custom prompt/company
          </span>
        </div>
        <textarea
          rows={5}
          value={inquiryText}
          onChange={e => {
            setInquiryText(e.target.value);
            setActiveScenarioId(null);
          }}
          placeholder="Type or paste any custom prospect inquiry..."
          style={{
            width: '100%',
            background: 'rgba(0, 0, 0, 0.4)',
            border: '1px solid var(--border-subtle)',
            borderRadius: 'var(--radius-md)',
            color: '#fff',
            padding: '0.85rem',
            fontSize: '0.82rem',
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
                <span>Executing Multi-Agent Workflow...</span>
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
            <div style={{ textAlign: 'center', color: 'var(--text-muted)', marginTop: '5rem', padding: '0 2rem' }}>
              <div style={{ fontSize: '1.2rem', marginBottom: '0.5rem' }}>⚡ Ready for Orchestration</div>
              Select one of the 5 demo cases on the left or enter any custom sales text, then click <strong>"Run Autonomous Deal Desk"</strong>.
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
