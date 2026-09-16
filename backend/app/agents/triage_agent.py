import json
from typing import Dict, Any
from app.services.llm_factory import llm_service

TRIAGE_SYSTEM_PROMPT = """
You are the Lead Triage & Entity Extraction Agent for an enterprise B2B CRM Deal Desk.
Analyze the incoming prospect inquiry, email, or meeting note and extract:
1. account_name: company name
2. contact_name: person name (if available, else 'Sales Lead')
3. contact_email: email address or synthetic default
4. title: A professional opportunity title (e.g., 'Enterprise AI Automation - [Company]')
5. amount: Estimated deal value in USD (default 35000.0 if unspecified)
6. discount_requested: Any discount percentage mentioned (e.g., 20.0 for 20%), 0.0 if none
7. intent: LOW, MEDIUM, or HIGH
8. extracted_needs: list of key business pain points / requirements

Respond ONLY with valid JSON with these exact keys.
"""

class TriageAgent:
    @staticmethod
    def run(raw_inquiry: str) -> Dict[str, Any]:
        result = llm_service.generate_json(
            system_prompt=TRIAGE_SYSTEM_PROMPT,
            user_prompt=f"PROSPECT INQUIRY:\n{raw_inquiry}"
        )
        return result
