"""LangGraph workflow state definition."""

from typing import Any
from typing_extensions import TypedDict


class IntakeWorkflowState(TypedDict, total=False):
    case_id: str
    session_messages: list[dict]
    extracted_document_texts: list[str]
    document_extraction_results: list[dict]
    follow_up_round: int

    # Agent outputs
    intake_output: dict[str, Any]
    risk_output: dict[str, Any]
    quality_output: dict[str, Any]
    bias_output: dict[str, Any]
    explanation_output: dict[str, Any]

    # Duplicate detection
    duplicate_matches: list[dict]
    duplicate_pending_confirmation: bool
    matched_case_id: str

    # Routing
    needs_followup: bool
    escalated: bool
    escalation_reason: str
    escalation_stage: str
    final_status: str

    # Human review
    human_review_required: bool
    human_review_reason: str
