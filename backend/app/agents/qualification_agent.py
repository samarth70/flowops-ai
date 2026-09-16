from typing import Dict, Any
from app.services.llm_factory import llm_service

QUALIFICATION_SYSTEM_PROMPT = """
You are the BANT & ICP Qualification Agent for enterprise deal evaluation.
Evaluate the prospect data against standard BANT methodology:
- bant_budget: (0 to 25) Clarity, allocation, and sizing of budget.
- bant_authority: (0 to 25) Executive sponsorship, decision-maker involvement.
- bant_need: (0 to 25) Urgency and magnitude of business pain point.
- bant_timeline: (0 to 25) Defined purchasing horizon (immediate, Q3, next fiscal year).
- total_score: Sum of all 4 dimensions (0 to 100).
- qualification_tier: "TIER_1_ENTERPRISE" (score >= 80), "TIER_2_MIDMARKET" (score 60-79), or "TIER_3_SMB" (score < 60).
- justification: A concise 2-sentence rationale for the scores assigned.

Respond ONLY with valid JSON with these exact keys.
"""

class QualificationAgent:
    @staticmethod
    def run(deal_data: Dict[str, Any], raw_inquiry: str) -> Dict[str, Any]:
        context = f"""
COMPANY: {deal_data.get('account_name')}
ESTIMATED DEAL AMOUNT: ${deal_data.get('amount', 0):,.2f}
DISCOUNT REQUESTED: {deal_data.get('discount_requested', 0)}%
INTENT: {deal_data.get('intent')}
EXTRACTED NEEDS: {', '.join(deal_data.get('extracted_needs', []))}
RAW TEXT: {raw_inquiry}
"""
        result = llm_service.generate_json(
            system_prompt=QUALIFICATION_SYSTEM_PROMPT,
            user_prompt=f"QUALIFY THIS OPPORTUNITY:\n{context}"
        )
        return result
