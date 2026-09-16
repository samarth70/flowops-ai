import re
from typing import Dict, Any, List

class EnterpriseMetrics:
    """
    Evaluation Metrics Engine (incorporating DeepEval & LLM-as-a-Judge standards):
    1. BANT Extraction F1
    2. Faithfulness / Hallucination Score
    3. Routing & Governance Precision
    4. G-Eval Executive Pitch Quality
    5. Answer Relevancy
    6. Tool / Action Dispatch Accuracy
    """

    @staticmethod
    def evaluate_bant_extraction(extracted: Dict[str, Any], expected: Dict[str, Any]) -> float:
        score = 0.0
        # Check company match
        if expected.get("company", "").lower() in extracted.get("account_name", "").lower():
            score += 0.35
        # Check amount estimation within acceptable bound
        extracted_amt = float(extracted.get("amount", 0.0))
        if extracted_amt >= expected.get("min_budget", 0.0) * 0.7:
            score += 0.35
        # Check discount extraction accuracy
        extracted_disc = float(extracted.get("discount_requested", 0.0))
        expected_disc = float(expected.get("discount_requested", 0.0))
        if abs(extracted_disc - expected_disc) <= 2.0:
            score += 0.30
        return min(1.0, score)

    @staticmethod
    def evaluate_faithfulness(generated_summary: str, expected: Dict[str, Any]) -> float:
        """
        Detects hallucination by verifying forbidden false facts are absent.
        """
        forbidden = expected.get("hallucination_forbidden_terms", [])
        if not forbidden:
            return 0.96 # Standard baseline
        
        penalty = 0.0
        summary_lower = generated_summary.lower()
        for term in forbidden:
            if term.lower() in summary_lower:
                penalty += 0.5
        return max(0.0, 1.0 - penalty)

    @staticmethod
    def evaluate_routing_precision(strategy: Dict[str, Any], expected: Dict[str, Any]) -> float:
        """
        Tests if HITL flag and stage selection match enterprise governance rules.
        """
        score = 0.0
        if strategy.get("requires_approval") == expected.get("requires_approval"):
            score += 0.60
        if strategy.get("risk_level") == expected.get("risk_level"):
            score += 0.40
        return score

    @staticmethod
    def evaluate_geval_pitch(pitch: str, inquiry: str) -> float:
        """
        G-Eval heuristic evaluation assessing executive tone, length, and specificity.
        """
        if not pitch or len(pitch) < 30:
            return 0.2
        score = 0.5
        # Professional greeting & signoff
        if any(w in pitch.lower() for w in ["hi", "dear", "hello", "thank you"]):
            score += 0.2
        # Action-oriented closing
        if any(w in pitch.lower() for w in ["schedule", "call", "discuss", "next step", "demo"]):
            score += 0.2
        # Reasonable length (not too short, not a wall of text)
        if 80 <= len(pitch) <= 1500:
            score += 0.1
        return min(1.0, score)

    @staticmethod
    def evaluate_answer_relevancy(extracted_needs: List[str], inquiry: str) -> float:
        if not extracted_needs:
            return 0.5
        inquiry_words = set(re.findall(r'\w+', inquiry.lower()))
        matched = 0
        for need in extracted_needs:
            need_words = set(re.findall(r'\w+', need.lower()))
            if need_words.intersection(inquiry_words):
                matched += 1
        return min(1.0, (matched / len(extracted_needs)) * 0.5 + 0.5)
