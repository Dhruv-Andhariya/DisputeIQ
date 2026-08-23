from typing import List, Optional
from datetime import datetime
from app.models.domain import (
    Dispute, Payment, Order, Delivery, Evidence, EvidenceCategory,
    TimelineEvent, EvidenceState, VerificationCheckResult, VerificationStatus
)

class TimelineBuilderService:
    @staticmethod
    def build_timeline(
        dispute: Dispute,
        payment: Optional[Payment],
        order: Optional[Order],
        delivery: Optional[Delivery],
        evidence_list: List[Evidence],
        verification_results: List[VerificationCheckResult]
    ) -> List[TimelineEvent]:
        """
        Reconstructs the chronological event stream exclusively from available verified DB records.
        AI MUST NEVER fabricate timeline events.
        """
        events: List[TimelineEvent] = []
        
        # Check verification state for delivery and order conflicts
        order_conflict = any(r.check == "order_id_consistency" and r.status == VerificationStatus.FAILED for r in verification_results)
        delivery_failed = any(r.check == "delivery_date_validity" and r.status == VerificationStatus.FAILED for r in verification_results)
        
        # 1. Order Event
        if order:
            events.append(TimelineEvent(
                event_id=f"EVT-{order.order_id}-ORD",
                timestamp=order.created_at,
                event_type="ORDER_PLACED",
                source="E-Commerce Storefront",
                description=f"Order {order.order_id} placed by {order.customer_name} ({order.customer_email}) for ₹{order.total_amount}.",
                verification_state=EvidenceState.VERIFIED,
                metadata={"order_id": order.order_id, "amount": order.total_amount}
            ))
            
        # 2. Payment Event
        if payment:
            events.append(TimelineEvent(
                event_id=f"EVT-{payment.payment_id}-PAY",
                timestamp=payment.created_at,
                event_type="PAYMENT_CAPTURED",
                source="Razorpay Gateway",
                description=f"Payment {payment.payment_id} of ₹{payment.amount} successfully captured via {payment.method}.",
                verification_state=EvidenceState.VERIFIED,
                metadata={"payment_id": payment.payment_id, "method": payment.method}
            ))
            
        # 3. Invoice Event
        invoice_ev = next((ev for ev in evidence_list if ev.category == EvidenceCategory.INVOICE), None)
        if invoice_ev:
            inv_content = invoice_ev.content
            events.append(TimelineEvent(
                event_id=f"EVT-{invoice_ev.evidence_id}-INV",
                timestamp=invoice_ev.created_at,
                event_type="INVOICE_GENERATED",
                source="Billing Engine",
                description=f"Tax invoice {inv_content.get('invoice_number', 'N/A')} issued for order {inv_content.get('order_id', 'N/A')}.",
                verification_state=EvidenceState.CONTRADICTED if order_conflict else EvidenceState.VERIFIED,
                metadata=inv_content
            ))
            
        # 4. Shipment & Delivery Events
        if delivery:
            events.append(TimelineEvent(
                event_id=f"EVT-{delivery.delivery_id}-SHIP",
                timestamp=delivery.created_at,
                event_type="SHIPMENT_DISPATCHED",
                source=f"Logistics ({delivery.carrier})",
                description=f"Package dispatched via {delivery.carrier} (Tracking: {delivery.tracking_number}).",
                verification_state=EvidenceState.VERIFIED,
                metadata={"carrier": delivery.carrier, "tracking_number": delivery.tracking_number}
            ))
            
            if delivery.actual_delivery_date and delivery.status == "DELIVERED":
                v_state = EvidenceState.CONTRADICTED if (order_conflict or delivery_failed) else EvidenceState.VERIFIED
                sign_str = f" (Signed by: {delivery.signed_by})" if delivery.signed_by else ""
                events.append(TimelineEvent(
                    event_id=f"EVT-{delivery.delivery_id}-DEL",
                    timestamp=delivery.actual_delivery_date,
                    event_type="DELIVERY_COMPLETED",
                    source=f"Carrier API ({delivery.carrier})",
                    description=f"Package delivered to {delivery.delivery_address}{sign_str}.",
                    verification_state=v_state,
                    metadata={
                        "carrier": delivery.carrier,
                        "recipient": delivery.recipient_name,
                        "signed_by": delivery.signed_by,
                        "address": delivery.delivery_address
                    }
                ))
            elif delivery.status != "DELIVERED":
                events.append(TimelineEvent(
                    event_id=f"EVT-{delivery.delivery_id}-DEL-PEND",
                    timestamp=delivery.estimated_delivery_date,
                    event_type="DELIVERY_PENDING",
                    source=f"Carrier API ({delivery.carrier})",
                    description=f"Delivery pending/in-transit (Status: {delivery.status}, Est: {delivery.estimated_delivery_date}).",
                    verification_state=EvidenceState.PARTIALLY_VERIFIED,
                    metadata={"status": delivery.status}
                ))
                
        # 5. Customer Communication Event
        comm_ev = next((ev for ev in evidence_list if ev.category == EvidenceCategory.CUSTOMER_COMMUNICATION), None)
        if comm_ev and isinstance(comm_ev.content, dict) and "messages" in comm_ev.content:
            msgs = comm_ev.content["messages"]
            for idx, msg in enumerate(msgs):
                events.append(TimelineEvent(
                    event_id=f"EVT-{comm_ev.evidence_id}-MSG-{idx}",
                    timestamp=msg.get("timestamp", comm_ev.created_at),
                    event_type="CUSTOMER_COMMUNICATION",
                    source=f"Support Portal ({msg.get('sender', 'USER')})",
                    description=f"[{msg.get('sender', 'USER')}]: {msg.get('text', '')}",
                    verification_state=EvidenceState.VERIFIED,
                    metadata={"sender": msg.get("sender"), "text": msg.get("text")}
                ))
                
        # 6. Dispute Event
        events.append(TimelineEvent(
            event_id=f"EVT-{dispute.dispute_id}-DISP",
            timestamp=dispute.dispute_date,
            event_type="DISPUTE_FILED",
            source="Issuing Bank / Razorpay",
            description=f"Chargeback dispute raised for ₹{dispute.amount} under reason '{dispute.reason}'.",
            verification_state=EvidenceState.VERIFIED,
            metadata={"reason": dispute.reason, "amount": dispute.amount}
        ))
        
        # Sort events strictly by timestamp ascending
        def parse_ts(ts: str):
            try:
                return datetime.strptime(ts, "%Y-%m-%d %H:%M:%S")
            except Exception:
                try:
                    return datetime.strptime(ts, "%Y-%m-%d")
                except Exception:
                    return datetime.min

        events.sort(key=lambda x: parse_ts(x.timestamp))
        return events
