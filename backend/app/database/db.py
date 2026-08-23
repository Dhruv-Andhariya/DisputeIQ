import sqlite3
import json
import os
from typing import List, Optional, Dict, Any
from app.core.config import settings
from app.models.domain import (
    Dispute, Payment, Order, Delivery, Evidence, Investigation, AuditEvent,
    DisputeStatus
)

DB_PATH = settings.DATABASE_URL.replace("sqlite:///", "")

def get_db_connection():
    os.makedirs(os.path.dirname(os.path.abspath(DB_PATH)), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()

    # Disputes Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS disputes (
        dispute_id TEXT PRIMARY KEY,
        payment_id TEXT NOT NULL,
        merchant_id TEXT NOT NULL,
        amount REAL NOT NULL,
        currency TEXT NOT NULL,
        reason TEXT NOT NULL,
        status TEXT NOT NULL,
        dispute_date TEXT NOT NULL,
        case_type TEXT NOT NULL,
        created_at TEXT NOT NULL,
        updated_at TEXT NOT NULL
    )
    """)

    # Payments Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS payments (
        payment_id TEXT PRIMARY KEY,
        order_id TEXT NOT NULL,
        customer_id TEXT NOT NULL,
        amount REAL NOT NULL,
        currency TEXT NOT NULL,
        status TEXT NOT NULL,
        method TEXT NOT NULL,
        created_at TEXT NOT NULL
    )
    """)

    # Orders Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS orders (
        order_id TEXT PRIMARY KEY,
        customer_id TEXT NOT NULL,
        items TEXT NOT NULL,
        total_amount REAL NOT NULL,
        currency TEXT NOT NULL,
        shipping_address TEXT NOT NULL,
        customer_email TEXT NOT NULL,
        customer_name TEXT NOT NULL,
        created_at TEXT NOT NULL
    )
    """)

    # Deliveries Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS deliveries (
        delivery_id TEXT PRIMARY KEY,
        order_id TEXT NOT NULL,
        carrier TEXT NOT NULL,
        tracking_number TEXT NOT NULL,
        status TEXT NOT NULL,
        estimated_delivery_date TEXT NOT NULL,
        actual_delivery_date TEXT,
        recipient_name TEXT,
        signed_by TEXT,
        delivery_address TEXT NOT NULL,
        created_at TEXT NOT NULL
    )
    """)

    # Evidence Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS evidence (
        evidence_id TEXT PRIMARY KEY,
        dispute_id TEXT NOT NULL,
        category TEXT NOT NULL,
        file_name TEXT NOT NULL,
        file_type TEXT NOT NULL,
        content TEXT NOT NULL,
        verification_status TEXT NOT NULL,
        created_at TEXT NOT NULL
    )
    """)

    # Investigations Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS investigations (
        investigation_id TEXT PRIMARY KEY,
        dispute_id TEXT NOT NULL,
        verification_results TEXT NOT NULL,
        readiness_score TEXT NOT NULL,
        timeline TEXT NOT NULL,
        ai_analysis TEXT,
        decision TEXT NOT NULL,
        status TEXT NOT NULL,
        created_at TEXT NOT NULL
    )
    """)

    # Audit Events Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS audit_events (
        event_id TEXT PRIMARY KEY,
        dispute_id TEXT NOT NULL,
        event_type TEXT NOT NULL,
        description TEXT NOT NULL,
        metadata TEXT NOT NULL,
        timestamp TEXT NOT NULL
    )
    """)

    conn.commit()
    conn.close()


# Database Access Functions

def save_dispute(dispute: Dispute):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
    INSERT OR REPLACE INTO disputes 
    (dispute_id, payment_id, merchant_id, amount, currency, reason, status, dispute_date, case_type, created_at, updated_at)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        dispute.dispute_id, dispute.payment_id, dispute.merchant_id, dispute.amount,
        dispute.currency, dispute.reason, dispute.status, dispute.dispute_date,
        dispute.case_type, dispute.created_at, dispute.updated_at
    ))
    conn.commit()
    conn.close()

def get_dispute_by_id(dispute_id: str) -> Optional[Dispute]:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM disputes WHERE dispute_id = ?", (dispute_id,))
    row = cursor.fetchone()
    conn.close()
    if row:
        return Dispute(**dict(row))
    return None

def get_all_disputes() -> List[Dispute]:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM disputes ORDER BY created_at DESC")
    rows = cursor.fetchall()
    conn.close()
    return [Dispute(**dict(r)) for r in rows]

def save_payment(payment: Payment):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
    INSERT OR REPLACE INTO payments 
    (payment_id, order_id, customer_id, amount, currency, status, method, created_at)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        payment.payment_id, payment.order_id, payment.customer_id, payment.amount,
        payment.currency, payment.status, payment.method, payment.created_at
    ))
    conn.commit()
    conn.close()

def get_payment_by_id(payment_id: str) -> Optional[Payment]:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM payments WHERE payment_id = ?", (payment_id,))
    row = cursor.fetchone()
    conn.close()
    if row:
        return Payment(**dict(row))
    return None

def save_order(order: Order):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
    INSERT OR REPLACE INTO orders 
    (order_id, customer_id, items, total_amount, currency, shipping_address, customer_email, customer_name, created_at)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        order.order_id, order.customer_id, json.dumps([item.model_dump() for item in order.items]),
        order.total_amount, order.currency, order.shipping_address,
        order.customer_email, order.customer_name, order.created_at
    ))
    conn.commit()
    conn.close()

def get_order_by_id(order_id: str) -> Optional[Order]:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM orders WHERE order_id = ?", (order_id,))
    row = cursor.fetchone()
    conn.close()
    if row:
        data = dict(row)
        data['items'] = json.loads(data['items'])
        return Order(**data)
    return None

def save_delivery(delivery: Delivery):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
    INSERT OR REPLACE INTO deliveries 
    (delivery_id, order_id, carrier, tracking_number, status, estimated_delivery_date, actual_delivery_date, recipient_name, signed_by, delivery_address, created_at)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        delivery.delivery_id, delivery.order_id, delivery.carrier, delivery.tracking_number,
        delivery.status, delivery.estimated_delivery_date, delivery.actual_delivery_date,
        delivery.recipient_name, delivery.signed_by, delivery.delivery_address, delivery.created_at
    ))
    conn.commit()
    conn.close()

def get_delivery_by_order_id(order_id: str) -> Optional[Delivery]:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM deliveries WHERE order_id = ?", (order_id,))
    row = cursor.fetchone()
    conn.close()
    if row:
        return Delivery(**dict(row))
    return None

def save_evidence(evidence: Evidence):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
    INSERT OR REPLACE INTO evidence 
    (evidence_id, dispute_id, category, file_name, file_type, content, verification_status, created_at)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        evidence.evidence_id, evidence.dispute_id, evidence.category, evidence.file_name,
        evidence.file_type, json.dumps(evidence.content), evidence.verification_status, evidence.created_at
    ))
    conn.commit()
    conn.close()

def get_evidence_by_dispute_id(dispute_id: str) -> List[Evidence]:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM evidence WHERE dispute_id = ?", (dispute_id,))
    rows = cursor.fetchall()
    conn.close()
    results = []
    for r in rows:
        d = dict(r)
        d['content'] = json.loads(d['content'])
        results.append(Evidence(**d))
    return results

def save_investigation(investigation: Investigation):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
    INSERT OR REPLACE INTO investigations 
    (investigation_id, dispute_id, verification_results, readiness_score, timeline, ai_analysis, decision, status, created_at)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        investigation.investigation_id, investigation.dispute_id,
        json.dumps([v.model_dump() for v in investigation.verification_results]),
        json.dumps(investigation.readiness_score.model_dump()),
        json.dumps([t.model_dump() for t in investigation.timeline]),
        json.dumps(investigation.ai_analysis.model_dump()) if investigation.ai_analysis else None,
        json.dumps(investigation.decision.model_dump()),
        investigation.status, investigation.created_at
    ))
    conn.commit()
    conn.close()

def get_investigation_by_dispute_id(dispute_id: str) -> Optional[Investigation]:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM investigations WHERE dispute_id = ? ORDER BY created_at DESC LIMIT 1", (dispute_id,))
    row = cursor.fetchone()
    conn.close()
    if row:
        d = dict(row)
        d['verification_results'] = json.loads(d['verification_results'])
        d['readiness_score'] = json.loads(d['readiness_score'])
        d['timeline'] = json.loads(d['timeline'])
        d['ai_analysis'] = json.loads(d['ai_analysis']) if d['ai_analysis'] else None
        d['decision'] = json.loads(d['decision'])
        return Investigation(**d)
    return None

def save_audit_event(event: AuditEvent):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
    INSERT OR REPLACE INTO audit_events 
    (event_id, dispute_id, event_type, description, metadata, timestamp)
    VALUES (?, ?, ?, ?, ?, ?)
    """, (
        event.event_id, event.dispute_id, event.event_type, event.description,
        json.dumps(event.metadata), event.timestamp
    ))
    conn.commit()
    conn.close()

def get_audit_events_by_dispute_id(dispute_id: str) -> List[AuditEvent]:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM audit_events WHERE dispute_id = ? ORDER BY timestamp ASC", (dispute_id,))
    rows = cursor.fetchall()
    conn.close()
    results = []
    for r in rows:
        d = dict(r)
        d['metadata'] = json.loads(d['metadata'])
        results.append(AuditEvent(**d))
    return results
