import json
import random
import os
from datetime import datetime, timedelta

def generate_synthetic_dataset(seed: int = 42, count: int = 35):
    random.seed(seed)
    
    case_types = [
        "STRONG_CASE",
        "WEAK_CASE",
        "CONTRADICTORY_CASE",
        "MISSING_EVIDENCE_CASE",
        "EDGE_CASE"
    ]
    
    # Distribution of cases:
    # 12 Strong, 8 Weak, 10 Contradictory, 5 Missing Evidence, 5 Edge cases = 40 total
    case_distribution = (
        ["STRONG_CASE"] * 12 +
        ["WEAK_CASE"] * 8 +
        ["CONTRADICTORY_CASE"] * 10 +
        ["MISSING_EVIDENCE_CASE"] * 5 +
        ["EDGE_CASE"] * 5
    )
    
    first_names = ["Aarav", "Ananya", "Rohan", "Priya", "Vikram", "Sneha", "Kabir", "Diya", "Aditya", "Ishaan", "Meera", "Siddharth", "Neha", "Rahul", "Kavya"]
    last_names = ["Sharma", "Verma", "Patel", "Mehta", "Iyer", "Nair", "Gupta", "Singh", "Reddy", "Deshmukh", "Joshi", "Chopra", "Kulkarni", "Sen", "Bhat"]
    cities = ["Mumbai, MH", "Bengaluru, KA", "Delhi, DL", "Hyderabad, TS", "Chennai, TN", "Pune, MH", "Kolkata, WB", "Ahmedabad, GJ"]
    carriers = ["BlueDart Express", "Delhivery", "DTDC Courier", "Ekart Logistics", "Shadowfax"]
    products = [
        ("Wireless Noise-Canceling Headphones", 4999.0),
        ("Ergonomic Mechanical Keyboard", 3499.0),
        ("Ultra HD Smart Watch", 6299.0),
        ("Leather Executive Laptop Bag", 2899.0),
        ("Portable Bluetooth Speaker", 1999.0),
        ("High-Speed Gaming Mouse", 1499.0)
    ]
    
    dataset = []
    
    base_date = datetime(2026, 7, 1, 10, 0, 0)
    
    for i in range(len(case_distribution)):
        case_type = case_distribution[i]
        idx = i + 1
        
        dispute_id = f"DSP-2026-{idx:03d}"
        order_id = f"ORD-100{idx}"
        payment_id = f"PAY-500{idx}"
        customer_id = f"CUST-800{idx}"
        merchant_id = "MERCHANT_RAZORPAY_DEMO"
        
        prod_name, prod_price = random.choice(products)
        amount = prod_price
        
        fname = random.choice(first_names)
        lname = random.choice(last_names)
        cust_name = f"{fname} {lname}"
        cust_email = f"{fname.lower()}.{lname.lower()}@example.com"
        city = random.choice(cities)
        shipping_addr = f"Flat {random.randint(101, 909)}, Block B, Apex Heights, {city} - 400001"
        
        # Timestamps
        order_time = base_date + timedelta(days=idx, hours=random.randint(1, 5))
        payment_time = order_time + timedelta(minutes=random.randint(5, 30))
        invoice_time = payment_time + timedelta(minutes=random.randint(10, 60))
        shipment_time = order_time + timedelta(days=1, hours=random.randint(2, 6))
        
        # Default delivery: 3 days after shipment
        est_delivery = (shipment_time + timedelta(days=3)).strftime("%Y-%m-%d")
        act_delivery = (shipment_time + timedelta(days=3, hours=random.randint(2, 8))).strftime("%Y-%m-%d %H:%M:%S")
        dispute_time = (shipment_time + timedelta(days=7, hours=random.randint(1, 12))).strftime("%Y-%m-%d %H:%M:%S")
        
        # Delivery & Dispute specifics based on case_type
        delivery_status = "DELIVERED"
        signed_by = cust_name
        delivery_order_id = order_id
        delivery_customer_id = customer_id
        delivery_amount = amount
        dispute_amount = amount
        
        carrier = random.choice(carriers)
        tracking = f"{carrier[:3].upper()}{random.randint(10000000, 99999999)}"
        
        cust_comm = f"Hi, I received the order {order_id} on time. Everything works fine."
        
        # Corruption & specific behaviors
        if case_type == "STRONG_CASE":
            cust_comm = f"Hello support, just checking on my invoice for order {order_id}. I received the headphones safely."
        
        elif case_type == "WEAK_CASE":
            # Missing signed receipt or tracking shows delivered to receptionist
            signed_by = "Front Desk / Guard"
            cust_comm = f"I cannot find my parcel for {order_id}. Security guard says they didn't take it."
            
        elif case_type == "CONTRADICTORY_CASE":
            contra_subtype = idx % 4
            if contra_subtype == 0:
                # Order ID Mismatch: Delivery document references ORD-9999 instead of order_id!
                delivery_order_id = f"ORD-ERR-{idx:03d}"
                cust_comm = f"Disputing order {order_id} because delivery receipt belongs to a different order {delivery_order_id}."
            elif contra_subtype == 1:
                # Payment Amount Mismatch: Dispute for 4999, but payment was 3999
                dispute_amount = amount + 1000.0
                cust_comm = f"I was charged incorrect dispute amount {dispute_amount} vs order amount {amount}."
            elif contra_subtype == 2:
                # Delivery AFTER dispute date
                dispute_dt = (shipment_time + timedelta(days=1)).strftime("%Y-%m-%d %H:%M:%S")
                act_dt = (shipment_time + timedelta(days=5)).strftime("%Y-%m-%d %H:%M:%S")
                dispute_time = dispute_dt
                act_delivery = act_dt
                cust_comm = f"Filed dispute on {dispute_time} because delivery had not arrived yet."
            else:
                # Customer ID conflict
                delivery_customer_id = f"CUST-OTHER-{idx}"
                cust_comm = f"Delivery address belongs to customer {delivery_customer_id} instead of {customer_id}."

        elif case_type == "MISSING_EVIDENCE_CASE":
            # Missing delivery record or missing invoice
            delivery_status = "IN_TRANSIT"
            act_delivery = None
            signed_by = None
            cust_comm = f"Where is my package for {order_id}? Tracking has stopped updating."

        elif case_type == "EDGE_CASE":
            # Wrong category (Customer says product was damaged/broken, but dispute reason is Goods Not Received)
            cust_comm = f"The item received for {order_id} was completely shattered during transit. Demanding full refund."
        
        # Payment record
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
        
        # Order record
        order_record = {
            "order_id": order_id,
            "customer_id": customer_id,
            "items": [
                {"item_id": f"ITM-{idx:03d}", "name": prod_name, "quantity": 1, "price": prod_price}
            ],
            "total_amount": amount,
            "currency": "INR",
            "shipping_address": shipping_addr,
            "customer_email": cust_email,
            "customer_name": cust_name,
            "created_at": order_time.strftime("%Y-%m-%d %H:%M:%S")
        }
        
        # Delivery record
        delivery_record = {
            "delivery_id": f"DEL-700{idx}",
            "order_id": delivery_order_id,
            "carrier": carrier,
            "tracking_number": tracking,
            "status": delivery_status,
            "estimated_delivery_date": est_delivery,
            "actual_delivery_date": act_delivery,
            "recipient_name": cust_name,
            "signed_by": signed_by,
            "delivery_address": shipping_addr,
            "created_at": shipment_time.strftime("%Y-%m-%d %H:%M:%S")
        }
        
        # Dispute record
        dispute_record = {
            "dispute_id": dispute_id,
            "payment_id": payment_id,
            "merchant_id": merchant_id,
            "amount": dispute_amount,
            "currency": "INR",
            "reason": "Goods / Services Not Received",
            "status": "OPEN",
            "dispute_date": dispute_time,
            "case_type": case_type,
            "created_at": dispute_time,
            "updated_at": dispute_time
        }
        
        # Evidence items
        evidence_items = []
        
        # 1. Invoice
        evidence_items.append({
            "evidence_id": f"EVD-{idx:03d}-INV",
            "dispute_id": dispute_id,
            "category": "INVOICE",
            "file_name": f"invoice_{order_id}.json",
            "file_type": "application/json",
            "content": {
                "invoice_number": f"INV-2026-{idx:03d}",
                "order_id": order_id,
                "customer_id": customer_id,
                "amount": amount,
                "tax_amount": round(amount * 0.18, 2),
                "date": invoice_time.strftime("%Y-%m-%d %H:%M:%S"),
                "status": "PAID"
            },
            "verification_status": "FOUND",
            "created_at": invoice_time.strftime("%Y-%m-%d %H:%M:%S")
        })
        
        # 2. Order Confirmation
        evidence_items.append({
            "evidence_id": f"EVD-{idx:03d}-ORD",
            "dispute_id": dispute_id,
            "category": "ORDER_CONFIRMATION",
            "file_name": f"order_confirmation_{order_id}.json",
            "file_type": "application/json",
            "content": {
                "order_id": order_id,
                "customer_name": cust_name,
                "email": cust_email,
                "amount": amount,
                "date": order_time.strftime("%Y-%m-%d %H:%M:%S")
            },
            "verification_status": "FOUND",
            "created_at": order_time.strftime("%Y-%m-%d %H:%M:%S")
        })
        
        # 3. Proof of Delivery (unless MISSING_EVIDENCE_CASE)
        if case_type != "MISSING_EVIDENCE_CASE":
            evidence_items.append({
                "evidence_id": f"EVD-{idx:03d}-POD",
                "dispute_id": dispute_id,
                "category": "PROOF_OF_DELIVERY",
                "file_name": f"proof_of_delivery_{delivery_record['delivery_id']}.json",
                "file_type": "application/json",
                "content": delivery_record,
                "verification_status": "FOUND",
                "created_at": shipment_time.strftime("%Y-%m-%d %H:%M:%S")
            })
            
        # 4. Customer Communication
        evidence_items.append({
            "evidence_id": f"EVD-{idx:03d}-COMM",
            "dispute_id": dispute_id,
            "category": "CUSTOMER_COMMUNICATION",
            "file_name": f"chat_log_{customer_id}.json",
            "file_type": "application/json",
            "content": {
                "customer_id": customer_id,
                "messages": [
                    {
                        "timestamp": (order_time + timedelta(hours=2)).strftime("%Y-%m-%d %H:%M:%S"),
                        "sender": "CUSTOMER",
                        "text": f"Hi, I'm checking status for order {order_id}."
                    },
                    {
                        "timestamp": (shipment_time + timedelta(hours=1)).strftime("%Y-%m-%d %H:%M:%S"),
                        "sender": "SUPPORT",
                        "text": f"Your order has shipped with tracking number {tracking} via {carrier}."
                    },
                    {
                        "timestamp": (shipment_time + timedelta(days=4)).strftime("%Y-%m-%d %H:%M:%S"),
                        "sender": "CUSTOMER",
                        "text": cust_comm
                    }
                ]
            },
            "verification_status": "FOUND",
            "created_at": (shipment_time + timedelta(days=4)).strftime("%Y-%m-%d %H:%M:%S")
        })
        
        # 5. Terms & Conditions
        evidence_items.append({
            "evidence_id": f"EVD-{idx:03d}-TNC",
            "dispute_id": dispute_id,
            "category": "TERMS_AND_CONDITIONS",
            "file_name": "merchant_terms_v2.json",
            "file_type": "application/json",
            "content": {
                "version": "2.1",
                "refund_policy": "Non-received goods must be reported within 14 days of estimated delivery.",
                "delivery_policy": "Signature at delivery location constitutes completed fulfillment."
            },
            "verification_status": "FOUND",
            "created_at": order_time.strftime("%Y-%m-%d %H:%M:%S")
        })
        
        dataset.append({
            "dispute": dispute_record,
            "payment": payment_record,
            "order": order_record,
            "delivery": delivery_record,
            "evidence": evidence_items
        })

    out_dir = os.path.join("data", "synthetic")
    os.makedirs(out_dir, exist_ok=True)
    out_file = os.path.join(out_dir, "dataset.json")
    with open(out_file, "w") as f:
        json.dump(dataset, f, indent=2)
        
    print(f"Successfully generated {len(dataset)} synthetic dispute cases in {out_file}")
    return dataset

if __name__ == "__main__":
    generate_synthetic_dataset()
