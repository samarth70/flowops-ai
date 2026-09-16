import React, { useState, useEffect } from 'react';
import { 
  Activity, 
  ExternalLink, 
  ThumbsUp, 
  ThumbsDown, 
  Clock, 
  Layers, 
  Sparkles, 
  DollarSign 
} from 'lucide-react';
import { fetchTraces, sendFeedback } from '../services/api';

export default function ObservabilityModal() {
  const [telemetry, setTelemetry] = useState({ traces: [], langfuse_active: false });
  const [loading, setLoading] = useState(true);
  const [votedTraces, setVotedTraces] = useState({});

  const loadTraces = async () => {
    try {
      setLoading(true);
      const data = await fetchTraces();
      setTelemetry(data);
    } catch (e) {
      console.error('Failed to fetch traces:', e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadTraces();
  }, []);

  const handleVote = async (traceId, val) => {
    try {
      await sendFeedback(traceId, val);
      setVotedTraces(prev => ({ ...prev, [traceId]: val }));
    } catch (e) {
      console.error('Feedback failed:', e);
    }
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
      {/* Top Banner */}
      <div className="hero-banner">
        <div className="hero-text">
          <h1>Langfuse Cloud &amp; Distributed Tracing Telemetry</h1>
          <p>
            Real-time observability across all agent node invocations. Tracks prompt token volume, completion latency waterfall, and human feedback scoring.
          </p>
        </div>

        <div className="hero-controls">
          <div style={{
            background: 'rgba(99, 102, 241, 0.15)',
            border: '1px solid var(--accent-primary)',
            padding: '0.5rem 1rem',
            borderRadius: 'var(--radius-md)',
            color: '#c7d2fe',
            fontSize: '0.8rem',
            display: 'flex',
            alignItems: 'center',
            gap: '0.4rem'
          }}>
            <Sparkles size={14} />
            <span>Telemetry Pipeline • OpenTelemetry V2</span>
          </div>
        </div>
      </div>

      {/* Traces List */}
      <div className="glass-panel" style={{ padding: '1.5rem' }}>
        <h3 style={{ fontSize: '1.1rem', marginBottom: '1rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
          <Activity size={18} style={{ color: 'var(--accent-primary)' }} />
          <span>Recent Execution Traces ({telemetry.traces.length})</span>
        </h3>

        {telemetry.traces.length === 0 ? (
          <div style={{ textAlign: 'center', color: 'var(--text-muted)', padding: '3rem 0' }}>
            No traces recorded yet. Run a deal through the Live Agent Desk to generate traces.
          </div>
        ) : (
          <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
            {telemetry.traces.map((trace, idx) => (
              <div
                key={trace.id || idx}
                style={{
                  background: 'rgba(255, 255, 255, 0.02)',
                  border: '1px solid var(--border-subtle)',
                  borderRadius: 'var(--radius-md)',
                  padding: '1.25rem'
                }}
              >
                <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '0.75rem' }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '0.6rem' }}>
                    <span style={{ fontFamily: 'JetBrains Mono', fontSize: '0.8rem', color: 'var(--accent-cyan)' }}>
                      {trace.id}
                    </span>
                    <span style={{
                      fontSize: '0.7rem',
                      background: trace.status === 'SUCCESS' ? 'rgba(16, 185, 129, 0.15)' : 'rgba(99, 102, 241, 0.15)',
                      color: trace.status === 'SUCCESS' ? '#6ee7b7' : '#c7d2fe',
                      padding: '0.15rem 0.45rem',
                      borderRadius: 'var(--radius-sm)',
                      fontWeight: 600
                    }}>
                      {trace.name}
                    </span>
                  </div>

                  <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
                    <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>
                      ⏱️ {trace.latency_ms}ms
                    </span>
                    <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>
                      🪙 {trace.total_tokens} tokens
                    </span>
                    <span style={{ fontSize: '0.8rem', color: '#34d399', fontWeight: 600 }}>
                      ⚡ Trace Verified
                    </span>

                    {/* Thumbs Up / Down Score */}
                    <div style={{ display: 'flex', gap: '0.3rem', alignItems: 'center', marginLeft: '0.5rem' }}>
                      <button
                        title="Score as Good (Syncs to Langfuse)"
                        onClick={() => handleVote(trace.id, 1.0)}
                        style={{
                          background: votedTraces[trace.id] === 1.0 ? 'rgba(16, 185, 129, 0.25)' : 'rgba(255, 255, 255, 0.05)',
                          border: 'none',
                          color: votedTraces[trace.id] === 1.0 ? '#34d399' : 'var(--text-muted)',
                          padding: '0.3rem',
                          borderRadius: '4px',
                          cursor: 'pointer'
                        }}
                      >
                        <ThumbsUp size={13} />
                      </button>
                      <button
                        title="Score as Poor (Syncs to Langfuse)"
                        onClick={() => handleVote(trace.id, 0.0)}
                        style={{
                          background: votedTraces[trace.id] === 0.0 ? 'rgba(244, 63, 94, 0.25)' : 'rgba(255, 255, 255, 0.05)',
                          border: 'none',
                          color: votedTraces[trace.id] === 0.0 ? '#f43f5e' : 'var(--text-muted)',
                          padding: '0.3rem',
                          borderRadius: '4px',
                          cursor: 'pointer'
                        }}
                      >
                        <ThumbsDown size={13} />
                      </button>
                    </div>

                    {trace.external_url && (
                      <a
                        href={trace.external_url}
                        target="_blank"
                        rel="noreferrer"
                        style={{
                          color: 'var(--accent-primary)',
                          display: 'flex',
                          alignItems: 'center',
                          gap: '0.2rem',
                          fontSize: '0.75rem',
                          textDecoration: 'none'
                        }}
                      >
                        <span>Langfuse</span>
                        <ExternalLink size={12} />
                      </a>
                    )}
                  </div>
                </div>

                {/* Spans Waterfall */}
                {trace.spans && trace.spans.length > 0 && (
                  <div style={{ display: 'flex', flexDirection: 'column', gap: '0.4rem', marginTop: '0.65rem' }}>
                    {trace.spans.map((span, sIdx) => (
                      <div
                        key={span.id || sIdx}
                        style={{
                          display: 'flex',
                          alignItems: 'center',
                          justifyContent: 'space-between',
                          padding: '0.4rem 0.65rem',
                          background: 'rgba(0, 0, 0, 0.3)',
                          borderRadius: 'var(--radius-sm)',
                          fontSize: '0.75rem'
                        }}
                      >
                        <span style={{ color: 'var(--accent-cyan)', fontWeight: 500 }}>
                          ↳ {span.name}
                        </span>
                        <span style={{ color: 'var(--text-secondary)' }}>
                          {span.model}
                        </span>
                        <span style={{ color: 'var(--text-muted)' }}>
                          {span.tokens} tokens
                        </span>
                        <span style={{ color: '#e2e8f0' }}>
                          {span.latency_ms}ms
                        </span>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
