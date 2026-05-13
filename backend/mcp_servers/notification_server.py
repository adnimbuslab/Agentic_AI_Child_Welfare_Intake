"""MCP-006: Notification / Escalation MCP Server."""

import uuid
from datetime import datetime, timezone
from backend.db import get_table


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def route_to_human_review(case_id: str, reason: str, escalation_type: str) -> dict:
    """MCP-006-T1: Place case in human review queue."""
    table = get_table("IntakeCases")
    table.update_item(
        Key={"caseId": case_id},
        UpdateExpression="SET humanReviewRequired = :hr, humanReviewReason = :reason, updatedAt = :now",
        ExpressionAttributeValues={
            ":hr": True,
            ":reason": reason,
            ":now": _now(),
        },
    )
    return {
        "routed": True,
        "caseId": case_id,
        "escalationType": escalation_type,
        "reason": reason,
    }


def notify_caseworker(case_id: str, message: str | None = None) -> dict:
    """MCP-006-T2: Send notification to assigned caseworker (POC logs only)."""
    return {
        "notified": True,
        "caseId": case_id,
        "channel": "caseworker-dashboard",
        "message": message or f"Case {case_id} is ready for review.",
    }


def notify_supervisor(case_id: str, reason: str) -> dict:
    """MCP-006-T3: Send notification to supervisor (POC logs only)."""
    return {
        "notified": True,
        "caseId": case_id,
        "channel": "supervisor-alert",
        "reason": reason,
    }


def create_review_task(case_id: str, task_type: str, description: str) -> dict:
    """MCP-006-T4: Create a task record in the review queue."""
    return {
        "taskId": uuid.uuid4().hex[:12],
        "caseId": case_id,
        "taskType": task_type,
        "description": description,
        "status": "pending",
        "createdAt": _now(),
    }
