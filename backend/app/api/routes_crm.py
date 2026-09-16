from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Dict, Any
from pydantic import BaseModel
from app.db import get_db
from app.services.crm_service import crm_service

router = APIRouter(prefix="/api/crm", tags=["CRM Operations"])

class StageUpdateRequest(BaseModel):
    stage: str
    actor: str = "Sales Representative"

class HITLApprovalRequest(BaseModel):
    approved: bool
    notes: str
    approver: str = "Sales Director"

@router.get("/deals")
def list_deals(db: Session = Depends(get_db)):
    deals = crm_service.get_all_opportunities(db)
    return [deal.to_dict() for deal in deals]

@router.get("/deals/{deal_id}")
def get_deal(deal_id: int, db: Session = Depends(get_db)):
    deal = crm_service.get_opportunity(db, deal_id)
    if not deal:
        raise HTTPException(status_code=404, detail=f"Deal #{deal_id} not found")
    return deal.to_dict()

@router.post("/deals/{deal_id}/stage")
def update_deal_stage(deal_id: int, payload: StageUpdateRequest, db: Session = Depends(get_db)):
    deal = crm_service.update_stage(db, deal_id, payload.stage, payload.actor)
    if not deal:
        raise HTTPException(status_code=404, detail=f"Deal #{deal_id} not found")
    return {"status": "success", "deal": deal.to_dict()}

@router.post("/deals/{deal_id}/hitl")
def process_hitl_decision(deal_id: int, payload: HITLApprovalRequest, db: Session = Depends(get_db)):
    deal = crm_service.handle_hitl_approval(db, deal_id, payload.approved, payload.notes, payload.approver)
    if not deal:
        raise HTTPException(status_code=404, detail=f"Deal #{deal_id} not found")
    return {
        "status": "success",
        "action": "APPROVED" if payload.approved else "REJECTED",
        "deal": deal.to_dict()
    }

@router.get("/audit-logs")
def get_audit_logs(deal_id: int = None, limit: int = 25, db: Session = Depends(get_db)):
    logs = crm_service.get_audit_logs(db, deal_id, limit)
    return [log.to_dict() for log in logs]
