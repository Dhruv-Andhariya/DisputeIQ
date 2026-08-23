from typing import List, Optional
from app.models.domain import (
    VerificationCheckResult, VerificationStatus, VerificationSeverity,
    EvidenceReadinessScore, AIReasoningOutput, DecisionResult, FinalDecision
)
from app.core.config import settings

class DecisionEngine:
    @staticmethod
    def evaluate_decision(
        verification_results: List[VerificationCheckResult],
        readiness_score: EvidenceReadinessScore,
        ai_analysis: Optional[AIReasoningOutput] = None
    ) -> DecisionResult:
        """
        Combines deterministic verification results, readiness score, and AI reasoning.
        Enforces absolute safety override rules: DETERMINISTIC CONFLICTS ALWAYS WIN OVER AI.
        """
        reasoning_summary: List[str] = []
        
        # Check for critical or high severity deterministic verification failures or warnings
        critical_conflicts = [
            r for r in verification_results 
            if (r.status == VerificationStatus.FAILED and r.severity in [VerificationSeverity.CRITICAL, VerificationSeverity.HIGH])
        ]
        
        warning_conflicts = [
            r for r in verification_results
            if (r.status == VerificationStatus.WARNING and r.severity == VerificationSeverity.HIGH)
        ]
        
        # -------------------------------------------------------------
        # SAFETY OVERRIDE RULE 1: Deterministic conflict detected!
        # -------------------------------------------------------------
        if critical_conflicts:
            conflict_msgs = [f"• {c.check}: {c.message}" for c in critical_conflicts]
            reasoning_summary.append("SAFETY OVERRIDE TRIGGERED: Deterministic verification detected critical evidence conflict(s).")
            reasoning_summary.extend(conflict_msgs)
            
            ai_rec_str = ai_analysis.recommendation.value if ai_analysis else "N/A"
            reasoning_summary.append(f"AI recommendation was '{ai_rec_str}', but auto-action was BLOCKED by deterministic safety rules.")
            
            return DecisionResult(
                final_decision=FinalDecision.HUMAN_REVIEW,
                confidence=0.0,
                recommended_action="Escalate to Human Analyst. Automatic contesting is blocked due to critical verification failure.",
                safety_override_triggered=True,
                override_reason=f"Critical verification failure in {critical_conflicts[0].check}: {critical_conflicts[0].message}",
                reasoning_summary=reasoning_summary
            )

        if warning_conflicts:
            conflict_msgs = [f"• {c.check}: {c.message}" for c in warning_conflicts]
            reasoning_summary.append("HIGH SEVERITY WARNING: Ambiguous or weak evidence detected.")
            reasoning_summary.extend(conflict_msgs)
            
            return DecisionResult(
                final_decision=FinalDecision.HUMAN_REVIEW,
                confidence=0.65,
                recommended_action="Escalate to Human Analyst due to high-severity verification warnings (weak signature / category conflict).",
                safety_override_triggered=True,
                override_reason=f"Verification warning in {warning_conflicts[0].check}: {warning_conflicts[0].message}",
                reasoning_summary=reasoning_summary
            )

        # -------------------------------------------------------------
        # SAFETY OVERRIDE RULE 2: AI analysis unavailable or failed
        # -------------------------------------------------------------
        if not ai_analysis:
            reasoning_summary.append("AI reasoning service unavailable. Falling back safely to Human Review.")
            return DecisionResult(
                final_decision=FinalDecision.HUMAN_REVIEW,
                confidence=0.5,
                recommended_action="Escalate to Human Analyst for manual evaluation (AI reasoning unavailable).",
                safety_override_triggered=True,
                override_reason="AI Reasoning service output was unavailable or unparseable.",
                reasoning_summary=reasoning_summary
            )

        # -------------------------------------------------------------
        # SAFETY OVERRIDE RULE 3: Low evidence readiness score (< 50)
        # -------------------------------------------------------------
        if readiness_score.total_score < 50.0:
            reasoning_summary.append(f"Evidence Readiness Score ({readiness_score.total_score}/100) is below acceptable threshold.")
            return DecisionResult(
                final_decision=FinalDecision.HUMAN_REVIEW,
                confidence=ai_analysis.confidence,
                recommended_action="Escalate to Human Analyst to request missing merchant documentation.",
                safety_override_triggered=True,
                override_reason=f"Insufficient evidence readiness score ({readiness_score.total_score}/100).",
                reasoning_summary=reasoning_summary
            )

        # -------------------------------------------------------------
        # SAFETY OVERRIDE RULE 4: Low AI confidence (< threshold)
        # -------------------------------------------------------------
        if ai_analysis.confidence < settings.CONFIDENCE_THRESHOLD:
            reasoning_summary.append(f"AI Confidence ({ai_analysis.confidence:.2f}) is below minimum threshold ({settings.CONFIDENCE_THRESHOLD}).")
            return DecisionResult(
                final_decision=FinalDecision.HUMAN_REVIEW,
                confidence=ai_analysis.confidence,
                recommended_action="Escalate to Human Analyst due to low AI decision confidence.",
                safety_override_triggered=False,
                override_reason=f"AI confidence {ai_analysis.confidence:.2f} < threshold {settings.CONFIDENCE_THRESHOLD}.",
                reasoning_summary=reasoning_summary
            )

        # -------------------------------------------------------------
        # STANDARD DECISIONS: Pass all safety checks
        # -------------------------------------------------------------
        ai_rec = ai_analysis.recommendation
        
        if ai_rec == FinalDecision.CONTEST:
            reasoning_summary.append("All deterministic checks passed cleanly. High evidence readiness and high AI confidence.")
            reasoning_summary.extend(ai_analysis.reasoning)
            return DecisionResult(
                final_decision=FinalDecision.CONTEST,
                confidence=ai_analysis.confidence,
                recommended_action="Prepare and submit dispute contest package to payment gateway.",
                safety_override_triggered=False,
                override_reason=None,
                reasoning_summary=reasoning_summary
            )
            
        elif ai_rec == FinalDecision.DO_NOT_CONTEST:
            reasoning_summary.append("AI reasoning identified conclusive evidence supporting customer chargeback.")
            reasoning_summary.extend(ai_analysis.reasoning)
            return DecisionResult(
                final_decision=FinalDecision.DO_NOT_CONTEST,
                confidence=ai_analysis.confidence,
                recommended_action="Accept dispute. Do not contest as merchant documentation is unviable.",
                safety_override_triggered=False,
                override_reason=None,
                reasoning_summary=reasoning_summary
            )
            
        else:
            reasoning_summary.append("AI recommended Human Review based on contextual nuances.")
            reasoning_summary.extend(ai_analysis.reasoning)
            return DecisionResult(
                final_decision=FinalDecision.HUMAN_REVIEW,
                confidence=ai_analysis.confidence,
                recommended_action="Escalate to Human Analyst for expert dispute resolution.",
                safety_override_triggered=False,
                override_reason=None,
                reasoning_summary=reasoning_summary
            )
