"""LangGraph workflow orchestration (WF-001 through WF-013)."""

from langgraph.graph import StateGraph, END
from backend.workflow.state import IntakeWorkflowState
from backend.agents import intake_understanding, risk_assessment, data_quality, bias_monitoring, explanation
from backend.agents import duplicate_detector
from backend.mcp_servers import (
    intake_server,
    audit_server,
    knowledge_server,
    risk_server as risk_mcp,
    case_history_server,
    notification_server,
)
from backend.config import MAX_FOLLOWUP_ROUNDS


# --- WF-002: Intake Understanding Node ---

def intake_understanding_node(state: IntakeWorkflowState) -> dict:
    required_fields = knowledge_server.get_intake_required_fields()
    current_case = intake_server.get_intake_case(state["case_id"])
    current_fields = current_case.get("structuredFields") if current_case else None

    output = intake_understanding.run(
        session_messages=state.get("session_messages", []),
        extracted_document_texts=state.get("extracted_document_texts"),
        current_structured_fields=current_fields,
    )

    intake_server.save_structured_intake(state["case_id"], output.get("structuredFields", {}))

    audit_server.save_agent_decision(
        case_id=state["case_id"],
        agent_name="intake-understanding",
        output_json=output,
        confidence_score=output.get("overallConfidenceScore"),
        escalated=output.get("escalate", False),
        escalation_reason=output.get("escalationReason"),
        input_summary=f"{len(state.get('session_messages', []))} messages processed",
    )

    return {"intake_output": output}


# --- WF-002b: Duplicate Check Node ---

def duplicate_check_node(state: IntakeWorkflowState) -> dict:
    structured = state.get("intake_output", {}).get("structuredFields", {})
    existing_cases = case_history_server.search_existing_cases()

    matches = duplicate_detector.find_duplicates(
        new_fields=structured,
        existing_cases=existing_cases,
        current_case_id=state["case_id"],
    )

    audit_server.save_agent_decision(
        case_id=state["case_id"],
        agent_name="duplicate-detector",
        output_json={"matches": matches, "candidateCount": len(existing_cases)},
        confidence_score=matches[0]["confidence"] if matches else 0.0,
    )

    if matches and matches[0].get("confirmationRequired"):
        return {
            "duplicate_matches": matches,
            "duplicate_pending_confirmation": True,
        }

    if matches and matches[0].get("autoMatch"):
        return {
            "duplicate_matches": matches,
            "duplicate_pending_confirmation": False,
            "matched_case_id": matches[0]["caseId"],
        }

    return {
        "duplicate_matches": matches,
        "duplicate_pending_confirmation": False,
    }


def duplicate_router(state: IntakeWorkflowState) -> str:
    if state.get("duplicate_pending_confirmation"):
        return "duplicate_confirmation_needed"
    if state.get("matched_case_id"):
        return "duplicate_confirmation_needed"
    return "follow_up_check"


# --- WF-003: Follow-Up Question Router ---

def follow_up_router(state: IntakeWorkflowState) -> str:
    output = state.get("intake_output", {})

    if output.get("escalate"):
        return "human_review_queue"

    missing = output.get("missingRequiredFields", [])
    round_num = state.get("follow_up_round", 0)

    if missing and round_num < MAX_FOLLOWUP_ROUNDS:
        return "needs_followup"

    if missing and round_num >= MAX_FOLLOWUP_ROUNDS:
        return "human_review_queue"

    return "risk_assessment"


# --- WF-004: Risk Assessment Node ---

def risk_assessment_node(state: IntakeWorkflowState) -> dict:
    policy = knowledge_server.get_risk_policy_guidelines()
    prior = case_history_server.get_prior_referrals()
    structured = state.get("intake_output", {}).get("structuredFields", {})

    quality_score = state.get("quality_output", {}).get("dataQualityScore", 0.7)
    risk_calc = risk_mcp.calculate_risk_score(structured, quality_score)

    output = risk_assessment.run(
        structured_fields=structured,
        data_quality_score=quality_score,
        document_summaries=state.get("extracted_document_texts"),
    )

    risk_mcp.save_risk_assessment(state["case_id"], output)

    audit_server.save_agent_decision(
        case_id=state["case_id"],
        agent_name="risk-assessment",
        output_json=output,
        confidence_score=output.get("confidenceScore"),
        escalated=output.get("escalate", False),
        escalation_reason=output.get("escalationReason"),
    )

    intake_server.update_intake_case(state["case_id"], {
        "riskLevel": output.get("riskLevel"),
        "riskConfidence": str(output.get("confidenceScore", 0)),
        "urgency": output.get("urgency"),
    })

    return {"risk_output": output}


# --- WF-005: Risk Confidence Gate ---

def risk_gate(state: IntakeWorkflowState) -> str:
    output = state.get("risk_output", {})
    if output.get("escalate"):
        return "human_review_queue"
    return "data_quality"


# --- WF-006: Data Quality Node ---

def data_quality_node(state: IntakeWorkflowState) -> dict:
    knowledge_server.get_intake_required_fields()
    structured = state.get("intake_output", {}).get("structuredFields", {})

    output = data_quality.run(
        structured_fields=structured,
        intake_messages=state.get("session_messages"),
        document_extraction_results=state.get("document_extraction_results"),
        follow_up_round=state.get("follow_up_round", 0),
    )

    audit_server.save_agent_decision(
        case_id=state["case_id"],
        agent_name="data-quality",
        output_json=output,
        confidence_score=output.get("dataQualityScore"),
        escalated=output.get("escalate", False),
        escalation_reason=output.get("escalationReason"),
    )

    intake_server.update_intake_case(state["case_id"], {
        "dataQualityScore": str(output.get("dataQualityScore", 0)),
    })

    return {"quality_output": output}


# --- WF-007: Data Quality Gate ---

def quality_gate(state: IntakeWorkflowState) -> str:
    output = state.get("quality_output", {})
    if output.get("escalate"):
        return "human_review_queue"
    if not output.get("readyForReview", True):
        return "needs_followup"
    return "bias_monitoring"


# --- WF-008: Bias Monitoring Node ---

def bias_monitoring_node(state: IntakeWorkflowState) -> dict:
    bias_policy = knowledge_server.get_bias_monitoring_policy()
    structured = state.get("intake_output", {}).get("structuredFields", {})
    risk_out = state.get("risk_output", {})

    output = bias_monitoring.run(
        risk_assessment_output=risk_out,
        structured_fields=structured,
        bias_policy=bias_policy,
    )

    audit_server.save_agent_decision(
        case_id=state["case_id"],
        agent_name="bias-monitoring",
        output_json=output,
        confidence_score=output.get("biasConfidence"),
        escalated=output.get("humanReviewRequired", False),
        escalation_reason=output.get("escalationReason"),
    )

    intake_server.update_intake_case(state["case_id"], {
        "biasStatus": output.get("biasStatus"),
    })

    return {"bias_output": output}


# --- WF-009: Bias Gate ---

def bias_gate(state: IntakeWorkflowState) -> str:
    output = state.get("bias_output", {})
    if output.get("humanReviewRequired") or output.get("biasStatus") == "Flagged":
        return "human_review_queue"
    return "save_intake"


# --- WF-010: Save Final Intake Record ---

def save_intake_node(state: IntakeWorkflowState) -> dict:
    intake_server.update_intake_case(state["case_id"], {
        "structuredFields": state.get("intake_output", {}).get("structuredFields", {}),
    })

    audit_server.save_agent_decision(
        case_id=state["case_id"],
        agent_name="system",
        output_json={"action": "save_final_intake_record"},
    )

    return {}


# --- WF-011: Explanation Node ---

def explanation_node(state: IntakeWorkflowState) -> dict:
    output = explanation.run(
        intake_understanding_output=state.get("intake_output", {}),
        risk_assessment_output=state.get("risk_output", {}),
        data_quality_output=state.get("quality_output", {}),
        bias_monitoring_output=state.get("bias_output", {}),
        case_id=state["case_id"],
    )

    audit_server.save_agent_decision(
        case_id=state["case_id"],
        agent_name="explanation",
        output_json=output,
        escalated=output.get("humanReviewRequired", False),
        escalation_reason=output.get("humanReviewReason"),
    )

    final_status = output.get("finalCaseStatus", "ESCALATED_TO_SUPERVISOR")
    intake_server.update_intake_case(state["case_id"], {"status": final_status})

    if final_status == "READY_FOR_CASEWORKER_REVIEW":
        notification_server.notify_caseworker(state["case_id"])

    return {
        "explanation_output": output,
        "final_status": final_status,
        "human_review_required": output.get("humanReviewRequired", False),
    }


def explanation_gate(state: IntakeWorkflowState) -> str:
    if state.get("human_review_required"):
        return "human_review_queue"
    return "end"


# --- WF-012: Human Review Queue Node ---

def human_review_queue_node(state: IntakeWorkflowState) -> dict:
    stage = "final-gate"
    reason = "Escalated for human review"

    intake_out = state.get("intake_output", {})
    risk_out = state.get("risk_output", {})
    quality_out = state.get("quality_output", {})
    bias_out = state.get("bias_output", {})

    if intake_out.get("escalate"):
        stage = "post-intake"
        reason = intake_out.get("escalationReason", reason)
    elif risk_out.get("escalate"):
        stage = "post-risk"
        reason = risk_out.get("escalationReason", reason)
    elif quality_out.get("escalate"):
        stage = "post-quality"
        reason = quality_out.get("escalationReason", reason)
    elif bias_out.get("humanReviewRequired"):
        stage = "post-bias"
        reason = bias_out.get("escalationReason", reason)

    notification_server.route_to_human_review(
        case_id=state["case_id"],
        reason=reason,
        escalation_type=stage,
    )

    risk_level = risk_out.get("riskLevel", "")
    if risk_level == "Critical":
        notification_server.notify_supervisor(state["case_id"], reason)

    audit_server.save_escalation_reason(
        case_id=state["case_id"],
        agent_name="workflow",
        reason=reason,
    )

    status = "ESCALATED_TO_SUPERVISOR"
    if risk_level == "Critical":
        status = "CRITICAL_IMMEDIATE_REVIEW"
    elif bias_out.get("biasStatus") == "Flagged":
        status = "BIAS_REVIEW_REQUIRED"

    intake_server.update_intake_case(state["case_id"], {
        "status": status,
        "humanReviewRequired": True,
        "humanReviewReason": reason,
    })

    return {
        "escalated": True,
        "escalation_reason": reason,
        "escalation_stage": stage,
        "final_status": status,
    }


# --- Needs Follow-Up Node (sends questions back, pauses for user) ---

def needs_followup_node(state: IntakeWorkflowState) -> dict:
    questions = state.get("intake_output", {}).get("followUpQuestions", [])
    round_num = state.get("follow_up_round", 0) + 1

    if questions:
        question_text = "\n".join(f"- {q}" for q in questions)
        intake_server.save_intake_message(
            case_id=state["case_id"],
            message_text=question_text,
            sender_type="agent",
            message_type="follow-up-question",
            agent_generated=True,
        )

    intake_server.update_intake_case(state["case_id"], {
        "missingFieldHistory": state.get("intake_output", {}).get("missingRequiredFields", []),
    })

    return {
        "follow_up_round": round_num,
        "needs_followup": True,
    }


# --- Duplicate Confirmation Needed Node (pauses workflow, returns to user) ---

def duplicate_confirmation_node(state: IntakeWorkflowState) -> dict:
    matches = state.get("duplicate_matches", [])
    if matches:
        match_info = matches[0]
        intake_server.save_intake_message(
            case_id=state["case_id"],
            message_text=f"Potential duplicate detected: case {match_info['caseId']} "
                         f"(confidence: {match_info['confidence']:.0%}). "
                         f"Reason: {match_info.get('reasoning', 'N/A')}",
            sender_type="agent",
            message_type="duplicate-check",
            agent_generated=True,
        )
    return {"duplicate_pending_confirmation": True}


# --- Build the graph ---

def build_workflow() -> StateGraph:
    graph = StateGraph(IntakeWorkflowState)

    graph.add_node("intake_understanding", intake_understanding_node)
    graph.add_node("duplicate_check", duplicate_check_node)
    graph.add_node("duplicate_confirmation_needed", duplicate_confirmation_node)
    graph.add_node("follow_up_check", lambda state: {})
    graph.add_node("risk_assessment", risk_assessment_node)
    graph.add_node("data_quality", data_quality_node)
    graph.add_node("bias_monitoring", bias_monitoring_node)
    graph.add_node("save_intake", save_intake_node)
    graph.add_node("explanation", explanation_node)
    graph.add_node("human_review_queue", human_review_queue_node)
    graph.add_node("needs_followup", needs_followup_node)

    graph.set_entry_point("intake_understanding")

    graph.add_edge("intake_understanding", "duplicate_check")

    graph.add_conditional_edges("duplicate_check", duplicate_router, {
        "duplicate_confirmation_needed": "duplicate_confirmation_needed",
        "follow_up_check": "follow_up_check",
    })

    graph.add_edge("duplicate_confirmation_needed", END)

    graph.add_conditional_edges("follow_up_check", follow_up_router, {
        "risk_assessment": "risk_assessment",
        "human_review_queue": "human_review_queue",
        "needs_followup": "needs_followup",
    })

    graph.add_edge("needs_followup", END)

    graph.add_conditional_edges("risk_assessment", risk_gate, {
        "data_quality": "data_quality",
        "human_review_queue": "human_review_queue",
    })

    graph.add_conditional_edges("data_quality", quality_gate, {
        "bias_monitoring": "bias_monitoring",
        "human_review_queue": "human_review_queue",
        "needs_followup": "needs_followup",
    })

    graph.add_conditional_edges("bias_monitoring", bias_gate, {
        "save_intake": "save_intake",
        "human_review_queue": "human_review_queue",
    })

    graph.add_edge("save_intake", "explanation")

    graph.add_conditional_edges("explanation", explanation_gate, {
        "human_review_queue": "human_review_queue",
        "end": END,
    })

    graph.add_edge("human_review_queue", END)

    return graph


def compile_workflow():
    graph = build_workflow()
    return graph.compile()
