import json
import random
import os
from datetime import datetime, timedelta

def generate_evaluation_dataset(seed: int = 999, count: int = 25):
    """Generates a held-out dataset specifically for system evaluation."""
    random.seed(seed)
    
    case_distribution = (
        ["STRONG_CASE"] * 7 +
        ["WEAK_CASE"] * 5 +
        ["CONTRADICTORY_CASE"] * 7 +
        ["MISSING_EVIDENCE_CASE"] * 3 +
        ["EDGE_CASE"] * 3
    )
    
    first_names = ["Anish", "Bhavna", "Chirag", "Divya", "Esha", "Farhan", "Gaurav", "Harini"]
    last_names = ["Kapoor", "Joshi", "Chawla", "Trivedi", "Sinha", "Saxena", "Roy", "Dutta"]
    
    dataset = []
    base_date = datetime(2026, 8, 1, 10, 0, 0)
    
    for i in range(len(case_distribution)):
        case_type = case_distribution[i]
        idx = i + 101
        
        dispute_id = f"DSP-EVAL-{idx:03d}"
        order_id = f"ORD-EVAL-{idx}"
        payment_id = f"PAY-EVAL-{idx}"
        customer_id = f"CUST-EVAL-{idx}"
        
        amount = random.choice([1999.0, 3499.0, 4999.0, 7999.0])
        fname = random.choice(first_names)
        lname = random.choice(last_names)
        cust_name = f"{fname} {lname}"
        cust_email = f"{fname.lower()}.{lname.lower()}@evaltest.com"
        
        order_time = base_date + timedelta(days=i, hours=2)
        payment_time = order_time + timedelta(minutes=15)
        shipment_time = order_time + timedelta(days=1)
        est_delivery = (shipment_time + timedelta(days=3)).strftime("%Y-%m-%d")
        act_delivery = (shipment_time + timedelta(days=3, hours=4)).strftime("%Y-%m-%d %H:%M:%S")
        dispute_time = (shipment_time + timedelta(days=8)).strftime("%Y-%m-%d %H:%M:%S")
        
        delivery_status = "DELIVERED"
        signed_by = cust_name
        del_order_id = order_id
        dispute_amount = amount
        cust_comm_text = f"Hi, confirming receipt of order {order_id}."
        expected_ground_truth = "CONTEST"
        
        if case_type == "STRONG_CASE":
            expected_ground_truth = "CONTEST"
            cust_comm_text = f"Thank you, order {order_id} received in perfect condition."
            
        elif case_type == "WEAK_CASE":
            expected_ground_truth = "HUMAN_REVIEW"
            signed_by = "Front Desk Guard"
            cust_comm_text = f"I cannot locate my package for order {order_id}. Security guard says he doesn't remember signing."
            
        elif case_type == "CONTRADICTORY_CASE":
            expected_ground_truth = "HUMAN_REVIEW"
            if idx % 3 == 0:
                del_order_id = f"ORD-EVAL-ERR-{idx}"
                cust_comm_text = f"Disputing order {order_id} due to order number mismatch on tracking receipt."
            elif idx % 3 == 1:
                dispute_amount = amount + 500.0
                cust_comm_text = f"Disputing charge for order {order_id} due to price mismatch."
            else:
                dispute_time = (shipment_time + timedelta(hours=12)).strftime("%Y-%m-%d %H:%M:%S")
                act_delivery = (shipment_time + timedelta(days=4)).strftime("%Y-%m-%d %H:%M:%S")
                cust_comm_text = f"Disputed order {order_id} before delivery arrived."
                
        elif case_type == "MISSING_EVIDENCE_CASE":
            expected_ground_truth = "HUMAN_REVIEW"
            delivery_status = "IN_TRANSIT"
            act_delivery = None
            signed_by = None
            cust_comm_text = f"Package for order {order_id} is stuck in transit."
            
        elif case_type == "EDGE_CASE":
            expected_ground_truth = "HUMAN_REVIEW"
            cust_comm_text = f"The product received for order {order_id} was completely shattered and broken inside the packaging!"

        payment_record = {
            "payment_id": payment_id,
            "order_id": order_id,
            "customer_id": customer_id,
            "amount": amount,
            "currency": "INR",
            "status": "captured",
            "method": "card",
            "created_at": payment_time.strftime("%Y-%m-%d %H:%M:%S")
        }
        
        order_record = {
            "order_id": order_id,
            "customer_id": customer_id,
            "items": [{"item_id": f"ITM-{idx}", "name": "Tech Gadget", "quantity": 1, "price": amount}],
            "total_amount": amount,
            "currency": "INR",
            "shipping_address": "Bengaluru, KA",
            "customer_email": cust_email,
            "customer_name": cust_name,
            "created_at": order_time.strftime("%Y-%m-%d %H:%M:%S")
        }
        
        delivery_record = {
            "delivery_id": f"DEL-EVAL-{idx}",
            "order_id": del_order_id,
            "carrier": "BlueDart",
            "tracking_number": f"BD{idx:08d}",
            "status": delivery_status,
            "estimated_delivery_date": est_delivery,
            "actual_delivery_date": act_delivery,
            "recipient_name": cust_name,
            "signed_by": signed_by,
            "delivery_address": "Bengaluru, KA",
            "created_at": shipment_time.strftime("%Y-%m-%d %H:%M:%S")
        }
        
        dispute_record = {
            "dispute_id": dispute_id,
            "payment_id": payment_id,
            "merchant_id": "MERCHANT_EVAL",
            "amount": dispute_amount,
            "currency": "INR",
            "reason": "Goods / Services Not Received",
            "status": "OPEN",
            "dispute_date": dispute_time,
            "case_type": case_type,
            "created_at": dispute_time,
            "updated_at": dispute_time
        }
        
        evidence_items = []
        evidence_items.append({
            "evidence_id": f"EVD-{idx}-INV",
            "dispute_id": dispute_id,
            "category": "INVOICE",
            "file_name": f"invoice_{order_id}.json",
            "file_type": "application/json",
            "content": {"invoice_number": f"INV-{idx}", "order_id": order_id, "amount": amount},
            "verification_status": "FOUND",
            "created_at": payment_time.strftime("%Y-%m-%d %H:%M:%S")
        })
        evidence_items.append({
            "evidence_id": f"EVD-{idx}-ORD",
            "dispute_id": dispute_id,
            "category": "ORDER_CONFIRMATION",
            "file_name": f"order_{order_id}.json",
            "file_type": "application/json",
            "content": {"order_id": order_id, "amount": amount},
            "verification_status": "FOUND",
            "created_at": order_time.strftime("%Y-%m-%d %H:%M:%S")
        })
        
        if case_type != "MISSING_EVIDENCE_CASE":
            evidence_items.append({
                "evidence_id": f"EVD-{idx}-POD",
                "dispute_id": dispute_id,
                "category": "PROOF_OF_DELIVERY",
                "file_name": f"pod_{delivery_record['delivery_id']}.json",
                "file_type": "application/json",
                "content": delivery_record,
                "verification_status": "FOUND",
                "created_at": shipment_time.strftime("%Y-%m-%d %H:%M:%S")
            })

        evidence_items.append({
            "evidence_id": f"EVD-{idx}-COMM",
            "dispute_id": dispute_id,
            "category": "CUSTOMER_COMMUNICATION",
            "file_name": f"chat_{customer_id}.json",
            "file_type": "application/json",
            "content": {
                "customer_id": customer_id,
                "messages": [
                    {
                        "timestamp": (shipment_time + timedelta(days=2)).strftime("%Y-%m-%d %H:%M:%S"),
                        "sender": "CUSTOMER",
                        "text": cust_comm_text
                    }
                ]
            },
            "verification_status": "FOUND",
            "created_at": (shipment_time + timedelta(days=2)).strftime("%Y-%m-%d %H:%M:%S")
        })

        dataset.append({
            "dispute": dispute_record,
            "payment": payment_record,
            "order": order_record,
            "delivery": delivery_record,
            "evidence": evidence_items,
            "ground_truth_decision": expected_ground_truth
        })

    out_dir = os.path.join("evaluation", "test_cases")
    os.makedirs(out_dir, exist_ok=True)
    out_file = os.path.join(out_dir, "test_dataset.json")
    with open(out_file, "w") as f:
        json.dump(dataset, f, indent=2)
    print(f"Generated updated evaluation test set with {len(dataset)} cases in {out_file}")
    return dataset

if __name__ == "__main__":
    generate_evaluation_dataset()
