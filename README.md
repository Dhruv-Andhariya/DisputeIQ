# DisputeIQ — AI-Powered Dispute Investigation & Evidence Intelligence Layer

[![Track](https://img.shields.io/badge/Razorpay_Internship_2027-Track_2:_AI_Risk_Manager-blue.svg)](https://razorpay.com)
[![Python](https://img.shields.io/badge/Python-3.11+-3776AB?logo=python&logoColor=white)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.109+-009688?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![React](https://img.shields.io/badge/React-18.2+-61DAFB?logo=react&logoColor=white)](https://reactjs.org)
[![Gemini](https://img.shields.io/badge/AI-Google_Gemini-8E44AD?logo=google&logoColor=white)](https://deepmind.google/technologies/gemini/)

> **Official Project Objective:** *"Stop the merchant losing money to fraud, returns and chargebacks."*

---

## 1. Problem Statement & Context
Merchant dispute and chargeback investigation is **not** simply about receiving a dispute notification and blindly submitting an evidence PDF.

Existing payment infrastructure tells the merchant:
```
"A dispute has been raised."
```

**DisputeIQ** sits on top of existing payment/dispute infrastructure to answer:
```
"Is this dispute defensible?
 What evidence supports the merchant?
 Is the evidence internally consistent?
 What happened across the transaction lifecycle?
 What should the merchant do, and why?"
```

---

## 2. Core Architecture Philosophy

```
┌────────────────────────────────────────────────────────┐
│  DETERMINISTIC CODE  =  CORRECTNESS                    │
│  AI                  =  REASONING                      │
│  HUMAN               =  FINAL JUDGMENT                 │
│  AUDIT               =  ACCOUNTABILITY                 │
└────────────────────────────────────────────────────────┘
```

DisputeIQ strictly enforces this distinction:
- **Deterministic Code**: Handles factual consistency, ID matching, amount verification, timestamp validation, and safety override blocks.
- **AI Reasoning**: Interprets customer communications, synthesizes context across verified facts, and generates structured explanations.
- **Human Controls**: Human operators retain sole execution authority for financial submissions.
- **Audit Trail**: Every verification, retry, LLM output, and human approval is immutably logged.

---

## 3. Non-Negotiable Differentiators

### 1. Evidence Verification & Deterministic Overrides
Never blindly trust evidence. Deterministic verification detects data corruptions and conflicts BEFORE AI reasoning.
- **Example**: Dispute raised for Order `ORD1001`, invoice shows `ORD1001`, but delivery proof references `ORD1002`.
- **System Action**: Flags a **HIGH Severity Order Identity Conflict**.
- **Critical Safety Rule**: The LLM CANNOT override this deterministic check. Even if AI suggests `CONTEST` with 94% confidence, the final system decision is forcibly set to `HUMAN_REVIEW` and automated action is blocked!

### 2. Chronological Timeline Reconstruction
DisputeIQ reconstructs the complete transaction lifecycle:
$$\text{Order} \longrightarrow \text{Payment} \longrightarrow \text{Invoice} \longrightarrow \text{Shipment} \longrightarrow \text{Delivery} \longrightarrow \text{Customer Comm} \longrightarrow \text{Dispute}$$
- Assembled 100% deterministically from verified DB records.
- The AI is strictly forbidden from fabricating timeline events.

### 3. Bounded AI + Human-in-the-Loop Controls
- **AI Capabilities**: Investigates, reasons, summarizes, identifies supporting evidence, flags missing evidence, and suggests recommendations.
- **AI Boundaries**: Cannot fabricate evidence, alter verified facts, override deterministic checks, or execute financial actions.
- **Human Control Point**: Final contest submission requires explicit human approval.

---

## 4. Scope (MVP)
Supported Dispute Category: **Goods / Services Not Received**

---

## 5. Technology Stack
- **Backend**: Python 3.11+, FastAPI, Pydantic v2
- **Database**: SQLite (via standard Python `sqlite3` + JSON fields)
- **Frontend**: React (Vite), Tailwind CSS, Axios, Lucide React Icons
- **AI Service**: Google Gemini API via `google-genai` (wrapped inside `ai_service.py`)
- **Testing & Evaluation**: Pytest, standalone evaluation benchmark pipeline

---

## 6. Architecture & Modular Structure

```
DisputeIQ/
├── PROJECT_SPEC.md              # Authoritative product & engineering specification
├── README.md                    # System documentation
├── .env.example                 # Environment variables configuration template
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI app initialization & CORS setup
│   │   ├── api/routes.py        # REST API endpoints
│   │   ├── models/domain.py     # Pydantic domain entities
│   │   ├── services/
│   │   │   ├── verification_engine.py   # Deterministic verification functions
│   │   │   ├── evidence_retrieval.py    # Database evidence retrieval & mapping
│   │   │   ├── timeline_builder.py      # Chronological timeline builder
│   │   │   ├── readiness_score.py       # Decomposable Evidence Readiness Score
│   │   │   ├── decision_engine.py       # Policy decision matrix & safety overrides
│   │   │   ├── audit_service.py         # Immutable SQLite audit logger
│   │   │   ├── razorpay_service.py      # Mock Razorpay Adapter
│   │   │   └── dispute_service.py       # Main pipeline orchestrator
│   │   ├── ai/
│   │   │   ├── ai_service.py            # Gemini LLM integration & safe fallback
│   │   │   ├── prompts.py               # System prompt & 13 guardrail directives
│   │   │   └── guardrails.py            # Pydantic JSON parser & validator
│   │   └── database/
│   │       ├── db.py                    # SQLite persistence layer
│   │       └── seed.py                  # Database seeder
│   └── tests/
│       └── test_verification.py         # Pytest verification test suite
├── frontend/
│   └── src/
│       ├── components/          # React UI components (EvidenceMatrix, VerificationList, etc.)
│       └── pages/               # DisputeList & InvestigationDetail pages
├── data/synthetic/              # Seed generator (40 disputes across 5 archetypes)
└── evaluation/                  # Evaluation pipeline & held-out test suite
```

---

## 7. Synthetic Data Archetypes
Generated using a fixed random seed (`seed=42`) creating 40 dispute records:
1. `STRONG_CASE` (12 disputes): Full proof of delivery signed by customer, matching amounts/IDs, valid timeline.
2. `WEAK_CASE` (8 disputes): Delivery proof signed by reception/guard, or missing carrier signature.
3. `CONTRADICTORY_CASE` (10 disputes): Controlled corruptions (Order ID mismatch `ORD1001` vs `ORD1002`, amount mismatch, delivery date after dispute filing).
4. `MISSING_EVIDENCE_CASE` (5 disputes): Missing carrier tracking proof or invoice document.
5. `EDGE_CASE` (5 disputes): Wrong category conflict (Customer complaints about damaged goods filed under Goods Not Received).

---

## 8. Decomposable Evidence Readiness Score (0 - 100)
Every score is fully explainable with 4 sub-component progress indicators:
- **Required Evidence Completeness**: 40 pts (POD 20, Invoice 10, Order Conf 10)
- **Evidence Data Consistency**: 30 pts (Deductions for check failures)
- **Timeline & Delivery Support**: 15 pts (Carrier verified status 10, Recipient signature 5)
- **Customer Communication Integrity**: 15 pts (Customer interaction logs present 15)

---

## 9. Evaluation Results (Held-Out Test Set)

Run evaluation script:
```bash
python evaluation/evaluate.py
```
Output saved to `evaluation/results/summary.json`:
- **Held-Out Test Cases**: 25 disputes
- **Recommendation Accuracy**: `100%`
- **False-Contest Rate**: `0.0%` (Zero dangerous false contests on contradictory cases!)
- **False-Acceptance Rate**: `0.0%`
- **Human Escalation Rate**: `72.0%` (Safely escalates ambiguous & contradictory cases to humans)

---

## 10. Installation & Quickstart

### Prerequisites
- Python 3.11+
- Node.js 18+ & npm

### Backend Setup
```bash
# Clone and enter repository
cd Razor_pay

# Create virtual environment & install requirements
python -m venv venv
venv\Scripts\activate
pip install -r backend/requirements.txt

# Create .env file
cp .env.example .env

# Seed database with 40 synthetic dispute cases
python backend/app/database/seed.py

# Run pytest unit verification suite
python -m pytest backend/tests

# Start FastAPI backend server
python backend/app/main.py
```
Backend server will start at `http://localhost:8000`.

### Frontend Setup
```bash
cd frontend
npm install
npm run dev
```
Frontend app will start at `http://localhost:3000`.

---

## 11. Three Live Demo Scenarios

### SCENARIO 1 — Strong Case (Automated Contest Path)
- Select `DSP-2026-001` (Case Type: `STRONG_CASE`).
- **Observed Behavior**: All deterministic checks pass, Evidence Readiness > 85/100, AI recommends `CONTEST`, decision is `CONTEST`.
- Human click "Approve & Prepare Submission" -> Mock Razorpay Adapter logs submission.

### SCENARIO 2 — Contradictory Case (Order ID Mismatch - Primary Demo Moment)
- Select `DSP-2026-005` (Case Type: `CONTRADICTORY_CASE`, Order ID mismatch `ORD-1005` vs `ORD-ERR-005`).
- **Observed Behavior**: Deterministic verification check `order_id_consistency` **FAILS** with `HIGH` severity.
- **Safety Override Triggered**: Decision engine forcibly overrides decision to **`HUMAN_REVIEW`** and blocks automated contesting!

### SCENARIO 3 — System Failure & Safe Degradation
- On any Investigation Detail page, click the **"Simulate System Failure"** button.
- **Observed Behavior**: System logs 3 bounded retry attempts to external Carrier Logistics API, captures HTTP 504 timeout, marks evidence unavailable, drops confidence to 0.20, degrades safely to **`HUMAN_REVIEW`**, and logs audit events!

---

## 12. License & Author
Built for **Razorpay Internship 2027 — Track 2: AI Risk Manager**.
