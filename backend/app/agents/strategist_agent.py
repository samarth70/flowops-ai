from typing import Dict, Any
from app.services.llm_factory import llm_service

STRATEGIST_SYSTEM_PROMPT = """
You are the Executive Deal Strategist & Governance Agent.
Analyze the deal parameters, BANT score, and client requirements to build an enterprise deal strategy:
1. risk_level: "LOW", "MEDIUM", "HIGH", or "CRITICAL"
2. requires_approval: boolean (true if discount_requested > 20.0 or deal size > 75000 with discount > 15.0)
3. recommended_discount: recommended approved discount percentage (e.g. 10.0, 15.0)
4. suggested_stage: "Discovery", "Value Proposition", "Proposal/Quote", or "Negotiation"
5. ai_summary: High-level deal assessment (2-3 sentences)
6. ai_recommended_strategy: Pricing & negotiation playbook advice for the sales team
7. ai_pitch_draft: A tailored, professional outreach email addressed to the prospect
8. ai_next_step: Immediate actionable next step for the sales representative

Respond ONLY with valid JSON with these exact keys.
"""

class StrategistAgent:
    @staticmethod
    def run(deal_data: Dict[str, Any], qualification_data: Dict[str, Any]) -> Dict[str, Any]:
        context = f"""
ACCOUNT: {deal_data.get('account_name')}
CONTACT: {deal_data.get('contact_name')} ({deal_data.get('contact_email')})
AMOUNT: ${deal_data.get('amount', 0):,.2f}
DISCOUNT REQUESTED: {deal_data.get('discount_requested', 0.0)}%
BANT TOTAL SCORE: {qualification_data.get('total_score', 0)}/100 (Tier: {qualification_data.get('qualification_tier')})
JUSTIFICATION: {qualification_data.get('justification')}
PAIN POINTS: {', '.join(deal_data.get('extracted_needs', []))}
"""
        result = llm_service.generate_json(
            system_prompt=STRATEGIST_SYSTEM_PROMPT,
            user_prompt=f"DEVELOP DEAL STRATEGY AND GOVERNANCE:\n{context}"
        )

        # Enforce deterministic guardrail on top of LLM reasoning
        disc = float(deal_data.get("discount_requested", 0.0))
        amt = float(deal_data.get("amount", 0.0))
        data = result.get("data", {})

        if disc > 20.0 or (amt >= 75000.0 and disc > 15.0):
            data["requires_approval"] = True
            data["risk_level"] = "HIGH" if disc <= 30.0 else "CRITICAL"
        else:
            data["requires_approval"] = False

        result["data"] = data
        return result
