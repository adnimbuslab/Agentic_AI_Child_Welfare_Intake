"""Human Review API route: API-006."""

from datetime import datetime, timezone
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from backend.mcp_servers import intake_server, audit_server

router = APIRouter()


class HumanReviewRequest(BaseModel):
    reviewerId: str
    action: str  # approve | override | request_more_info
    overrideRiskLevel: str | None = None
    notes: str | None = None


# --- API-006: Human Review Action ---

@router.post("/{caseId}/human-review")
def human_review_action(caseId: str, req: HumanReviewRequest):
    case = intake_server.get_intake_case(caseId)
    if not case:
        raise HTTPException(status_code=404, detail=f"Case {caseId} not found")

    valid_actions = {"approve", "override", "request_more_info"}
    if req.action not in valid_actions:
        raise HTTPException(status_code=400, detail=f"Invalid action. Must be one of: {valid_actions}")

    before_state = {
        "status": case.get("status"),
        "riskLevel": case.get("riskLevel"),
        "humanReviewRequired": case.get("humanReviewRequired"),
    }

    updates = {"humanReviewRequired": False}

    if req.action == "approve":
        updates["status"] = "READY_FOR_CASEWORKER_REVIEW"
    elif req.action == "override":
        updates["status"] = "READY_FOR_CASEWORKER_REVIEW"
        if req.overrideRiskLevel:
            updates["riskLevel"] = req.overrideRiskLevel
    elif req.action == "request_more_info":
        updates["status"] = "NEEDS_MORE_INFORMATION"

    updated_case = intake_server.update_intake_case(caseId, updates)

    audit_server.save_human_override(
        case_id=caseId,
        reviewer_id=req.reviewerId,
        action=req.action,
        notes=req.notes,
        override_risk_level=req.overrideRiskLevel,
        before_state=before_state,
        after_state=updates,
    )

    return {
        "caseId": caseId,
        "newStatus": updated_case.get("status"),
        "updatedAt": datetime.now(timezone.utc).isoformat(),
    }
