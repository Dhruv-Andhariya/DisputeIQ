from typing import List, Optional, Dict, Any
from app.core.config import settings
from app.models.domain import (
    Dispute, Payment, Order, Delivery, Evidence, EvidenceCategory,
    VerificationCheckResult, VerificationStatus, EvidenceReadinessScore,
    AIReasoningOutput, FinalDecision
)
from app.ai.prompts import SYSTEM_PROMPT, USER_PROMPT_TEMPLATE
from app.ai.guardrails import AIGuardrails

class AIService:
    @staticmethod
    def analyze_dispute(
        dispute: Dispute,
        payment: Optional[Payment],
        order: Optional[Order],
        delivery: Optional[Delivery],
        evidence_list: List[Evidence],
        verification_results: List[VerificationCheckResult],
        readiness_score: EvidenceReadinessScore
    ) -> AIReasoningOutput:
        """
        Sends controlled, verified context to Gemini LLM and receives structured investigation analysis.
        If Gemini API key is missing or call fails, returns a safe fallback reasoning output.
        """
        # Format verification check summary
        ver_lines = []
        has_critical_failure = False
        for v in verification_results:
            status_symbol = "✓" if v.status == VerificationStatus.PASSED else ("✗" if v.status == VerificationStatus.FAILED else "⚠️")
            ver_lines.append(f"[{status_symbol}] {v.check} ({v.severity.value}): {v.message} (Expected: {v.expected}, Actual: {v.actual})")
            if v.status == VerificationStatus.FAILED and v.severity in ["CRITICAL", "HIGH"]:
                has_critical_failure = True
        ver_summary = "\n".join(ver_lines)
        
        # Customer communication summary
        comm_ev = next((ev for ev in evidence_list if ev.category == EvidenceCategory.CUSTOMER_COMMUNICATION), None)
        comm_str = "No customer communication records attached."
        if comm_ev and isinstance(comm_ev.content, dict) and "messages" in comm_ev.content:
            msgs = comm_ev.content["messages"]
            comm_lines = [f"- [{m.get('sender')} @ {m.get('timestamp')}]: {m.get('text')}" for m in msgs]
            comm_str = "\n".join(comm_lines)
            
        user_prompt = USER_PROMPT_TEMPLATE.format(
            dispute_id=dispute.dispute_id,
            dispute_amount=dispute.amount,
            dispute_reason=dispute.reason.value if hasattr(dispute.reason, 'value') else str(dispute.reason),
            dispute_date=dispute.dispute_date,
            order_id=order.order_id if order else "N/A",
            payment_id=payment.payment_id if payment else "N/A",
            payment_amount=payment.amount if payment else 0.0,
            order_amount=order.total_amount if order else 0.0,
            customer_name=order.customer_name if order else "N/A",
            customer_email=order.customer_email if order else "N/A",
            carrier=delivery.carrier if delivery else "N/A",
            tracking_number=delivery.tracking_number if delivery else "N/A",
            delivery_status=delivery.status if delivery else "N/A",
            actual_delivery_date=delivery.actual_delivery_date if delivery else "N/A",
            signed_by=delivery.signed_by if delivery else "N/A",
            delivery_address=delivery.delivery_address if delivery else "N/A",
            verification_summary=ver_summary,
            readiness_score=readiness_score.total_score,
            readiness_summary=readiness_score.summary,
            customer_communication=comm_str
        )
        
        # Try calling Gemini API if key is present
        if settings.GEMINI_API_KEY and len(settings.GEMINI_API_KEY.strip()) > 5:
            try:
                from google import genai
                from google.genai import types
                
                client = genai.Client(api_key=settings.GEMINI_API_KEY)
                response = client.models.generate_content(
                    model=settings.GEMINI_MODEL,
                    contents=[
                        types.Content(role="user", parts=[types.Part.from_text(text=SYSTEM_PROMPT + "\n\n" + user_prompt)])
                    ],
                    config=types.GenerateContentConfig(
                        temperature=0.1,
                        response_mime_type="application/json"
                    )
                )
                
                if response and response.text:
                    parsed = AIGuardrails.validate_and_parse_json(response.text)
                    if parsed:
                        return parsed
            except Exception as e:
                print(f"[AIService] Gemini API call exception: {e}")

        # Rule-based fallback if LLM API fails or key is missing
        return AIService._rule_based_fallback(
            dispute=dispute,
            payment=payment,
            order=order,
            delivery=delivery,
            evidence_list=evidence_list,
            verification_results=verification_results,
            readiness_score=readiness_score,
            has_critical_failure=has_critical_failure
        )

    @staticmethod
    def _rule_based_fallback(
        dispute: Dispute,
        payment: Optional[Payment],
        order: Optional[Order],
        delivery: Optional[Delivery],
        evidence_list: List[Evidence],
        verification_results: List[VerificationCheckResult],
        readiness_score: EvidenceReadinessScore,
        has_critical_failure: bool
    ) -> AIReasoningOutput:
        """Deterministic reasoning synthesis used as safe fallback when LLM API is offline."""
        reasoning = []
        supporting = []
        missing = []
        risk_flags = []
        
        if has_critical_failure:
            for v in verification_results:
                if v.status == VerificationStatus.FAILED and v.severity in ["CRITICAL", "HIGH"]:
                    risk_flags.append(f"{v.check}: {v.message}")
            reasoning.append("Critical evidence inconsistencies detected during verification checks.")
            reasoning.append("Order or payment records fail factual alignment across merchant files.")
            
            return AIReasoningOutput(
                recommendation=FinalDecision.HUMAN_REVIEW,
                confidence=0.85,
                case_summary=f"Dispute {dispute.dispute_id} contains critical evidence contradictions blocking automated contesting.",
                reasoning=reasoning,
                supporting_evidence=supporting,
                missing_evidence=missing,
                risk_flags=risk_flags
            )

        # Missing evidence
        categories = {ev.category for ev in evidence_list}
        if EvidenceCategory.PROOF_OF_DELIVERY not in categories:
            missing.append("Proof of Delivery (Carrier Tracking)")
            risk_flags.append("No carrier proof of delivery attached to case file.")
            
        if delivery and delivery.status == "DELIVERED" and delivery.signed_by:
            supporting.append(f"Carrier {delivery.carrier} confirmed delivery signed by '{delivery.signed_by}' on {delivery.actual_delivery_date}.")
            reasoning.append(f"Valid proof of delivery confirmed on {delivery.actual_delivery_date}.")
            
        if payment and order and payment.amount == order.total_amount == dispute.amount:
            supporting.append(f"Payment amount ₹{payment.amount} perfectly matches order total and dispute claim.")
            reasoning.append("Financial records are fully consistent.")

        if not missing and not risk_flags and readiness_score.total_score >= 80.0:
            rec = FinalDecision.CONTEST
            conf = 0.92
            summary = f"Strong merchant defense: Complete verified documentation exists demonstrating full delivery of order {order.order_id if order else ''} prior to dispute filing."
        elif missing or readiness_score.total_score < 60.0:
            rec = FinalDecision.HUMAN_REVIEW
            conf = 0.70
            summary = f"Incomplete merchant evidence package: Additional documentation required for order {order.order_id if order else ''}."
        else:
            rec = FinalDecision.CONTEST
            conf = 0.82
            summary = f"Valid dispute defense package assembled for dispute {dispute.dispute_id}."

        return AIReasoningOutput(
            recommendation=rec,
            confidence=conf,
            case_summary=summary,
            reasoning=reasoning,
            supporting_evidence=supporting,
            missing_evidence=missing,
            risk_flags=risk_flags
        )
