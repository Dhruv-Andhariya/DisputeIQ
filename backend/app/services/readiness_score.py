from typing import List, Optional
from app.models.domain import (
    Evidence, VerificationCheckResult, VerificationStatus, EvidenceCategory,
    EvidenceReadinessScore, ScoreComponent, Delivery
)

class ReadinessScoreCalculator:
    @staticmethod
    def calculate_score(
        evidence_list: List[Evidence],
        verification_results: List[VerificationCheckResult],
        delivery: Optional[Delivery]
    ) -> EvidenceReadinessScore:
        components: List[ScoreComponent] = []
        
        # 1. Required Evidence Completeness (Max 40 pts)
        categories = {ev.category for ev in evidence_list}
        has_pod = EvidenceCategory.PROOF_OF_DELIVERY in categories
        has_inv = EvidenceCategory.INVOICE in categories
        has_ord = EvidenceCategory.ORDER_CONFIRMATION in categories
        
        req_score = 0.0
        if has_pod: req_score += 20.0
        if has_inv: req_score += 10.0
        if has_ord: req_score += 10.0
        
        components.append(ScoreComponent(
            name="Required Evidence Completeness",
            score=req_score,
            max_score=40.0,
            explanation=f"Proof of Delivery ({'20/20' if has_pod else '0/20'}), Invoice ({'10/10' if has_inv else '0/10'}), Order Confirmation ({'10/10' if has_ord else '0/10'})."
        ))
        
        # 2. Evidence Data Consistency (Max 30 pts)
        failed_checks = [r for r in verification_results if r.status == VerificationStatus.FAILED]
        warning_checks = [r for r in verification_results if r.status == VerificationStatus.WARNING]
        
        consist_score = 30.0
        for f in failed_checks:
            if f.severity == "CRITICAL":
                consist_score -= 15.0
            elif f.severity == "HIGH":
                consist_score -= 10.0
            elif f.severity == "MEDIUM":
                consist_score -= 5.0
        for w in warning_checks:
            consist_score -= 2.0
            
        consist_score = max(0.0, consist_score)
        
        components.append(ScoreComponent(
            name="Evidence Data Consistency",
            score=consist_score,
            max_score=30.0,
            explanation=f"Deducted for {len(failed_checks)} failed consistency check(s) and {len(warning_checks)} warning(s)."
        ))
        
        # 3. Timeline & Delivery Support (Max 15 pts)
        time_score = 0.0
        if delivery and delivery.status == "DELIVERED":
            time_score += 10.0
            if delivery.signed_by:
                # Check if signed by direct recipient or receptionist/guard
                sb = delivery.signed_by.lower()
                if "desk" in sb or "guard" in sb or "reception" in sb:
                    time_score += 2.0  # Partial credit for third-party signature
                else:
                    time_score += 5.0  # Full credit for direct customer signature
                    
        # Check delivery date check failure
        del_check_failed = any(r.check == "delivery_date_validity" and r.status == VerificationStatus.FAILED for r in verification_results)
        if del_check_failed:
            time_score = 0.0
            
        components.append(ScoreComponent(
            name="Timeline & Delivery Verification",
            score=time_score,
            max_score=15.0,
            explanation=f"Carrier verified delivery ({'10/10' if delivery and delivery.status == 'DELIVERED' else '0/10'}), Recipient signature ({'5/5' if delivery and delivery.signed_by and 'desk' not in delivery.signed_by.lower() and 'guard' not in delivery.signed_by.lower() else '2/5 (Third Party)'})."
        ))
        
        # 4. Customer Communication Integrity (Max 15 pts)
        has_comm = EvidenceCategory.CUSTOMER_COMMUNICATION in categories
        comm_score = 15.0 if has_comm else 5.0
        
        components.append(ScoreComponent(
            name="Customer Communication Integrity",
            score=comm_score,
            max_score=15.0,
            explanation="Customer interaction logs present and verified." if has_comm else "No prior customer communication logs found."
        ))
        
        total = sum(c.score for c in components)
        total = round(min(100.0, max(0.0, total)), 1)
        
        if total >= 80.0:
            summary = "High Evidence Readiness: Documentation is comprehensive, consistent, and strong."
        elif total >= 55.0:
            summary = "Moderate Evidence Readiness: Minor evidence gaps or mild inconsistency detected."
        else:
            summary = "Low Evidence Readiness: Missing critical documents or severe data conflicts present."
            
        return EvidenceReadinessScore(
            total_score=total,
            components=components,
            summary=summary
        )
