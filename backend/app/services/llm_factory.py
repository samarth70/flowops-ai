import os
import re
import json
import time
import logging
from typing import Dict, Any, Optional
from app.config import settings

logger = logging.getLogger("FlowOps.LLM")

class LLMFactory:
    """
    Unified LLM Client providing:
    - Primary inference with Groq Cloud (Free Tier, ultra-fast Llama-3.3-70B)
    - Automatic failover to Google Gemini Flash (Free Tier)
    - High-fidelity offline enterprise reasoning simulator when keys are unconfigured.
    """

    def __init__(self):
        self.groq_client = None
        self.gemini_client = None

        if settings.has_groq:
            try:
                from groq import Groq
                self.groq_client = Groq(api_key=settings.GROQ_API_KEY)
                logger.info("Groq API client initialized successfully.")
            except Exception as e:
                logger.warning(f"Failed to initialize Groq client: {e}")

        if settings.has_gemini:
            try:
                import google.generativeai as genai
                genai.configure(api_key=settings.GEMINI_API_KEY)
                self.gemini_client = genai
                logger.info("Google Gemini API client initialized successfully.")
            except Exception as e:
                logger.warning(f"Failed to initialize Gemini client: {e}")

    def generate_json(self, system_prompt: str, user_prompt: str, temperature: float = 0.2) -> Dict[str, Any]:
        start_time = time.time()
        
        # 1. Try Groq (Primary Free Tier)
        if self.groq_client:
            try:
                response = self.groq_client.chat.completions.create(
                    model=settings.GROQ_MODEL,
                    messages=[
                        {"role": "system", "content": system_prompt + "\nYou must reply with valid JSON only. Do not include markdown codeblocks or extra text."},
                        {"role": "user", "content": user_prompt}
                    ],
                    response_format={"type": "json_object"},
                    temperature=temperature,
                    max_tokens=2048
                )
                raw_text = response.choices[0].message.content
                parsed = json.loads(raw_text)
                latency = int((time.time() - start_time) * 1000)
                tokens = (response.usage.total_tokens if response.usage else 850)
                return {
                    "data": parsed,
                    "model": settings.GROQ_MODEL,
                    "provider": "groq",
                    "latency_ms": latency,
                    "tokens": tokens
                }
            except Exception as e:
                logger.warning(f"Groq generation failed, attempting Gemini failover: {e}")

        # 2. Try Gemini (Failover Free Tier)
        if self.gemini_client:
            try:
                model = self.gemini_client.GenerativeModel(
                    model_name=settings.GEMINI_MODEL,
                    generation_config={"response_mime_type": "application/json"}
                )
                combined = f"SYSTEM: {system_prompt}\n\nUSER: {user_prompt}"
                res = model.generate_content(combined)
                parsed = json.loads(res.text)
                latency = int((time.time() - start_time) * 1000)
                return {
                    "data": parsed,
                    "model": settings.GEMINI_MODEL,
                    "provider": "gemini",
                    "latency_ms": latency,
                    "tokens": 920
                }
            except Exception as e:
                logger.warning(f"Gemini generation failed: {e}")

        # 3. Fallback Offline Enterprise Mock Engine
        return self._mock_reasoning_engine(system_prompt, user_prompt, start_time)

    def _mock_reasoning_engine(self, system_prompt: str, user_prompt: str, start_time: float) -> Dict[str, Any]:
        text_lower = user_prompt.lower()
        time.sleep(0.15)
        latency = int((time.time() - start_time) * 1000)

        # Dynamic extraction from user_prompt
        company = "Enterprise Prospect Corp"
        if "global retail systems" in text_lower:
            company = "Global Retail Systems"
        elif "cloudfleet" in text_lower:
            company = "CloudFleet"
        elif "apex health" in text_lower:
            company = "Apex Health"
        elif "nexus telecommunications" in text_lower or "nexus" in text_lower:
            company = "Nexus Telecommunications"
        elif "acme" in text_lower:
            company = "Acme Global Logistics"
        elif "fintech" in text_lower:
            company = "Fintech Velocity Ltd"
        elif "nordic" in text_lower:
            company = "Nordic Scaleups Inc"
        else:
            # Try to match "at [Name]" or "We are [Name]"
            m = re.search(r'(?:at|we are|from)\s+([A-Z][a-zA-Z0-9\s]{2,25})', user_prompt)
            if m:
                company = m.group(1).strip()

        # Amount extraction
        amount = 35000.0
        amt_match = re.search(r'\$(\d+(?:,\d{3})*(?:\.\d+)?)\s*(k|m|thousand|million)?', user_prompt, re.IGNORECASE)
        if amt_match:
            num_str = amt_match.group(1).replace(",", "")
            multiplier = amt_match.group(2)
            base_amt = float(num_str)
            if multiplier and multiplier.lower().startswith('k'):
                base_amt *= 1000
            elif multiplier and multiplier.lower().startswith('m'):
                base_amt *= 1000000
            amount = base_amt
        else:
            amt_num = re.search(r'(\d+)\s*(?:k|thousand)', text_lower)
            if amt_num:
                amount = float(amt_num.group(1)) * 1000.0

        # Discount extraction
        discount = 0.0
        disc_match = re.search(r'(\d+)%\s*discount', text_lower)
        if disc_match:
            discount = float(disc_match.group(1))
        elif "discount" in text_lower:
            disc_match2 = re.search(r'discount.*?(\d+)%', text_lower)
            if disc_match2:
                discount = float(disc_match2.group(1))

        if "triage" in system_prompt.lower():
            return {
                "data": {
                    "account_name": company,
                    "contact_name": "Sarah Jenkins" if "acme" in text_lower else "Alex Rivera",
                    "contact_email": f"contact@{company.lower().replace(' ', '').replace(',', '')}.com",
                    "title": f"Enterprise AI Deal Desk Implementation - {company}",
                    "amount": amount,
                    "discount_requested": discount,
                    "intent": "HIGH" if amount > 50000 else "MEDIUM",
                    "extracted_needs": [
                        "Automate CRM inbound lead qualification",
                        "Multi-agent deal desk orchestration",
                        "Audit logging and compliance tracking"
                    ]
                },
                "model": "offline-enterprise-simulator",
                "provider": "offline-simulator",
                "latency_ms": latency,
                "tokens": 460
            }

        elif "qualification agent" in system_prompt.lower():
            is_urgent = "immediate" in text_lower or "friday" in text_lower or "q3" in text_lower
            b = 25 if amount >= 50000 else (15 if amount > 0 else 5)
            a = 25 if "cfo" in text_lower or "vp" in text_lower else 20
            n = 25 if "rfp" in text_lower or "immediate" in text_lower else 20
            t = 25 if is_urgent else 15
            total = b + a + n + t
            tier = "TIER_1_ENTERPRISE" if total >= 80 else ("TIER_2_MIDMARKET" if total >= 60 else "TIER_3_SMB")
            return {
                "data": {
                    "bant_budget": b,
                    "bant_authority": a,
                    "bant_need": n,
                    "bant_timeline": t,
                    "total_score": total,
                    "qualification_tier": tier,
                    "justification": f"Clear enterprise alignment with verified decision maker and ${amount:,.0f} budget horizon."
                },
                "model": "offline-enterprise-simulator",
                "provider": "offline-simulator",
                "latency_ms": latency,
                "tokens": 520
            }

        else: # Strategist Agent
            requires_approval = discount > 20.0 or (amount >= 75000.0 and discount > 15.0)
            risk = "HIGH" if discount > 20.0 else ("MEDIUM" if discount > 10.0 else "LOW")
            stage = "Negotiation" if discount > 20.0 else ("Discovery" if amount == 0 else "Proposal/Quote")
            
            pitch = f"Hello, thank you for reaching out to explore FlowOps AI for {company}. We have evaluated your requirement for CRM automation and structured an enterprise solution aligned with your goals. Let us schedule a brief executive demonstration this week to review the deployment blueprint and discuss next steps."
            
            return {
                "data": {
                    "risk_level": risk,
                    "requires_approval": requires_approval,
                    "recommended_discount": min(discount, 15.0),
                    "suggested_stage": stage,
                    "ai_summary": f"Strategic opportunity with {company} valued at ${amount:,.2f}. High intent with {discount}% discount request.",
                    "ai_recommended_strategy": "Present custom SLA bundle while capping discount at standard 15% enterprise guardrail.",
                    "ai_pitch_draft": pitch,
                    "ai_next_step": "Submit for VP Approval on discount exception" if requires_approval else "Deliver formal proposal package"
                },
                "model": "offline-enterprise-simulator",
                "provider": "offline-simulator",
                "latency_ms": latency,
                "tokens": 690
            }

llm_service = LLMFactory()
