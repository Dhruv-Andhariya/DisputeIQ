import pytest
from app.models.domain import (
    Dispute, Payment, Order, OrderItem, Delivery, Evidence, EvidenceCategory,
    VerificationStatus, VerificationSeverity, DisputeReason
)
from app.services.verification_engine import VerificationEngine

@pytest.fixture
def base_sample_data():
    dispute = Dispute(
        dispute_id="DSP-TEST-001",
        payment_id="PAY-TEST-001",
        merchant_id="MERCHANT_001",
        amount=4999.0,
        currency="INR",
        reason=DisputeReason.GOODS_SERVICES_NOT_RECEIVED,
        dispute_date="2026-08-10 12:00:00",
        created_at="2026-08-10 12:00:00",
        updated_at="2026-08-10 12:00:00"
    )
    
    payment = Payment(
        payment_id="PAY-TEST-001",
        order_id="ORD-1001",
        customer_id="CUST-8001",
        amount=4999.0,
        currency="INR",
        created_at="2026-08-01 10:00:00"
    )
    
    order = Order(
        order_id="ORD-1001",
        customer_id="CUST-8001",
        items=[OrderItem(item_id="ITM-01", name="Headphones", quantity=1, price=4999.0)],
        total_amount=4999.0,
        currency="INR",
        shipping_address="Mumbai, MH",
        customer_email="test@example.com",
        customer_name="Test Customer",
        created_at="2026-08-01 09:50:00"
    )
    
    delivery = Delivery(
        delivery_id="DEL-7001",
        order_id="ORD-1001",
        carrier="BlueDart",
        tracking_number="BD123456",
        status="DELIVERED",
        estimated_delivery_date="2026-08-04",
        actual_delivery_date="2026-08-04 14:30:00",
        recipient_name="Test Customer",
        signed_by="Test Customer",
        delivery_address="Mumbai, MH",
        created_at="2026-08-02 10:00:00"
    )
    
    evidence_list = [
        Evidence(
            evidence_id="EVD-001",
            dispute_id="DSP-TEST-001",
            category=EvidenceCategory.PROOF_OF_DELIVERY,
            file_name="pod.json",
            content={"order_id": "ORD-1001"},
            created_at="2026-08-04 14:30:00"
        ),
        Evidence(
            evidence_id="EVD-002",
            dispute_id="DSP-TEST-001",
            category=EvidenceCategory.INVOICE,
            file_name="invoice.json",
            content={"order_id": "ORD-1001", "amount": 4999.0},
            created_at="2026-08-01 10:05:00"
        ),
        Evidence(
            evidence_id="EVD-003",
            dispute_id="DSP-TEST-001",
            category=EvidenceCategory.ORDER_CONFIRMATION,
            file_name="order_conf.json",
            content={"order_id": "ORD-1001"},
            created_at="2026-08-01 09:55:00"
        )
    ]
    
    return dispute, payment, order, delivery, evidence_list


def test_verification_all_pass(base_sample_data):
    dispute, payment, order, delivery, evidence_list = base_sample_data
    results = VerificationEngine.run_all_checks(dispute, payment, order, delivery, evidence_list)
    
    for check in results:
        assert check.status == VerificationStatus.PASSED, f"Check {check.check} failed: {check.message}"


def test_order_id_mismatch_detection(base_sample_data):
    """CRITICAL TEST: Detects ORD1001 vs ORD1002 mismatch."""
    dispute, payment, order, delivery, evidence_list = base_sample_data
    
    # Corrupt delivery to reference ORD-1002 instead of ORD-1001
    delivery_mismatched = Delivery(
        delivery_id="DEL-7001",
        order_id="ORD-1002",  # MISMATCH!
        carrier="BlueDart",
        tracking_number="BD123456",
        status="DELIVERED",
        estimated_delivery_date="2026-08-04",
        actual_delivery_date="2026-08-04 14:30:00",
        recipient_name="Test Customer",
        signed_by="Test Customer",
        delivery_address="Mumbai, MH",
        created_at="2026-08-02 10:00:00"
    )
    
    check_result = VerificationEngine.verify_order_id_consistency(dispute, payment, delivery_mismatched, evidence_list)
    
    assert check_result.status == VerificationStatus.FAILED
    assert check_result.severity == VerificationSeverity.HIGH
    assert check_result.expected == "ORD-1001"
    assert check_result.actual == "ORD-1002"
    assert "Order Identity Conflict" in check_result.message


def test_payment_amount_mismatch(base_sample_data):
    dispute, payment, order, delivery, evidence_list = base_sample_data
    
    dispute_mismatched = dispute.model_copy(update={"amount": 5999.0})
    
    check_result = VerificationEngine.verify_payment_amount(dispute_mismatched, payment, order)
    assert check_result.status == VerificationStatus.FAILED
    assert check_result.severity == VerificationSeverity.HIGH
    assert check_result.actual == "₹5999.0"


def test_delivery_after_dispute_date(base_sample_data):
    dispute, payment, order, delivery, evidence_list = base_sample_data
    
    # Dispute on Aug 5, but actual delivery completed on Aug 10
    dispute_early = dispute.model_copy(update={"dispute_date": "2026-08-05 12:00:00"})
    delivery_late = delivery.model_copy(update={"actual_delivery_date": "2026-08-10 14:30:00"})
    
    check_result = VerificationEngine.verify_delivery_date(dispute_early, delivery_late)
    assert check_result.status == VerificationStatus.FAILED
    assert check_result.severity == VerificationSeverity.HIGH
    assert "Chronological Anomaly" in check_result.message


def test_missing_required_evidence(base_sample_data):
    dispute, payment, order, delivery, evidence_list = base_sample_data
    
    # Remove Proof of Delivery
    evidence_missing = [ev for ev in evidence_list if ev.category != EvidenceCategory.PROOF_OF_DELIVERY]
    
    check_result = VerificationEngine.check_required_evidence(evidence_missing)
    assert check_result.status == VerificationStatus.FAILED
    assert check_result.severity == VerificationSeverity.HIGH
    assert "PROOF_OF_DELIVERY" in check_result.message
