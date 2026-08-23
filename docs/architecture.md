# DisputeIQ System Architecture & Technical Design

## 1. Overview & System Blueprint
DisputeIQ is designed as a **Modular Monolith** that acts as an intelligent evidence verification and decision layer sitting on top of payment gateways (such as Razorpay).

```
 ┌──────────────────────────────────────────────────────────────────────────┐
 │                           React Frontend (Vite)                          │
 └────────────────────────────────────┬─────────────────────────────────────┘
                                      │ REST API / Axios
 ┌────────────────────────────────────▼─────────────────────────────────────┐
 │                         FastAPI REST API Layer                           │
 └────────────────────────────────────┬─────────────────────────────────────┘
                                      │
 ┌────────────────────────────────────▼─────────────────────────────────────┐
 │                      Dispute Investigation Pipeline                      │
 │                                                                          │
 │  ┌──────────────────────────┐             ┌───────────────────────────┐  │
 │  │ Evidence Retrieval       │────────────►│ Verification Engine       │  │
 │  └──────────────────────────┘             └─────────────┬─────────────┘  │
 │                                                         │                │
 │  ┌──────────────────────────┐             ┌─────────────▼─────────────┐  │
 │  │ Timeline Builder         │◄────────────│ Evidence Readiness Score  │  │
 │  └─────────────┬────────────┘             └─────────────┬─────────────┘  │
 │                │                                        │                │
 │                └───────────────────┬────────────────────┘                │
 │                                    │                                     │
 │                       ┌────────────▼─────────────┐                       │
 │                       │  AI Reasoning Service    │                       │
 │                       │  (Google Gemini LLM)     │                       │
 │                       └────────────┬─────────────┘                       │
 │                                    │                                     │
 │                       ┌────────────▼─────────────┐                       │
 │                       │  Decision Engine         │                       │
 │                       │  & Safety Overrides      │                       │
 │                       └────────────┬─────────────┘                       │
 │                                    │                                     │
 │  ┌──────────────────────────┐      │      ┌───────────────────────────┐  │
 │  │ Audit Trail Service      │◄─────┴─────►│ Mock Razorpay Adapter     │  │
 │  └──────────────────────────┘             └───────────────────────────┘  │
 └────────────────────────────────────┬─────────────────────────────────────┘
                                      │
 ┌────────────────────────────────────▼─────────────────────────────────────┐
 │                         SQLite Database Layer                            │
 └──────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Core Architecture Principles

### 1. Deterministic Code = Correctness
Factual consistency checks (Order ID matching, payment amount equality, delivery date vs dispute date validation) are implemented as deterministic Python functions. They return machine-readable results with explicit status, severity, expected, and actual values.

### 2. AI = Reasoning
LLMs excel at semantic reasoning, interpreting customer chat logs, synthesizing multiple verified facts, and articulating clear explanations. However, LLMs are NOT allowed to modify factual data, invent records, or override deterministic checks.

### 3. Human = Final Judgment
Automatic financial actions are blocked when critical data conflicts exist. A human analyst MUST review and approve contest submissions.

### 4. Audit = Accountability
Every action, evidence retrieval, deterministic check failure, LLM invocation, retry, and human decision is immutably logged to an SQLite audit trail.

---

## 3. Component Responsibilities

### 3.1 Verification Engine (`verification_engine.py`)
Executes 8 deterministic checks:
1. `payment_amount_consistency`: Dispute Amount == Payment Amount == Order Amount.
2. `order_id_consistency`: Payment Order ID == Delivery Order ID == Invoice Order ID. (Detects `ORD1001` vs `ORD1002`).
3. `customer_id_consistency`: Customer ID consistency across order, payment, and delivery.
4. `delivery_date_validity`: Delivery completed date <= Dispute creation date.
5. `dispute_date_validity`: Dispute date >= Order creation date.
6. `required_evidence_completeness`: Validates presence of mandatory categories (Proof of Delivery, Invoice, Order Confirmation).
7. `duplicate_evidence_detection`: Identifies duplicate files.
8. `detect_missing_evidence`: Identifies missing categories.

### 3.2 Evidence Retrieval & Mapping (`evidence_retrieval.py`)
Retrieves dispute evidence items and maps their status (`VERIFIED`, `CONTRADICTED`, `MISSING`, `PARTIALLY_VERIFIED`) based on deterministic verification output.

### 3.3 Timeline Builder (`timeline_builder.py`)
Constructs an immutable chronological event sequence:
Order Placed -> Payment Captured -> Invoice Issued -> Shipment Dispatched -> Delivery Completed -> Customer Communication -> Dispute Filed.
Timeline events are generated strictly from DB records; AI cannot create timeline events.

### 3.4 Evidence Readiness Score (`readiness_score.py`)
Calculates a 0-100 score with explicit sub-component progress bars:
- Required Evidence Completeness (40 pts max)
- Evidence Data Consistency (30 pts max)
- Timeline & Delivery Support (15 pts max)
- Customer Communication Integrity (15 pts max)

### 3.5 AI Investigation Service (`ai_service.py` & `guardrails.py`)
Sends controlled, verified context to Gemini API. Enforces 13 system prompt guardrails. Passes output through Pydantic JSON validation. Falls back to deterministic rule-based reasoning if LLM API is unavailable.

### 3.6 Decision Engine (`decision_engine.py`)
Applies policy matrix:
- **SAFETY OVERRIDE 1**: If any verification check fails with `CRITICAL` or `HIGH` severity (e.g. Order ID mismatch `ORD1001` vs `ORD1002`), decision is forcibly overridden to `HUMAN_REVIEW` and auto-contest is blocked.
- **SAFETY OVERRIDE 2**: If AI is unavailable -> `HUMAN_REVIEW`.
- **SAFETY OVERRIDE 3**: If Evidence Readiness Score < 50 -> `HUMAN_REVIEW`.
- **SAFETY OVERRIDE 4**: If AI Confidence < 0.75 -> `HUMAN_REVIEW`.
- **PASS**: High confidence + Passed checks + Readiness >= 80 -> `CONTEST`.

### 3.7 Audit Service (`audit_service.py`)
Logs events to SQLite with unique IDs, timestamps, descriptions, and metadata.

### 3.8 Mock Razorpay Adapter (`razorpay_service.py`)
Provides mock interfaces for dispute querying, evidence document uploading, and contest submission.

---

## 4. Failure Handling & Resilience
1. **External Carrier API Failure**: 3 bounded retry attempts, HTTP 504 timeout capture, safe degradation to `HUMAN_REVIEW` with evidence marked unavailable.
2. **LLM Provider Outage**: Returns structured fallback output without crashing the pipeline.
3. **Malformed Evidence**: Flags malformed document, continues analysis with remaining valid records.

---

## 5. Productionization Roadmap

If evolving this prototype into a high-scale production enterprise service:

1. **Real Razorpay Integration**: Replace `MockRazorpayAdapter` with authenticated Razorpay APIs (`/v1/disputes`, `/v1/payments`).
2. **Event-Driven Architecture**: Introduce Redis / Kafka event bus for async dispute processing.
3. **Scalable Database & Caching**: Migrate SQLite to PostgreSQL with Read Replicas and Redis cache for transaction lookups.
4. **Authentication & Authorization**: Implement OAuth2 / JWT with Role-Based Access Control (RBAC) for merchant analysts.
5. **Observability & Monitoring**: Integrate OpenTelemetry, Prometheus metrics, Grafana dashboards, and LLM drift monitoring (Arize / TruLens).
6. **Data Privacy & Encryption**: Encrypt PII fields (customer names, emails, shipping addresses) at rest using AWS KMS / GCP KMS.
