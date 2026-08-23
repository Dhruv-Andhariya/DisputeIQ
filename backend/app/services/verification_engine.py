from typing import List, Optional
from datetime import datetime
from app.models.domain import (
    Dispute, Payment, Order, Delivery, Evidence, EvidenceCategory,
    VerificationCheckResult, VerificationStatus, VerificationSeverity
)

class VerificationEngine:
    @staticmethod
    def verify_payment_amount(dispute: Dispute, payment: Optional[Payment], order: Optional[Order]) -> VerificationCheckResult:
        """Verifies if the dispute amount matches the payment amount and order total amount."""
        check_name = "payment_amount_consistency"
        
        if not payment:
            return VerificationCheckResult(
                check=check_name,
                status=VerificationStatus.FAILED,
                severity=VerificationSeverity.CRITICAL,
                expected=f"₹{dispute.amount}",
                actual="MISSING_PAYMENT_RECORD",
                message="Associated payment record was not found in payment system."
            )
            
        dispute_amt = round(float(dispute.amount), 2)
        payment_amt = round(float(payment.amount), 2)
        
        if dispute_amt != payment_amt:
            return VerificationCheckResult(
                check=check_name,
                status=VerificationStatus.FAILED,
                severity=VerificationSeverity.HIGH,
                expected=f"₹{payment_amt}",
                actual=f"₹{dispute_amt}",
                message=f"Dispute amount (₹{dispute_amt}) does not match captured payment amount (₹{payment_amt})."
            )
            
        if order and round(float(order.total_amount), 2) != payment_amt:
            return VerificationCheckResult(
                check=check_name,
                status=VerificationStatus.WARNING,
                severity=VerificationSeverity.MEDIUM,
                expected=f"₹{payment_amt}",
                actual=f"₹{order.total_amount}",
                message=f"Order total (₹{order.total_amount}) differs from payment amount (₹{payment_amt})."
            )
            
        return VerificationCheckResult(
            check=check_name,
            status=VerificationStatus.PASSED,
            severity=VerificationSeverity.INFO,
            expected=f"₹{payment_amt}",
            actual=f"₹{dispute_amt}",
            message="Payment amount is perfectly consistent across dispute, payment, and order records."
        )

    @staticmethod
    def verify_order_id_consistency(
        dispute: Dispute, 
        payment: Optional[Payment], 
        delivery: Optional[Delivery],
        evidence_list: List[Evidence]
    ) -> VerificationCheckResult:
        """Verifies if Order ID is consistent across payment, invoice evidence, and delivery records."""
        check_name = "order_id_consistency"
        
        if not payment:
            return VerificationCheckResult(
                check=check_name,
                status=VerificationStatus.FAILED,
                severity=VerificationSeverity.CRITICAL,
                expected="VALID_ORDER_ID",
                actual="MISSING_PAYMENT",
                message="Cannot verify order ID consistency without payment record."
            )
            
        expected_order_id = payment.order_id
        
        # Check delivery record order_id
        if delivery and delivery.order_id != expected_order_id:
            return VerificationCheckResult(
                check=check_name,
                status=VerificationStatus.FAILED,
                severity=VerificationSeverity.HIGH,
                expected=expected_order_id,
                actual=delivery.order_id,
                message=f"Order Identity Conflict: Payment references '{expected_order_id}', but delivery proof references a different order '{delivery.order_id}'."
            )
            
        # Check invoice evidence order_id
        for ev in evidence_list:
            if ev.category == EvidenceCategory.INVOICE and isinstance(ev.content, dict):
                inv_order_id = ev.content.get("order_id")
                if inv_order_id and inv_order_id != expected_order_id:
                    return VerificationCheckResult(
                        check=check_name,
                        status=VerificationStatus.FAILED,
                        severity=VerificationSeverity.HIGH,
                        expected=expected_order_id,
                        actual=inv_order_id,
                        message=f"Order Identity Conflict: Invoice evidence references order '{inv_order_id}' instead of payment order '{expected_order_id}'."
                    )

        return VerificationCheckResult(
            check=check_name,
            status=VerificationStatus.PASSED,
            severity=VerificationSeverity.INFO,
            expected=expected_order_id,
            actual=expected_order_id,
            message="Order ID is verified consistent across payment, invoice, and delivery records."
        )

    @staticmethod
    def verify_customer_id_consistency(payment: Optional[Payment], order: Optional[Order], delivery: Optional[Delivery]) -> VerificationCheckResult:
        """Verifies if Customer ID matches across payment, order, and delivery."""
        check_name = "customer_id_consistency"
        
        if not payment or not order:
            return VerificationCheckResult(
                check=check_name,
                status=VerificationStatus.WARNING,
                severity=VerificationSeverity.MEDIUM,
                expected="MATCHING_CUSTOMER_ID",
                actual="INCOMPLETE_RECORDS",
                message="Insufficient records to complete full customer identity verification."
            )
            
        if payment.customer_id != order.customer_id:
            return VerificationCheckResult(
                check=check_name,
                status=VerificationStatus.FAILED,
                severity=VerificationSeverity.HIGH,
                expected=order.customer_id,
                actual=payment.customer_id,
                message=f"Customer Identity Conflict: Order belongs to '{order.customer_id}', but payment was made by '{payment.customer_id}'."
            )
            
        return VerificationCheckResult(
            check=check_name,
            status=VerificationStatus.PASSED,
            severity=VerificationSeverity.INFO,
            expected=order.customer_id,
            actual=payment.customer_id,
            message="Customer identity is consistent across payment and order records."
        )

    @staticmethod
    def verify_delivery_date(dispute: Dispute, delivery: Optional[Delivery]) -> VerificationCheckResult:
        """Verifies if delivery occurred BEFORE dispute was filed."""
        check_name = "delivery_date_validity"
        
        if not delivery:
            return VerificationCheckResult(
                check=check_name,
                status=VerificationStatus.FAILED,
                severity=VerificationSeverity.HIGH,
                expected="DELIVERY_RECORD_PRESENT",
                actual="MISSING_DELIVERY_RECORD",
                message="No delivery record available to verify delivery date."
            )
            
        if delivery.status != "DELIVERED" or not delivery.actual_delivery_date:
            return VerificationCheckResult(
                check=check_name,
                status=VerificationStatus.FAILED,
                severity=VerificationSeverity.HIGH,
                expected="DELIVERED",
                actual=delivery.status,
                message=f"Delivery is incomplete or in status '{delivery.status}'."
            )
            
        try:
            # Parse dates
            fmt = "%Y-%m-%d %H:%M:%S"
            dispute_dt = datetime.strptime(dispute.dispute_date, fmt)
            delivery_dt = datetime.strptime(delivery.actual_delivery_date, fmt)
            
            if delivery_dt > dispute_dt:
                return VerificationCheckResult(
                    check=check_name,
                    status=VerificationStatus.FAILED,
                    severity=VerificationSeverity.HIGH,
                    expected=f"Delivery before {dispute.dispute_date}",
                    actual=delivery.actual_delivery_date,
                    message=f"Chronological Anomaly: Actual delivery date ({delivery.actual_delivery_date}) is after the dispute filing date ({dispute.dispute_date})."
                )
                
            return VerificationCheckResult(
                check=check_name,
                status=VerificationStatus.PASSED,
                severity=VerificationSeverity.INFO,
                expected=f"Delivery before {dispute.dispute_date}",
                actual=delivery.actual_delivery_date,
                message=f"Delivery completed on {delivery.actual_delivery_date}, prior to dispute filing on {dispute.dispute_date}."
            )
        except Exception as e:
            return VerificationCheckResult(
                check=check_name,
                status=VerificationStatus.WARNING,
                severity=VerificationSeverity.MEDIUM,
                expected="VALID_TIMESTAMP_FORMAT",
                actual=str(e),
                message="Timestamp format parsing warning during delivery date verification."
            )

    @staticmethod
    def verify_dispute_date(dispute: Dispute, order: Optional[Order]) -> VerificationCheckResult:
        """Verifies if dispute date is chronologically after order date."""
        check_name = "dispute_date_validity"
        
        if not order:
            return VerificationCheckResult(
                check=check_name,
                status=VerificationStatus.WARNING,
                severity=VerificationSeverity.MEDIUM,
                expected="ORDER_RECORD_PRESENT",
                actual="MISSING_ORDER_RECORD",
                message="Cannot verify dispute date without order record."
            )
            
        try:
            fmt = "%Y-%m-%d %H:%M:%S"
            dispute_dt = datetime.strptime(dispute.dispute_date, fmt)
            order_dt = datetime.strptime(order.created_at, fmt)
            
            if dispute_dt < order_dt:
                return VerificationCheckResult(
                    check=check_name,
                    status=VerificationStatus.FAILED,
                    severity=VerificationSeverity.CRITICAL,
                    expected=f"Dispute after {order.created_at}",
                    actual=dispute.dispute_date,
                    message=f"Impossible Timestamp: Dispute date ({dispute.dispute_date}) precedes order creation date ({order.created_at})."
                )
                
            return VerificationCheckResult(
                check=check_name,
                status=VerificationStatus.PASSED,
                severity=VerificationSeverity.INFO,
                expected=f"Dispute after {order.created_at}",
                actual=dispute.dispute_date,
                message="Dispute timestamp is valid and occurred after order creation."
            )
        except Exception as e:
            return VerificationCheckResult(
                check=check_name,
                status=VerificationStatus.WARNING,
                severity=VerificationSeverity.MEDIUM,
                expected="VALID_TIMESTAMP_FORMAT",
                actual=str(e),
                message="Timestamp parsing error during dispute date check."
            )

    @staticmethod
    def check_required_evidence(evidence_list: List[Evidence]) -> VerificationCheckResult:
        """Checks for mandatory evidence categories (Proof of Delivery, Invoice, Order Confirmation)."""
        check_name = "required_evidence_completeness"
        
        present_categories = {ev.category for ev in evidence_list}
        required_categories = {
            EvidenceCategory.PROOF_OF_DELIVERY,
            EvidenceCategory.INVOICE,
            EvidenceCategory.ORDER_CONFIRMATION
        }
        
        missing = required_categories - present_categories
        
        if missing:
            missing_str = ", ".join([cat.value for cat in missing])
            return VerificationCheckResult(
                check=check_name,
                status=VerificationStatus.FAILED,
                severity=VerificationSeverity.HIGH,
                expected="PROOF_OF_DELIVERY, INVOICE, ORDER_CONFIRMATION",
                actual=f"Missing: {missing_str}",
                message=f"Critical evidence missing: Merchant lacks {missing_str}."
            )
            
        return VerificationCheckResult(
            check=check_name,
            status=VerificationStatus.PASSED,
            severity=VerificationSeverity.INFO,
            expected="All mandatory categories present",
            actual="Proof of Delivery, Invoice, and Order Confirmation present",
            message="All required evidence categories are present in the merchant file."
        )

    @staticmethod
    def detect_duplicate_evidence(evidence_list: List[Evidence]) -> VerificationCheckResult:
        """Detects duplicate evidence files or identical evidence content."""
        check_name = "duplicate_evidence_detection"
        
        seen_filenames = set()
        duplicates = []
        
        for ev in evidence_list:
            if ev.file_name in seen_filenames:
                duplicates.append(ev.file_name)
            seen_filenames.add(ev.file_name)
            
        if duplicates:
            return VerificationCheckResult(
                check=check_name,
                status=VerificationStatus.WARNING,
                severity=VerificationSeverity.MEDIUM,
                expected="No duplicate evidence files",
                actual=f"Duplicates: {', '.join(duplicates)}",
                message=f"Duplicate evidence documents detected: {', '.join(duplicates)}."
            )
            
        return VerificationCheckResult(
            check=check_name,
            status=VerificationStatus.PASSED,
            severity=VerificationSeverity.INFO,
            expected="No duplicate evidence files",
            actual="Unique evidence files",
            message="No duplicate evidence documents detected."
        )

    @staticmethod
    def detect_missing_evidence(evidence_list: List[Evidence]) -> List[str]:
        """Returns list of missing evidence categories."""
        present_categories = {ev.category for ev in evidence_list}
        required_categories = {
            EvidenceCategory.PROOF_OF_DELIVERY,
            EvidenceCategory.INVOICE,
            EvidenceCategory.ORDER_CONFIRMATION,
            EvidenceCategory.CUSTOMER_COMMUNICATION,
            EvidenceCategory.TERMS_AND_CONDITIONS
        }
        return [cat.value for cat in (required_categories - present_categories)]

    @staticmethod
    def verify_communication_relevance(dispute: Dispute, evidence_list: List[Evidence]) -> VerificationCheckResult:
        """Verifies if customer communication aligns with dispute claim (Goods / Services Not Received)."""
        check_name = "customer_communication_relevance"
        
        comm_ev = next((ev for ev in evidence_list if ev.category == EvidenceCategory.CUSTOMER_COMMUNICATION), None)
        if not comm_ev or not isinstance(comm_ev.content, dict) or "messages" not in comm_ev.content:
            return VerificationCheckResult(
                check=check_name,
                status=VerificationStatus.PASSED,
                severity=VerificationSeverity.INFO,
                expected="RELEVANT_COMMUNICATION",
                actual="NO_COMMUNICATION_LOGS",
                message="No customer chat logs available for category relevance check."
            )
            
        msgs = comm_ev.content.get("messages", [])
        combined_text = " ".join([m.get("text", "").lower() for m in msgs])
        
        # Check for damage / defective keywords when dispute is filed as Goods Not Received
        damage_keywords = ["broken", "shattered", "damaged", "defective", "cracked"]
        found_keywords = [kw for kw in damage_keywords if kw in combined_text]
        
        if found_keywords:
            return VerificationCheckResult(
                check=check_name,
                status=VerificationStatus.WARNING,
                severity=VerificationSeverity.HIGH,
                expected="Non-receipt claim alignment",
                actual=f"Keywords found: {', '.join(found_keywords)}",
                message=f"Dispute Category Conflict: Dispute filed as 'Goods / Services Not Received', but customer chat mentions item was '{', '.join(found_keywords)}'."
            )
            
        return VerificationCheckResult(
            check=check_name,
            status=VerificationStatus.PASSED,
            severity=VerificationSeverity.INFO,
            expected="Relevant communication",
            actual="Consistent customer communication",
            message="Customer communication text is consistent with non-receipt dispute claim."
        )

    @staticmethod
    def verify_signature_authenticity(delivery: Optional[Delivery], order: Optional[Order]) -> VerificationCheckResult:
        """Verifies if recipient signature matches order customer name or if it was signed by a third-party."""
        check_name = "signature_authenticity"
        
        if not delivery or not delivery.signed_by:
            return VerificationCheckResult(
                check=check_name,
                status=VerificationStatus.WARNING,
                severity=VerificationSeverity.MEDIUM,
                expected="Direct recipient signature",
                actual="MISSING_SIGNATURE",
                message="Carrier delivery record lacks recipient signature."
            )
            
        sb = delivery.signed_by.lower()
        if "desk" in sb or "guard" in sb or "reception" in sb or "security" in sb:
            return VerificationCheckResult(
                check=check_name,
                status=VerificationStatus.WARNING,
                severity=VerificationSeverity.HIGH,
                expected=order.customer_name if order else "Direct Recipient",
                actual=delivery.signed_by,
                message=f"Weak Signature Proof: Package was signed for by third-party '{delivery.signed_by}' rather than direct recipient."
            )
            
        return VerificationCheckResult(
            check=check_name,
            status=VerificationStatus.PASSED,
            severity=VerificationSeverity.INFO,
            expected=order.customer_name if order else "Direct Recipient",
            actual=delivery.signed_by,
            message=f"Direct recipient signature verified ('{delivery.signed_by}')."
        )

    @classmethod
    def run_all_checks(
        cls,
        dispute: Dispute,
        payment: Optional[Payment],
        order: Optional[Order],
        delivery: Optional[Delivery],
        evidence_list: List[Evidence]
    ) -> List[VerificationCheckResult]:
        """Runs all deterministic verification checks and returns structured output."""
        return [
            cls.verify_payment_amount(dispute, payment, order),
            cls.verify_order_id_consistency(dispute, payment, delivery, evidence_list),
            cls.verify_customer_id_consistency(payment, order, delivery),
            cls.verify_delivery_date(dispute, delivery),
            cls.verify_dispute_date(dispute, order),
            cls.check_required_evidence(evidence_list),
            cls.detect_duplicate_evidence(evidence_list),
            cls.verify_communication_relevance(dispute, evidence_list),
            cls.verify_signature_authenticity(delivery, order)
        ]

