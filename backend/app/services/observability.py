import time
import uuid
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
from app.config import settings

logger = logging.getLogger("FlowOps.Observability")

class ObservabilityManager:
    """
    Observability & Telemetry Manager:
    - Syncs spans & traces to Langfuse Cloud (Free tier) if keys are provided.
    - Maintains an in-memory high-speed telemetry buffer for instant UI trace exploration.
    - Computes cost ($0 free tier tracked), tokens, and latency breakdown.
    """

    def __init__(self):
        self.langfuse = None
        self.local_traces: List[Dict[str, Any]] = []

        if settings.has_langfuse:
            try:
                from langfuse import Langfuse
                self.langfuse = Langfuse(
                    public_key=settings.LANGFUSE_PUBLIC_KEY,
                    secret_key=settings.LANGFUSE_SECRET_KEY,
                    host=settings.LANGFUSE_HOST
                )
                logger.info("Langfuse Cloud tracing active.")
            except Exception as e:
                logger.warning(f"Failed to initialize Langfuse Cloud: {e}")

    def start_trace(self, name: str, user_id: str = "sales-rep-1", metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        trace_id = f"trace_{uuid.uuid4().hex[:12]}"
        trace_obj = {
            "id": trace_id,
            "name": name,
            "user_id": user_id,
            "metadata": metadata or {},
            "start_time": time.time(),
            "timestamp": datetime.utcnow().isoformat(),
            "spans": [],
            "scores": {},
            "status": "RUNNING",
            "total_tokens": 0,
            "latency_ms": 0,
            "external_url": f"https://cloud.langfuse.com/project/trace/{trace_id}" if settings.has_langfuse else None
        }

        # Remote Langfuse
        if self.langfuse:
            try:
                self.langfuse.trace(
                    id=trace_id,
                    name=name,
                    user_id=user_id,
                    metadata=metadata
                )
            except Exception as e:
                logger.debug(f"Langfuse trace creation error: {e}")

        return trace_obj

    def add_span(self, trace_obj: Dict[str, Any], step_name: str, input_data: Any, output_data: Any,
                 model: str = "llama-3.3-70b", latency_ms: int = 250, tokens: int = 150):
        span_id = f"span_{uuid.uuid4().hex[:8]}"
        span_entry = {
            "id": span_id,
            "name": step_name,
            "model": model,
            "input": input_data,
            "output": output_data,
            "latency_ms": latency_ms,
            "tokens": tokens,
            "timestamp": datetime.utcnow().isoformat()
        }
        trace_obj["spans"].append(span_entry)
        trace_obj["total_tokens"] += tokens

        # Sync with Langfuse
        if self.langfuse:
            try:
                self.langfuse.generation(
                    trace_id=trace_obj["id"],
                    name=step_name,
                    model=model,
                    input=input_data,
                    output=output_data,
                    usage={"total_tokens": tokens}
                )
            except Exception as e:
                logger.debug(f"Langfuse generation log error: {e}")

    def end_trace(self, trace_obj: Dict[str, Any], status: str = "SUCCESS"):
        trace_obj["end_time"] = time.time()
        trace_obj["latency_ms"] = int((trace_obj["end_time"] - trace_obj["start_time"]) * 1000)
        trace_obj["status"] = status

        # Keep last 50 traces in memory
        self.local_traces.insert(0, trace_obj)
        if len(self.local_traces) > 50:
            self.local_traces.pop()

        if self.langfuse:
            try:
                self.langfuse.flush()
            except Exception as e:
                logger.debug(f"Langfuse flush error: {e}")

    def log_feedback(self, trace_id: str, score_name: str, value: float, comment: Optional[str] = None):
        """User thumbs up / thumbs down feedback score"""
        for t in self.local_traces:
            if t["id"] == trace_id:
                t["scores"][score_name] = {"value": value, "comment": comment}
                break

        if self.langfuse:
            try:
                self.langfuse.score(
                    trace_id=trace_id,
                    name=score_name,
                    value=value,
                    comment=comment
                )
            except Exception as e:
                logger.debug(f"Langfuse score log error: {e}")

    def get_recent_traces(self, limit: int = 15) -> List[Dict[str, Any]]:
        return self.local_traces[:limit]

observability = ObservabilityManager()
