from typing import Dict, Any
from sqlalchemy.orm import Session
from app.services.crm_service import crm_service
from app.models import Opportunity

class DispatcherAgent:
    @staticmethod
    def run(
        db: Session,
        triage_data: Dict[str, Any],
        qualification_data: Dict[str, Any],
        strategy_data: Dict[str, Any],
        raw_inquiry: str,
        trace_id: str,
        model_used: str,
        latency_ms: int,
        total_tokens: int
    ) -> Opportunity:
        requires_approval = strategy_data.get("requires_approval", False)
        discount_requested = float(triage_data.get("discount_requested", 0.0))

        # Build opportunity payload
        deal_payload = {
            "title": triage_data.get("title", f"Enterprise Opportunity - {triage_data.get('account_name')}"),
            "account_name": triage_data.get("account_name", "Prospective Account"),
            "contact_name": triage_data.get("contact_name", "Alex Rivera"),
            "contact_email": triage_data.get("contact_email", "lead@company.com"),
            "amount": float(triage_data.get("amount", 35000.0)),
            "stage": "Discovery" if requires_approval else strategy_data.get("suggested_stage", "Proposal/Quote"),
            "probability": 25 if requires_approval else 60,
            
            # BANT
            "bant_budget": int(qualification_data.get("bant_budget", 20)),
            "bant_authority": int(qualification_data.get("bant_authority", 20)),
            "bant_need": int(qualification_data.get("bant_need", 20)),
            "bant_timeline": int(qualification_data.get("bant_timeline", 20)),
            "bant_score": int(qualification_data.get("total_score", 80)),
            
            # Governance
            "discount_requested": discount_requested,
            "discount_approved": 0.0 if requires_approval else float(strategy_data.get("recommended_discount", 10.0)),
            "risk_level": strategy_data.get("risk_level", "LOW"),
            "requires_approval": requires_approval,
            "approval_status": "PENDING" if requires_approval else "NOT_REQUIRED",
            "approval_notes": f"Flagged for Sales Director review: requested {discount_requested}% discount exceeds threshold." if requires_approval else "Within standard sales authorization limits.",
            
            # AI outputs
            "raw_inquiry": raw_inquiry,
            "ai_summary": strategy_data.get("ai_summary"),
            "ai_recommended_strategy": strategy_data.get("ai_recommended_strategy"),
            "ai_pitch_draft": strategy_data.get("ai_pitch_draft"),
            "ai_next_step": strategy_data.get("ai_next_step"),
            
            # Telemetry
            "langfuse_trace_id": trace_id,
            "llm_model_used": model_used,
            "latency_ms": latency_ms,
            "total_tokens": total_tokens
        }

        opportunity = crm_service.create_opportunity(db, deal_payload)
        return opportunity
