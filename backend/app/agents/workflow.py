import asyncio
import time
from typing import Dict, Any, List, Optional, TypedDict
from sqlalchemy.orm import Session

from app.agents.triage_agent import TriageAgent
from app.agents.qualification_agent import QualificationAgent
from app.agents.strategist_agent import StrategistAgent
from app.agents.dispatcher_agent import DispatcherAgent
from app.services.observability import observability
from app.models import Opportunity

class DealDeskState(TypedDict):
    raw_inquiry: str
    triage_data: Dict[str, Any]
    qualification_data: Dict[str, Any]
    strategy_data: Dict[str, Any]
    opportunity_id: Optional[int]
    requires_approval: bool
    approval_status: str
    trace_id: str
    logs: List[str]
    current_step: str

class DealDeskWorkflow:
    """
    Multi-Agent LangGraph-Style Deal Desk Workflow:
    Triage Agent -> Qualification Agent -> Deal Strategist Agent -> HITL Interceptor -> CRM Dispatcher
    """

    @classmethod
    async def run_streaming(cls, raw_inquiry: str, db: Session):
        """
        Async generator for Server-Sent Events (SSE).
        Yields real-time step updates, thoughts, tool inputs/outputs, and final CRM record.
        """
        trace = observability.start_trace(
            name="Agentic_CRM_Deal_Desk_Run",
            metadata={"source": "inbound_chat", "raw_inquiry_length": len(raw_inquiry)}
        )
        trace_id = trace["id"]

        yield {
            "type": "workflow_started",
            "trace_id": trace_id,
            "message": "Workflow initiated: Ingesting inbound enterprise inquiry...",
            "timestamp": time.time()
        }
        await asyncio.sleep(0.4)

        # Step 1: Lead Triage
        yield {
            "type": "agent_step",
            "agent": "Lead Triage Agent",
            "status": "processing",
            "message": "Extracting entity parameters, deal size, and key customer pain points...",
            "timestamp": time.time()
        }
        t1 = time.time()
        triage_res = TriageAgent.run(raw_inquiry)
        triage_data = triage_res["data"]
        observability.add_span(
            trace,
            step_name="Triage_Agent",
            input_data={"raw_inquiry": raw_inquiry},
            output_data=triage_data,
            model=triage_res["model"],
            latency_ms=triage_res["latency_ms"],
            tokens=triage_res["tokens"]
        )
        yield {
            "type": "agent_step",
            "agent": "Lead Triage Agent",
            "status": "completed",
            "output": triage_data,
            "latency_ms": triage_res["latency_ms"],
            "model": triage_res["model"],
            "timestamp": time.time()
        }
        await asyncio.sleep(0.4)

        # Step 2: BANT Qualification
        yield {
            "type": "agent_step",
            "agent": "BANT & ICP Qualification Agent",
            "status": "processing",
            "message": "Evaluating Budget, Authority, Need, and Timeline against enterprise criteria...",
            "timestamp": time.time()
        }
        qual_res = QualificationAgent.run(triage_data, raw_inquiry)
        qual_data = qual_res["data"]
        observability.add_span(
            trace,
            step_name="Qualification_Agent",
            input_data=triage_data,
            output_data=qual_data,
            model=qual_res["model"],
            latency_ms=qual_res["latency_ms"],
            tokens=qual_res["tokens"]
        )
        yield {
            "type": "agent_step",
            "agent": "BANT & ICP Qualification Agent",
            "status": "completed",
            "output": qual_data,
            "latency_ms": qual_res["latency_ms"],
            "model": qual_res["model"],
            "timestamp": time.time()
        }
        await asyncio.sleep(0.4)

        # Step 3: Deal Strategist & Governance
        yield {
            "type": "agent_step",
            "agent": "Deal Strategist & Governance Agent",
            "status": "processing",
            "message": "Analyzing margin risk, generating customized pitch and discount recommendation...",
            "timestamp": time.time()
        }
        strat_res = StrategistAgent.run(triage_data, qual_data)
        strat_data = strat_res["data"]
        observability.add_span(
            trace,
            step_name="Strategist_Governance_Agent",
            input_data={"triage": triage_data, "qualification": qual_data},
            output_data=strat_data,
            model=strat_res["model"],
            latency_ms=strat_res["latency_ms"],
            tokens=strat_res["tokens"]
        )
        yield {
            "type": "agent_step",
            "agent": "Deal Strategist & Governance Agent",
            "status": "completed",
            "output": strat_data,
            "latency_ms": strat_res["latency_ms"],
            "model": strat_res["model"],
            "timestamp": time.time()
        }
        await asyncio.sleep(0.35)

        # Step 4: Self-Reflective Critic (Reflexion Loop)
        from app.agents.critic_agent import CriticAgent
        yield {
            "type": "agent_step",
            "agent": "Self-Reflective Critic Agent (Reflexion)",
            "status": "processing",
            "message": "Performing policy self-reflection, checking SLA grounding and anti-hallucination compliance...",
            "timestamp": time.time()
        }
        critic_res = CriticAgent.run(triage_data, strat_data, raw_inquiry)
        critic_data = critic_res["data"]
        observability.add_span(
            trace,
            step_name="Reflexion_Critic_Agent",
            input_data={"proposal": strat_data},
            output_data=critic_data,
            model=critic_res.get("model", "reflexion-engine"),
            latency_ms=critic_res.get("latency_ms", 200),
            tokens=critic_res.get("tokens", 180)
        )
        if critic_data.get("refined_pitch"):
            strat_data["ai_pitch_draft"] = critic_data["refined_pitch"]

        yield {
            "type": "agent_step",
            "agent": "Self-Reflective Critic Agent (Reflexion)",
            "status": "completed",
            "output": critic_data,
            "latency_ms": critic_res.get("latency_ms", 200),
            "model": critic_res.get("model", "reflexion-engine"),
            "timestamp": time.time()
        }
        await asyncio.sleep(0.35)

        # Step 5: Human-in-the-loop Interceptor check
        requires_approval = strat_data.get("requires_approval", False)
        if requires_approval:
            yield {
                "type": "hitl_flag",
                "risk_level": strat_data.get("risk_level", "HIGH"),
                "message": f"CRITICAL GUARDRAIL TRIGGERED: Discount of {triage_data.get('discount_requested', 0)}% requires Sales Director authorization.",
                "timestamp": time.time()
            }
            await asyncio.sleep(0.3)

        # Step 6: CRM Action Dispatcher
        yield {
            "type": "agent_step",
            "agent": "CRM Sync & Action Dispatcher",
            "status": "processing",
            "message": "Persisting Opportunity record and generating immutable audit trails...",
            "timestamp": time.time()
        }
        
        total_tokens = triage_res["tokens"] + qual_res["tokens"] + strat_res["tokens"]
        total_latency = int((time.time() - t1) * 1000)

        opp = DispatcherAgent.run(
            db=db,
            triage_data=triage_data,
            qualification_data=qual_data,
            strategy_data=strat_data,
            raw_inquiry=raw_inquiry,
            trace_id=trace_id,
            model_used=strat_res["model"],
            latency_ms=total_latency,
            total_tokens=total_tokens
        )

        observability.end_trace(trace, status="SUCCESS")

        yield {
            "type": "workflow_completed",
            "opportunity": opp.to_dict(),
            "trace_id": trace_id,
            "total_tokens": total_tokens,
            "total_latency_ms": total_latency,
            "langfuse_url": trace.get("external_url"),
            "message": f"Deal #{opp.id} ('{opp.title}') successfully created in CRM stage '{opp.stage}'.",
            "timestamp": time.time()
        }
