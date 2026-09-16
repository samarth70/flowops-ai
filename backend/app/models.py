from datetime import datetime
from typing import Optional, List, Dict, Any
from sqlalchemy import Column, Integer, String, Float, Boolean, Text, DateTime, JSON
from sqlalchemy.orm import declarative_base

Base = declarative_base()

class Opportunity(Base):
    __tablename__ = "opportunities"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    title = Column(String(255), nullable=False)
    account_name = Column(String(255), nullable=False)
    contact_name = Column(String(255), nullable=True)
    contact_email = Column(String(255), nullable=True)
    
    # Financials & Stage
    amount = Column(Float, default=0.0)
    stage = Column(String(50), default="New") 
    # Stages: New, Discovery, Value Proposition, Proposal/Quote, Negotiation, Closed Won, Closed Lost
    probability = Column(Integer, default=10) # 10% - 100%
    
    # BANT Scoring (0 - 25 each, total 0 - 100)
    bant_budget = Column(Integer, default=0)
    bant_authority = Column(Integer, default=0)
    bant_need = Column(Integer, default=0)
    bant_timeline = Column(Integer, default=0)
    bant_score = Column(Integer, default=0)
    
    # Risk & Governance / HITL
    discount_requested = Column(Float, default=0.0) # e.g. 25.0 for 25%
    discount_approved = Column(Float, default=0.0)
    risk_level = Column(String(20), default="LOW") # LOW, MEDIUM, HIGH, CRITICAL
    requires_approval = Column(Boolean, default=False)
    approval_status = Column(String(20), default="NOT_REQUIRED") # NOT_REQUIRED, PENDING, APPROVED, REJECTED
    approval_notes = Column(Text, nullable=True)

    # AI Outputs
    raw_inquiry = Column(Text, nullable=True)
    ai_summary = Column(Text, nullable=True)
    ai_recommended_strategy = Column(Text, nullable=True)
    ai_pitch_draft = Column(Text, nullable=True)
    ai_next_step = Column(String(255), nullable=True)
    
    # Observability
    langfuse_trace_id = Column(String(100), nullable=True)
    llm_model_used = Column(String(100), default="groq-llama-3.3-70b")
    latency_ms = Column(Integer, default=0)
    total_tokens = Column(Integer, default=0)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "title": self.title,
            "account_name": self.account_name,
            "contact_name": self.contact_name,
            "contact_email": self.contact_email,
            "amount": self.amount,
            "stage": self.stage,
            "probability": self.probability,
            "bant": {
                "budget": self.bant_budget,
                "authority": self.bant_authority,
                "need": self.bant_need,
                "timeline": self.bant_timeline,
                "total_score": self.bant_score
            },
            "governance": {
                "discount_requested": self.discount_requested,
                "discount_approved": self.discount_approved,
                "risk_level": self.risk_level,
                "requires_approval": self.requires_approval,
                "approval_status": self.approval_status,
                "approval_notes": self.approval_notes
            },
            "ai_insights": {
                "summary": self.ai_summary,
                "recommended_strategy": self.ai_recommended_strategy,
                "pitch_draft": self.ai_pitch_draft,
                "next_step": self.ai_next_step
            },
            "telemetry": {
                "trace_id": self.langfuse_trace_id,
                "model": self.llm_model_used,
                "latency_ms": self.latency_ms,
                "total_tokens": self.total_tokens
            },
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }

class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    opportunity_id = Column(Integer, nullable=True)
    actor = Column(String(100), default="Agentic Workflow")
    action = Column(String(100), nullable=False)
    details = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "opportunity_id": self.opportunity_id,
            "actor": self.actor,
            "action": self.action,
            "details": self.details,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }

class EvaluationRun(Base):
    __tablename__ = "evaluation_runs"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    run_name = Column(String(100), nullable=False)
    model_name = Column(String(100), nullable=False)
    total_test_cases = Column(Integer, default=0)
    passed_test_cases = Column(Integer, default=0)
    
    # 7 Evaluation Metrics (Normalized 0.0 to 1.0)
    bant_extraction_score = Column(Float, default=0.0)
    faithfulness_score = Column(Float, default=0.0) # Hallucination check
    answer_relevancy_score = Column(Float, default=0.0)
    routing_precision_score = Column(Float, default=0.0) # HITL & Stage routing
    geval_pitch_quality_score = Column(Float, default=0.0)
    tool_selection_score = Column(Float, default=0.0)
    avg_latency_ms = Column(Float, default=0.0)
    
    details_json = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "run_name": self.run_name,
            "model_name": self.model_name,
            "total_test_cases": self.total_test_cases,
            "passed_test_cases": self.passed_test_cases,
            "metrics": {
                "bant_extraction": round(self.bant_extraction_score or 0.0, 3),
                "faithfulness": round(self.faithfulness_score or 0.0, 3),
                "answer_relevancy": round(self.answer_relevancy_score or 0.0, 3),
                "routing_precision": round(self.routing_precision_score or 0.0, 3),
                "geval_pitch_quality": round(self.geval_pitch_quality_score or 0.0, 3),
                "tool_selection": round(self.tool_selection_score or 0.0, 3),
                "avg_latency_ms": round(self.avg_latency_ms or 0.0, 1)
            },
            "details": self.details_json,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }
