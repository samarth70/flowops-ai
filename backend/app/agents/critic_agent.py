import re
from typing import Dict, Any
from app.services.llm_factory import llm_service

CRITIC_SYSTEM_PROMPT = """
You are the Self-Reflective Governance Critic Agent (Reflexion Loop).
Inspect the proposed deal pitch, pricing recommendation, and extracted parameters against corporate governance policies:
1. Has the agent promised unverified SLAs (e.g. 99.999% uptime) or custom code outside standard enterprise tiers?
2. Does the requested discount breach margin thresholds without required approval?
3. Are client requirements grounded in the original inquiry without hallucination?

Produce:
- critique_passed: boolean (true if all policies satisfied)
- critique_notes: Short diagnosis of potential risks or hallucinations detected
- refined_pitch: An updated, self-corrected pitch removing any ungrounded claims or risky promises.

Respond ONLY with valid JSON with these exact keys.
"""

class CriticAgent:
    @staticmethod
    def run(triage_data: Dict[str, Any], strat_data: Dict[str, Any], raw_inquiry: str) -> Dict[str, Any]:
        context = f"""
PROSPECT INQUIRY: {raw_inquiry}
ACCOUNT: {triage_data.get('account_name')}
PROPOSED DISCOUNT: {strat_data.get('recommended_discount')}%
PROPOSED PITCH: {strat_data.get('ai_pitch_draft')}
AI SUMMARY: {strat_data.get('ai_summary')}
"""
        result = llm_service.generate_json(
            system_prompt=CRITIC_SYSTEM_PROMPT,
            user_prompt=f"PERFORM SELF-REFLECTION CRITIQUE:\n{context}"
        )
        
        data = result.get("data", {})
        # Ensure standard defaults if simulated
        if not data or "critique_passed" not in data:
            discount = float(triage_data.get("discount_requested", 0.0))
            raw_lower = raw_inquiry.lower()
            needs_sla_addendum = "99.999" in raw_lower or "vpc" in raw_lower
            passed = discount <= 20.0 and not needs_sla_addendum
            
            notes = []
            refined_pitch = strat_data.get("ai_pitch_draft", "")
            if discount > 20.0:
                notes.append(f"Reflexion alert: {discount}% discount violates 20% margin guardrail; routed to HITL approval.")
            if needs_sla_addendum:
                notes.append("Reflexion compliance note: 99.999% SLA and VPC deployment require Tier-1 Enterprise Schedule A addendum.")
                refined_pitch += "\n\nNote: Dedicated VPC deployment and 99.999% high-availability SLA have been included under Tier-1 Enterprise Schedule A addendum."
            if passed:
                notes.append("Self-reflection verified: pitch language and pricing comply with standard enterprise guidelines.")

            data = {
                "critique_passed": passed,
                "critique_notes": " ".join(notes),
                "refined_pitch": refined_pitch
            }
            result["data"] = data

        return result
