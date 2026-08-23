import os
import json
import time
from typing import Dict, Any, List
from app.models.domain import (
    Dispute, Payment, Order, Delivery, Evidence, FinalDecision
)
from app.services.verification_engine import VerificationEngine
from app.services.evidence_retrieval import EvidenceRetrievalService
from app.services.readiness_score import ReadinessScoreCalculator
from app.services.decision_engine import DecisionEngine
from app.ai.ai_service import AIService
from evaluation.test_cases.generate_eval_dataset import generate_evaluation_dataset

def run_evaluation():
    print("==================================================")
    print("      DisputeIQ System Evaluation Pipeline        ")
    print("==================================================")
    
    eval_file = os.path.join("evaluation", "test_cases", "test_dataset.json")
    if not os.path.exists(eval_file):
        print("Held-out evaluation dataset not found. Generating now...")
        generate_evaluation_dataset()
        
    with open(eval_file, "r") as f:
        test_cases = json.load(f)
        
    total_cases = len(test_cases)
    print(f"Evaluating {total_cases} held-out test cases across 5 case types...\n")
    
    correct_count = 0
    false_contest_count = 0  # System contested when it should have escalated / do not contest
    false_acceptance_count = 0 # System accepted / did not contest when it was a valid contest case
    escalated_count = 0      # System escalated to HUMAN_REVIEW
    
    case_results = []
    confusion_matrix = {
        "CONTEST": {"CONTEST": 0, "DO_NOT_CONTEST": 0, "HUMAN_REVIEW": 0},
        "DO_NOT_CONTEST": {"CONTEST": 0, "DO_NOT_CONTEST": 0, "HUMAN_REVIEW": 0},
        "HUMAN_REVIEW": {"CONTEST": 0, "DO_NOT_CONTEST": 0, "HUMAN_REVIEW": 0}
    }
    
    start_time = time.time()
    
    for case in test_cases:
        dispute = Dispute(**case["dispute"])
        payment = Payment(**case["payment"])
        order = Order(**case["order"])
        delivery = Delivery(**case["delivery"])
        evidence_list = [Evidence(**ev) for ev in case["evidence"]]
        ground_truth = case["ground_truth_decision"]
        
        # 1. Run Verification
        ver_results = VerificationEngine.run_all_checks(dispute, payment, order, delivery, evidence_list)
        mapped_evidence = EvidenceRetrievalService.map_evidence_states(evidence_list, ver_results)
        
        # 2. Readiness Score
        readiness = ReadinessScoreCalculator.calculate_score(mapped_evidence, ver_results, delivery)
        
        # 3. AI Investigation
        ai_analysis = AIService.analyze_dispute(
            dispute=dispute,
            payment=payment,
            order=order,
            delivery=delivery,
            evidence_list=mapped_evidence,
            verification_results=ver_results,
            readiness_score=readiness
        )
        
        # 4. Decision Engine
        decision_result = DecisionEngine.evaluate_decision(ver_results, readiness, ai_analysis)
        predicted = decision_result.final_decision.value
        
        # Track metrics
        if predicted == ground_truth:
            correct_count += 1
            
        if predicted == "HUMAN_REVIEW":
            escalated_count += 1
            
        # False contest: System chose CONTEST when Ground Truth was HUMAN_REVIEW or DO_NOT_CONTEST
        if predicted == "CONTEST" and ground_truth != "CONTEST":
            false_contest_count += 1
            
        # False acceptance: System chose DO_NOT_CONTEST when Ground Truth was CONTEST
        if predicted == "DO_NOT_CONTEST" and ground_truth == "CONTEST":
            false_acceptance_count += 1
            
        confusion_matrix[ground_truth][predicted] += 1
        
        case_results.append({
            "dispute_id": dispute.dispute_id,
            "case_type": dispute.case_type,
            "ground_truth": ground_truth,
            "predicted_decision": predicted,
            "confidence": decision_result.confidence,
            "safety_override_triggered": decision_result.safety_override_triggered,
            "override_reason": decision_result.override_reason,
            "matches_ground_truth": predicted == ground_truth
        })

    elapsed_time = round(time.time() - start_time, 2)
    accuracy = round((correct_count / total_cases) * 100, 2)
    false_contest_rate = round((false_contest_count / total_cases) * 100, 2)
    false_acceptance_rate = round((false_acceptance_count / total_cases) * 100, 2)
    human_escalation_rate = round((escalated_count / total_cases) * 100, 2)
    
    summary = {
        "evaluation_timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "total_test_cases": total_cases,
        "execution_time_seconds": elapsed_time,
        "metrics": {
            "recommendation_accuracy": f"{accuracy}%",
            "false_contest_rate": f"{false_contest_rate}%",
            "false_acceptance_rate": f"{false_acceptance_rate}%",
            "human_escalation_rate": f"{human_escalation_rate}%"
        },
        "raw_counts": {
            "correct": correct_count,
            "false_contests": false_contest_count,
            "false_acceptances": false_acceptance_count,
            "escalated_to_human": escalated_count
        },
        "confusion_matrix": confusion_matrix,
        "case_details": case_results
    }

    out_dir = os.path.join("evaluation", "results")
    os.makedirs(out_dir, exist_ok=True)
    out_file = os.path.join(out_dir, "summary.json")
    with open(out_file, "w") as f:
        json.dump(summary, f, indent=2)

    print("==================================================")
    print("              EVALUATION RESULTS                  ")
    print("==================================================")
    print(f"Total Test Cases:        {total_cases}")
    print(f"Accuracy:                {accuracy}%")
    print(f"False-Contest Rate:      {false_contest_rate}%")
    print(f"False-Acceptance Rate:   {false_acceptance_rate}%")
    print(f"Human-Escalation Rate:   {human_escalation_rate}%")
    print(f"Results saved to:        {out_file}")
    print("==================================================")
    
    return summary

if __name__ == "__main__":
    run_evaluation()
