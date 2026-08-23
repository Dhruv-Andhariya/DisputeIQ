import os
import json
from typing import List, Optional, Dict, Any
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel

from app.models.domain import Dispute, Investigation, Evidence, TimelineEvent, AuditEvent
from app.database.db import get_all_disputes, get_dispute_by_id, get_investigation_by_dispute_id
from app.services.dispute_service import DisputeService
from app.services.evidence_retrieval import EvidenceRetrievalService
from app.services.audit_service import AuditService

router = APIRouter()

class HumanActionRequest(BaseModel):
    notes: Optional[str] = None

class DemoFailureRequest(BaseModel):
    dispute_id: str

@router.get("/health")
def health_check():
    return {"status": "ok", "app": "DisputeIQ AI Risk Manager API", "version": "1.0.0"}

@router.get("/disputes", response_model=List[Dispute])
def list_disputes():
    return get_all_disputes()

@router.get("/disputes/{dispute_id}", response_model=Dispute)
def get_dispute(dispute_id: str):
    dispute = get_dispute_by_id(dispute_id)
    if not dispute:
        raise HTTPException(status_code=404, detail=f"Dispute {dispute_id} not found.")
    return dispute

@router.post("/disputes/{dispute_id}/investigate", response_model=Investigation)
def investigate_dispute(dispute_id: str):
    try:
        return DisputeService.run_investigation(dispute_id)
    except ValueError as ve:
        raise HTTPException(status_code=404, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Investigation failure: {str(e)}")

@router.get("/disputes/{dispute_id}/evidence", response_model=List[Evidence])
def get_dispute_evidence(dispute_id: str):
    dispute = get_dispute_by_id(dispute_id)
    if not dispute:
        raise HTTPException(status_code=404, detail=f"Dispute {dispute_id} not found.")
    return EvidenceRetrievalService.retrieve_evidence(dispute_id)

@router.get("/disputes/{dispute_id}/timeline", response_model=List[TimelineEvent])
def get_dispute_timeline(dispute_id: str):
    inv = get_investigation_by_dispute_id(dispute_id)
    if not inv:
        # Run investigation to build timeline if not exists
        inv = DisputeService.run_investigation(dispute_id)
    return inv.timeline

@router.get("/disputes/{dispute_id}/audit", response_model=List[AuditEvent])
def get_dispute_audit(dispute_id: str):
    return AuditService.get_audit_trail(dispute_id)

@router.post("/disputes/{dispute_id}/approve")
def approve_dispute(dispute_id: str, req: HumanActionRequest = HumanActionRequest()):
    try:
        updated_dispute = DisputeService.approve_investigation(dispute_id, req.notes)
        return {"status": "SUCCESS", "message": "Dispute approved and contest submitted.", "dispute": updated_dispute}
    except ValueError as ve:
        raise HTTPException(status_code=404, detail=str(ve))

@router.post("/disputes/{dispute_id}/reject")
def reject_dispute(dispute_id: str, req: HumanActionRequest = HumanActionRequest()):
    try:
        updated_dispute = DisputeService.reject_investigation(dispute_id, req.notes)
        return {"status": "SUCCESS", "message": "Dispute rejected. Marked as accepted/closed.", "dispute": updated_dispute}
    except ValueError as ve:
        raise HTTPException(status_code=404, detail=str(ve))

@router.post("/demo/failure", response_model=Investigation)
def trigger_demo_failure(req: DemoFailureRequest):
    """
    Demonstrates SCENARIO 3: External API failure with bounded retries and safe degradation to HUMAN_REVIEW.
    """
    try:
        return DisputeService.simulate_system_failure(req.dispute_id)
    except ValueError as ve:
        raise HTTPException(status_code=404, detail=str(ve))

@router.get("/evaluation/summary")
def get_evaluation_summary():
    eval_path = os.path.join("evaluation", "results", "summary.json")
    if not os.path.exists(eval_path):
        return {
            "status": "NOT_RUN",
            "message": "Evaluation pipeline has not been executed yet. Run evaluation/evaluate.py to produce metrics."
        }
    with open(eval_path, "r") as f:
        return json.load(f)
