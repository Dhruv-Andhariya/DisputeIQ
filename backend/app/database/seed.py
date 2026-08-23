import json
import os
from app.database.db import (
    init_db, save_dispute, save_payment, save_order, save_delivery, save_evidence, save_audit_event
)
from app.models.domain import Dispute, Payment, Order, Delivery, Evidence, AuditEvent
from data.synthetic.generator import generate_synthetic_dataset

def seed_database():
    print("Initializing database tables...")
    init_db()
    
    dataset_path = os.path.join("data", "synthetic", "dataset.json")
    if not os.path.exists(dataset_path):
        print("Synthetic dataset not found. Generating now...")
        generate_synthetic_dataset()
        
    with open(dataset_path, "r") as f:
        dataset = json.load(f)
        
    print(f"Seeding {len(dataset)} dispute cases into SQLite database...")
    
    for case in dataset:
        dispute = Dispute(**case["dispute"])
        payment = Payment(**case["payment"])
        order = Order(**case["order"])
        delivery = Delivery(**case["delivery"])
        
        save_dispute(dispute)
        save_payment(payment)
        save_order(order)
        save_delivery(delivery)
        
        for ev_data in case["evidence"]:
            evidence = Evidence(**ev_data)
            save_evidence(evidence)
            
        # Initial Audit Event
        audit = AuditEvent(
            event_id=f"AUD-{dispute.dispute_id}-INIT",
            dispute_id=dispute.dispute_id,
            event_type="DISPUTE_RECEIVED",
            description=f"Dispute received from payment infrastructure for amount ₹{dispute.amount}.",
            metadata={
                "merchant_id": dispute.merchant_id,
                "reason": dispute.reason,
                "case_type": dispute.case_type
            },
            timestamp=dispute.created_at
        )
        save_audit_event(audit)
        
    print("Database seeding completed successfully!")

if __name__ == "__main__":
    seed_database()
