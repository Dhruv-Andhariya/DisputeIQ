from typing import Dict, Any, List
import time

class MockRazorpayAdapter:
    """
    MOCK RAZORPAY ADAPTER
    Simulates integration with Razorpay Dispute and Payment APIs.
    """
    
    @staticmethod
    def get_dispute(dispute_id: str) -> Dict[str, Any]:
        """Fetches dispute record from mock Razorpay payment infrastructure."""
        return {
            "dispute_id": dispute_id,
            "status": "under_review",
            "phase": "chargeback",
            "gateway": "Razorpay Payment Gateway",
            "currency": "INR"
        }

    @staticmethod
    def get_payment(payment_id: str) -> Dict[str, Any]:
        """Fetches payment record from mock Razorpay payment infrastructure."""
        return {
            "payment_id": payment_id,
            "status": "captured",
            "gateway": "Razorpay"
        }

    @staticmethod
    def upload_evidence(dispute_id: str, evidence_files: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Simulates uploading evidence documents to Razorpay dispute portal."""
        return {
            "dispute_id": dispute_id,
            "uploaded_count": len(evidence_files),
            "status": "SUCCESS",
            "message": f"Successfully uploaded {len(evidence_files)} evidence files to Razorpay dispute system."
        }

    @staticmethod
    def prepare_contest(dispute_id: str, evidence_summary: Dict[str, Any]) -> Dict[str, Any]:
        """Simulates preparing contest submission payload."""
        return {
            "dispute_id": dispute_id,
            "action": "PREPARE_CONTEST",
            "payload_ready": True,
            "evidence_count": len(evidence_summary.get("supporting_evidence", []))
        }

    @staticmethod
    def submit_contest(dispute_id: str, submission_data: Dict[str, Any]) -> Dict[str, Any]:
        """Simulates submitting contest claim to Razorpay / Card Network."""
        return {
            "dispute_id": dispute_id,
            "status": "CONTESTED",
            "acknowledgment_id": f"ACK-RZP-{dispute_id}",
            "submitted_at": time.strftime("%Y-%m-%d %H:%M:%S"),
            "message": "Dispute contest successfully submitted to issuing bank via Razorpay adapter."
        }
