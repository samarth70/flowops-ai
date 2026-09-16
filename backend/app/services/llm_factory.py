import os
import re
import json
import time
import logging
from typing import Dict, Any, Optional
from app.config import settings

logger = logging.getLogger("FlowOps.LLM")

def safe_extract_json(raw_text: str) -> Dict[str, Any]:
    text = raw_text.strip()
    if "```" in text:
        match = re.search(r"```(?:json)?\s*([\s\S]*?)\s*```", text)
        if match:
            text = match.group(1).strip()
        else:
            text = re.sub(r"^```(?:json)?\s*", "", text)
            text = re.sub(r"\s*```$", "", text)
    return json.loads(text.strip())

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
        
        # 1. Try Groq (Primary Free Tier with multi-model failover)
        if self.groq_client:
            # Candidate models ordered by performance and stability; handles deprecations
            groq_candidates = [
                settings.GROQ_MODEL,
                "llama-3.1-8b-instant",
                "llama3-70b-8192",
                "llama-3.1-70b-versatile",
                "llama-3.3-70b-versatile",
                "gemma2-9b-it"
            ]
            seen_groq = set()
            for model_name in groq_candidates:
                if not model_name or model_name in seen_groq:
                    continue
                seen_groq.add(model_name)

                try:
                    response = self.groq_client.chat.completions.create(
                        model=model_name,
                        messages=[
                            {"role": "system", "content": system_prompt + "\nYou must reply with valid JSON only. Do not include markdown codeblocks or extra text."},
                            {"role": "user", "content": user_prompt}
                        ],
                        response_format={"type": "json_object"},
                        temperature=temperature,
                        max_tokens=2048
                    )
                    raw_text = response.choices[0].message.content
                    parsed = safe_extract_json(raw_text)
                    latency = int((time.time() - start_time) * 1000)
                    tokens = (response.usage.total_tokens if response.usage else 850)
                    return {
                        "data": parsed,
                        "model": model_name,
                        "provider": "groq",
                        "latency_ms": latency,
                        "tokens": tokens
                    }
                except Exception as e:
                    err_str = str(e).lower()
                    if "401" in err_str or "invalid api key" in err_str or "invalid_api_key" in err_str:
                        logger.warning(f"Groq API authentication failed (401 invalid key). Cascading to Gemini failover: {e}")
                        break  # Key is invalid, no use retrying different models on same key
                    logger.warning(f"Groq model '{model_name}' failed or obsolete: {e}. Trying next candidate...")

        # 2. Try Gemini (Failover Free Tier with multi-model cascade)
        if self.gemini_client:
            gemini_candidates = [
                settings.GEMINI_MODEL,
                "gemini-2.0-flash",
                "gemini-1.5-flash",
                "gemini-1.5-pro"
            ]
            seen_gem = set()
            for gem_model in gemini_candidates:
                if not gem_model or gem_model in seen_gem:
                    continue
                seen_gem.add(gem_model)

                try:
                    model = self.gemini_client.GenerativeModel(
                        model_name=gem_model,
                        generation_config={"response_mime_type": "application/json"}
                    )
                    combined = f"SYSTEM: {system_prompt}\n\nUSER: {user_prompt}\n\nOutput only valid JSON."
                    res = model.generate_content(combined)
                    parsed = safe_extract_json(res.text)
                    latency = int((time.time() - start_time) * 1000)
                    return {
                        "data": parsed,
                        "model": gem_model,
                        "provider": "gemini",
                        "latency_ms": latency,
                        "tokens": 920
                    }
                except Exception as e:
                    logger.warning(f"Gemini model '{gem_model}' failed: {e}. Trying next Gemini candidate...")

        # 3. Fallback Offline Enterprise Mock Engine
        return self._mock_reasoning_engine(system_prompt, user_prompt, start_time)

    def _mock_reasoning_engine(self, system_prompt: str, user_prompt: str, start_time: float) -> Dict[str, Any]:
        text_lower = user_prompt.lower()
        time.sleep(0.15)
        latency = int((time.time() - start_time) * 1000)

        # Dynamic extraction from user_prompt
        company = "Enterprise Prospect Corp"
        # 1. Regex search for explicit company indicators
        comp_match = re.search(r'(?:at|we are|from|company:?|representing)\s+([A-Z][a-zA-Z0-9\s&]{2,30}?)(?:\.|\,|\n|!|\s+needs|\s+is|\s+want|\s+looking|\s+requesting)', user_prompt, re.IGNORECASE)
        if comp_match:
            candidate = comp_match.group(1).strip()
            # filter out non-company words
            if candidate.lower() not in ["the", "an", "our", "immediate", "urgent"]:
                company = candidate
        elif "cybershield" in text_lower:
            company = "CyberShield Security Corp"
        elif "nexus telecommunications" in text_lower or "nexus" in text_lower:
            company = "Nexus Telecommunications"
        elif "global retail" in text_lower:
            company = "Global Retail Systems"
        elif "cloudfleet" in text_lower:
            company = "CloudFleet"
        elif "apex health" in text_lower:
            company = "Apex Health Systems"
        elif "fintech velocity" in text_lower or "fintech" in text_lower:
            company = "FinTech Velocity Ltd"
        elif "acme" in text_lower:
            company = "Acme Global Logistics"
        elif "nordic" in text_lower:
            company = "Nordic Scaleups Inc"
        else:
            # Check for domain in email e.g. alex@company.com
            email_domain = re.search(r'@([a-zA-Z0-9\-]+)\.(?:com|org|io|net|se)', user_prompt)
            if email_domain:
                company = email_domain.group(1).capitalize() + " Corp"

        # Contact name extraction
        contact_name = "Alex Rivera"
        name_match = re.search(r'(?:my name is|i am|from)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)', user_prompt, re.IGNORECASE)
        if name_match:
            candidate_name = name_match.group(1).strip()
            if candidate_name.lower() not in ["enterprise", "sales", "vp", "cfo", "immediate"]:
                contact_name = candidate_name

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
        disc_match = re.search(r'(\d+)%\s*(?:discount|off|volume)', text_lower)
        if disc_match:
            discount = float(disc_match.group(1))
        elif "discount" in text_lower:
            disc_match2 = re.search(r'discount.*?(\d+)%', text_lower)
            if disc_match2:
                discount = float(disc_match2.group(1))

        # Dynamic needs extraction
        extracted_needs = []
        if "triage" in text_lower or "lead" in text_lower:
            extracted_needs.append("Automated inbound lead qualification and triage")
        if "crm" in text_lower:
            extracted_needs.append("Bidirectional CRM stage progression and opportunity tracking")
        if "sla" in text_lower or "99.9" in text_lower:
            extracted_needs.append("Enterprise SLA tier with high-availability commitment")
        if "soc2" in text_lower or "compliance" in text_lower or "iso" in text_lower or "security" in text_lower:
            extracted_needs.append("Enterprise SOC2 and compliance governance verification")
        if "discount" in text_lower:
            extracted_needs.append(f"Volume pricing evaluation (requested {discount}%)")
        if not extracted_needs:
            extracted_needs = ["Automate CRM workflow", "Multi-agent deal desk orchestration"]

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
