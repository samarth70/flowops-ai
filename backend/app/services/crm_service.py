from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from app.models import Opportunity, AuditLog
from datetime import datetime

class CRMService:
    @staticmethod
    def get_all_opportunities(db: Session) -> List[Opportunity]:
        return db.query(Opportunity).order_by(Opportunity.updated_at.desc()).all()

    @staticmethod
    def get_opportunity(db: Session, opp_id: int) -> Optional[Opportunity]:
        return db.query(Opportunity).filter(Opportunity.id == opp_id).first()

    @staticmethod
    def create_opportunity(db: Session, data: Dict[str, Any]) -> Opportunity:
        opp = Opportunity(
            title=data.get("title", "New Inbound Deal"),
            account_name=data.get("account_name", "Prospective Account"),
            contact_name=data.get("contact_name", "Unknown Contact"),
            contact_email=data.get("contact_email", "lead@company.com"),
            amount=data.get("amount", 25000.0),
            stage=data.get("stage", "New"),
            probability=data.get("probability", 10),
            bant_budget=data.get("bant_budget", 0),
            bant_authority=data.get("bant_authority", 0),
            bant_need=data.get("bant_need", 0),
            bant_timeline=data.get("bant_timeline", 0),
            bant_score=data.get("bant_score", 0),
            discount_requested=data.get("discount_requested", 0.0),
            discount_approved=data.get("discount_approved", 0.0),
            risk_level=data.get("risk_level", "LOW"),
            requires_approval=data.get("requires_approval", False),
            approval_status=data.get("approval_status", "NOT_REQUIRED"),
            approval_notes=data.get("approval_notes"),
            raw_inquiry=data.get("raw_inquiry"),
            ai_summary=data.get("ai_summary"),
            ai_recommended_strategy=data.get("ai_recommended_strategy"),
            ai_pitch_draft=data.get("ai_pitch_draft"),
            ai_next_step=data.get("ai_next_step"),
            langfuse_trace_id=data.get("langfuse_trace_id"),
            llm_model_used=data.get("llm_model_used", "groq-llama-3.3-70b"),
            latency_ms=data.get("latency_ms", 0),
            total_tokens=data.get("total_tokens", 0)
        )
        db.add(opp)
        db.commit()
        db.refresh(opp)

        audit = AuditLog(
            opportunity_id=opp.id,
            actor="Agentic Lead Desk",
            action="DEAL_CREATED",
            details=f"Created deal '{opp.title}' with amount ${opp.amount:,.2f}. Initial Stage: {opp.stage}"
        )
        db.add(audit)
        db.commit()
        return opp

    @staticmethod
    def update_stage(db: Session, opp_id: int, new_stage: str, actor: str = "Sales User") -> Optional[Opportunity]:
        opp = db.query(Opportunity).filter(Opportunity.id == opp_id).first()
        if not opp:
            return None

        old_stage = opp.stage
        opp.stage = new_stage

        # Update probability based on standard enterprise sales pipeline
        stage_probs = {
            "New": 10,
            "Discovery": 25,
            "Value Proposition": 50,
            "Proposal/Quote": 65,
            "Negotiation": 80,
            "Closed Won": 100,
            "Closed Lost": 0
        }
        opp.probability = stage_probs.get(new_stage, opp.probability)
        opp.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(opp)

        audit = AuditLog(
            opportunity_id=opp.id,
            actor=actor,
            action="STAGE_UPDATED",
            details=f"Moved stage from '{old_stage}' -> '{new_stage}' (Probability: {opp.probability}%)"
        )
        db.add(audit)
        db.commit()
        return opp

    @staticmethod
    def handle_hitl_approval(db: Session, opp_id: int, approved: bool, notes: str, approver: str = "Sales Director") -> Optional[Opportunity]:
        opp = db.query(Opportunity).filter(Opportunity.id == opp_id).first()
        if not opp:
            return None

        if approved:
            opp.approval_status = "APPROVED"
            opp.discount_approved = opp.discount_requested
            opp.requires_approval = False
            opp.stage = "Proposal/Quote" if opp.stage == "Discovery" or opp.stage == "New" else opp.stage
            action_desc = f"APPROVED requested discount of {opp.discount_requested}%. Notes: {notes}"
        else:
            opp.approval_status = "REJECTED"
            opp.discount_approved = 0.0
            opp.requires_approval = False
            action_desc = f"REJECTED requested discount of {opp.discount_requested}%. Retaining standard pricing. Notes: {notes}"

        opp.approval_notes = notes
        opp.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(opp)

        audit = AuditLog(
            opportunity_id=opp.id,
            actor=approver,
            action="HITL_DECISION",
            details=action_desc
        )
        db.add(audit)
        db.commit()
        return opp

    @staticmethod
    def get_audit_logs(db: Session, opp_id: Optional[int] = None, limit: int = 25) -> List[AuditLog]:
        query = db.query(AuditLog)
        if opp_id:
            query = query.filter(AuditLog.opportunity_id == opp_id)
        return query.order_by(AuditLog.created_at.desc()).limit(limit).all()

crm_service = CRMService()
