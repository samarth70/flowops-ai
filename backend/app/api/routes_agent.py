import json
from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional, Dict, Any

from app.db import get_db
from app.agents.workflow import DealDeskWorkflow
from app.services.observability import observability

router = APIRouter(prefix="/api/agent", tags=["Agent & Observability"])

class InboundInquiryRequest(BaseModel):
    inquiry: str
    source: Optional[str] = "web_inbound"

class FeedbackRequest(BaseModel):
    trace_id: str
    score_name: str = "user_approval"
    value: float # 1.0 (thumbs up) or 0.0 (thumbs down)
    comment: Optional[str] = None

@router.post("/stream")
async def stream_agent_execution(payload: InboundInquiryRequest, db: Session = Depends(get_db)):
    """
    Streams multi-agent thinking, tool outputs, and Langfuse spans using Server-Sent Events (SSE).
    """
    async def event_generator():
        async for event in DealDeskWorkflow.run_streaming(payload.inquiry, db):
            yield f"data: {json.dumps(event)}\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")

@router.get("/telemetry/traces")
def get_traces(limit: int = 15):
    """
    Retrieves recent trace waterfall logs and telemetry.
    """
    return {
        "traces": observability.get_recent_traces(limit=limit),
        "langfuse_active": observability.langfuse is not None
    }

@router.post("/telemetry/feedback")
def submit_feedback(payload: FeedbackRequest):
    """
    Logs user thumbs up / thumbs down directly to the Langfuse trace session.
    """
    observability.log_feedback(
        trace_id=payload.trace_id,
        score_name=payload.score_name,
        value=payload.value,
        comment=payload.comment
    )
    return {"status": "success", "trace_id": payload.trace_id, "score": payload.value}
