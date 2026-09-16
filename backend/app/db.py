import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.config import settings
from app.models import Base, Opportunity, AuditLog, EvaluationRun

# Use SQLite by default, easily swapped with postgresql:// for Supabase
engine = create_engine(
    settings.DATABASE_URL,
    connect_args={"check_same_thread": False} if settings.DATABASE_URL.startswith("sqlite") else {}
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        # Seed initial enterprise pipeline if empty
        if db.query(Opportunity).count() == 0:
            sample_deals = [
                Opportunity(
                    title="Enterprise Cloud Migration & AI Workflow License",
                    account_name="Acme Global Logistics",
                    contact_name="Sarah Jenkins",
                    contact_email="s.jenkins@acmeglobal.com",
                    amount=85000.0,
                    stage="Proposal/Quote",
                    probability=60,
                    bant_budget=25,
                    bant_authority=20,
                    bant_need=25,
                    bant_timeline=20,
                    bant_score=90,
                    discount_requested=15.0,
                    discount_approved=15.0,
                    risk_level="MEDIUM",
                    requires_approval=False,
                    approval_status="APPROVED",
                    approval_notes="Approved standard 15% discount for multi-year contract commitment.",
                    raw_inquiry="Acme Logistics needs to migrate 400 dispatch agents to an automated CRM flow. Budget allocated: $90k. Timeline: Q3 go-live.",
                    ai_summary="High-fit enterprise prospect with approved budget and executive sponsor. Strong alignment with multi-agent deal desk module.",
                    ai_recommended_strategy="Offer enterprise onboarding package with dedicated SLA to solidify multi-year commitment.",
                    ai_pitch_draft="Hi Sarah, following up on our discussion regarding Acme's dispatch automation...",
                    ai_next_step="Send formal Master Services Agreement (MSA) and schedule technical kickoff.",
                    llm_model_used="groq-llama-3.3-70b",
                    latency_ms=1150,
                    total_tokens=1420
                ),
                Opportunity(
                    title="GenAI Customer Retention Co-Pilot",
                    account_name="Fintech Velocity Ltd",
                    contact_name="Marcus Vance",
                    contact_email="mvance@fintechvelocity.io",
                    amount=120000.0,
                    stage="Negotiation",
                    probability=75,
                    bant_budget=25,
                    bant_authority=25,
                    bant_need=25,
                    bant_timeline=20,
                    bant_score=95,
                    discount_requested=25.0,
                    discount_approved=0.0,
                    risk_level="HIGH",
                    requires_approval=True,
                    approval_status="PENDING",
                    approval_notes="Flagged: Requested 25% discount exceeds 20% margin guardrail on $120k ARR deal.",
                    raw_inquiry="We are looking to implement AI deal qualification across 50 sales reps. We need a 25% volume discount to sign before end of month.",
                    ai_summary="Tier-1 opportunity with immediate purchase intent. Heavily price-sensitive on upfront license fees.",
                    ai_recommended_strategy="Counter-offer: 15% discount on base license in exchange for 2-year contract or usage commit.",
                    ai_pitch_draft="Dear Marcus, we've reviewed the volume structure for your 50 sales reps...",
                    ai_next_step="Await VP of Sales review on the 25% discount exception request.",
                    llm_model_used="gemini-2.0-flash",
                    latency_ms=980,
                    total_tokens=1650
                ),
                Opportunity(
                    title="SMB Automated CRM Triage Pilot",
                    account_name="Nordic Scaleups Inc",
                    contact_name="Elena Rostova",
                    contact_email="elena@nordicscaleups.se",
                    amount=18000.0,
                    stage="Discovery",
                    probability=30,
                    bant_budget=15,
                    bant_authority=15,
                    bant_need=20,
                    bant_timeline=10,
                    bant_score=60,
                    discount_requested=5.0,
                    discount_approved=5.0,
                    risk_level="LOW",
                    requires_approval=False,
                    approval_status="NOT_REQUIRED",
                    raw_inquiry="We have 10 customer service reps handling ~500 leads/mo. Wondering if an AI agent can pre-classify inbound leads.",
                    ai_summary="Standard SMB prospect seeking lead classification. Timeline is flexible, budget under evaluation.",
                    ai_recommended_strategy="Offer self-serve 14-day proof of concept with sample dataset.",
                    ai_pitch_draft="Hi Elena, great connecting! Here is a 14-day POC walkthrough...",
                    ai_next_step="Deliver interactive POC workspace link.",
                    llm_model_used="groq-llama-3.1-8b",
                    latency_ms=620,
                    total_tokens=940
                )
            ]
            db.add_all(sample_deals)
            db.commit()

            # Seed initial audit log
            audit = AuditLog(
                opportunity_id=2,
                actor="HITL Governance Interceptor",
                action="FLAGGED_FOR_APPROVAL",
                details="Deal #2 flagged: Discount request of 25.0% on $120,000 ARR exceeds maximum automated policy threshold (20.0%)."
            )
            db.add(audit)
            db.commit()
    finally:
        db.close()
