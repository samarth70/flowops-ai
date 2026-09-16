const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000';

export async function fetchDeals() {
  const res = await fetch(`${API_BASE}/api/crm/deals`);
  if (!res.ok) throw new Error('Failed to fetch deals');
  return res.json();
}

export async function fetchDeal(id) {
  const res = await fetch(`${API_BASE}/api/crm/deals/${id}`);
  if (!res.ok) throw new Error('Failed to fetch deal');
  return res.json();
}

export async function updateDealStage(id, stage) {
  const res = await fetch(`${API_BASE}/api/crm/deals/${id}/stage`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ stage, actor: 'Sales Representative' }),
  });
  if (!res.ok) throw new Error('Failed to update stage');
  return res.json();
}

export async function processHITL(id, approved, notes) {
  const res = await fetch(`${API_BASE}/api/crm/deals/${id}/hitl`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ approved, notes, approver: 'Sales Director' }),
  });
  if (!res.ok) throw new Error('Failed to process HITL decision');
  return res.json();
}

export async function fetchLatestEval() {
  const res = await fetch(`${API_BASE}/api/eval/runs/latest`);
  if (!res.ok) throw new Error('Failed to fetch evaluation metrics');
  return res.json();
}

export async function triggerEvalRun(modelName = 'Groq Llama-3.3-70B') {
  const res = await fetch(`${API_BASE}/api/eval/trigger?model_name=${encodeURIComponent(modelName)}`, {
    method: 'POST',
  });
  if (!res.ok) throw new Error('Failed to trigger evaluation run');
  return res.json();
}

export async function fetchTraces() {
  const res = await fetch(`${API_BASE}/api/agent/telemetry/traces`);
  if (!res.ok) throw new Error('Failed to fetch telemetry traces');
  return res.json();
}

export async function sendFeedback(traceId, value, comment = '') {
  const res = await fetch(`${API_BASE}/api/agent/telemetry/feedback`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ trace_id: traceId, score_name: 'user_approval', value, comment }),
  });
  return res.json();
}

export function streamAgentExecution(inquiry, onEvent, onError, onComplete) {
  fetch(`${API_BASE}/api/agent/stream`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ inquiry }),
  })
    .then(response => {
      const reader = response.body.getReader();
      const decoder = new TextDecoder();
      let buffer = '';

      function readChunk() {
        reader.read().then(({ done, value }) => {
          if (done) {
            if (onComplete) onComplete();
            return;
          }
          buffer += decoder.decode(value, { stream: true });
          const lines = buffer.split('\n\n');
          buffer = lines.pop() || '';

          for (const line of lines) {
            if (line.startsWith('data: ')) {
              try {
                const parsed = JSON.parse(line.slice(6));
                onEvent(parsed);
              } catch (e) {
                console.error('Error parsing SSE event:', e);
              }
            }
          }
          readChunk();
        }).catch(err => {
          if (onError) onError(err);
        });
      }

      readChunk();
    })
    .catch(err => {
      if (onError) onError(err);
    });
}
