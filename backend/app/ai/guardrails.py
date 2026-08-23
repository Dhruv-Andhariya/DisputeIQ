import json
import re
from typing import Optional, List, Dict, Any
from app.models.domain import AIReasoningOutput, FinalDecision

class AIGuardrails:
    @staticmethod
    def validate_and_parse_json(raw_text: str) -> Optional[AIReasoningOutput]:
        """
        Parses raw text response from LLM, strips markdown code blocks,
        and validates structure using Pydantic AIReasoningOutput model.
        """
        if not raw_text:
            return None
            
        cleaned = raw_text.strip()
        # Remove ```json ... ``` code fence if present
        if cleaned.startswith("```"):
            cleaned = re.sub(r"^```[a-zA-Z]*\n?", "", cleaned)
            cleaned = re.sub(r"\n?```$", "", cleaned)
            cleaned = cleaned.strip()
            
        try:
            data = json.loads(cleaned)
            
            # Sanitize recommendation enum value
            rec_raw = str(data.get("recommendation", "HUMAN_REVIEW")).upper().strip()
            if rec_raw not in ["CONTEST", "DO_NOT_CONTEST", "HUMAN_REVIEW"]:
                rec = FinalDecision.HUMAN_REVIEW
            else:
                rec = FinalDecision(rec_raw)
                
            confidence = float(data.get("confidence", 0.5))
            confidence = max(0.0, min(1.0, confidence))
            
            return AIReasoningOutput(
                recommendation=rec,
                confidence=confidence,
                case_summary=str(data.get("case_summary", "Dispute analysis complete.")),
                reasoning=[str(x) for x in data.get("reasoning", [])],
                supporting_evidence=[str(x) for x in data.get("supporting_evidence", [])],
                missing_evidence=[str(x) for x in data.get("missing_evidence", [])],
                risk_flags=[str(x) for x in data.get("risk_flags", [])]
            )
        except Exception as e:
            print(f"[AIGuardrails] JSON parsing error: {e}")
            return None

    @staticmethod
    def create_fallback_output(
        case_summary: str,
        reasoning: List[str],
        risk_flags: List[str],
        recommendation: FinalDecision = FinalDecision.HUMAN_REVIEW
    ) -> AIReasoningOutput:
        """Generates structured fallback AI reasoning output when LLM API is unavailable or fails."""
        return AIReasoningOutput(
            recommendation=recommendation,
            confidence=0.5,
            case_summary=case_summary,
            reasoning=reasoning,
            supporting_evidence=["Deterministic verification logs"],
            missing_evidence=[],
            risk_flags=risk_flags
        )
