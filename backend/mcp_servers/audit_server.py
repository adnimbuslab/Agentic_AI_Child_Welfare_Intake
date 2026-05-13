"""MCP-005: Audit & Governance MCP Server — immutable audit trail."""

import uuid
from datetime import datetime, timezone
from backend.db import get_table
from backend.models.agent_output import AgentOutput, AgentStatus
from backend.models.audit_event import AuditEvent, EventType


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _unique_ts() -> str:
    return f"{_now()}#{uuid.uuid4().hex[:8]}"


def save_agent_decision(
    case_id: str,
    agent_name: str,
    output_json: dict,
    confidence_score: float | None = None,
    escalated: bool = False,
    escalation_reason: str | None = None,
    input_summary: str | None = None,
) -> dict:
    """MCP-005-T1: Write agent output record to AgentOutputs."""
    table = get_table("AgentOutputs")
    now = _now()
    record = AgentOutput(
        caseId=case_id,
        agentNameTimestamp=f"{agent_name}#{now}#{uuid.uuid4().hex[:8]}",
        agentName=agent_name,
        inputSummary=input_summary,
        outputJson=output_json,
        confidenceScore=confidence_score,
        status=AgentStatus.ESCALATED if escalated else AgentStatus.SUCCESS,
        escalationReason=escalation_reason,
        createdAt=now,
    )
    table.put_item(Item=record.to_dynamo())

    _write_audit_event(
        case_id=case_id,
        event_type=EventType.AGENT_DECISION,
        actor=agent_name,
        agent_name=agent_name,
        action=f"{agent_name} decision recorded",
        reason=escalation_reason,
        after_state=output_json,
    )
    return {"saved": True, "agentName": agent_name}


def save_confidence_score(
    case_id: str, agent_name: str, field_name: str, confidence: float
) -> dict:
    """MCP-005-T2: Record field-level confidence in AuditEvents."""
    _write_audit_event(
        case_id=case_id,
        event_type=EventType.FIELD_EXTRACTION,
        actor=agent_name,
        agent_name=agent_name,
        action=f"confidence score for {field_name}",
        after_state={"field": field_name, "confidence": confidence},
    )
    return {"saved": True}


def save_escalation_reason(
    case_id: str, agent_name: str, reason: str, before_state: dict | None = None
) -> dict:
    """MCP-005-T3: Record escalation details in AuditEvents."""
    _write_audit_event(
        case_id=case_id,
        event_type=EventType.ESCALATION,
        actor=agent_name,
        agent_name=agent_name,
        action="escalation",
        reason=reason,
        before_state=before_state,
    )
    return {"saved": True}


def save_human_override(
    case_id: str,
    reviewer_id: str,
    action: str,
    notes: str | None = None,
    override_risk_level: str | None = None,
    before_state: dict | None = None,
    after_state: dict | None = None,
) -> dict:
    """MCP-005-T4: Record human reviewer override in AuditEvents."""
    _write_audit_event(
        case_id=case_id,
        event_type=EventType.HUMAN_OVERRIDE,
        actor=reviewer_id,
        action=action,
        reason=notes,
        before_state=before_state,
        after_state=after_state or {"overrideRiskLevel": override_risk_level},
    )
    return {"saved": True}


def get_audit_timeline(case_id: str) -> list[dict]:
    """MCP-005-T5: Retrieve ordered audit events for a case."""
    table = get_table("AuditEvents")
    resp = table.query(
        KeyConditionExpression="caseId = :cid",
        ExpressionAttributeValues={":cid": case_id},
        ScanIndexForward=True,
    )
    return [AuditEvent.from_dynamo(item).model_dump() for item in resp.get("Items", [])]


def _write_audit_event(
    case_id: str,
    event_type: EventType,
    actor: str,
    action: str,
    agent_name: str | None = None,
    reason: str | None = None,
    before_state: dict | None = None,
    after_state: dict | None = None,
) -> None:
    table = get_table("AuditEvents")
    now = _now()
    event = AuditEvent(
        caseId=case_id,
        eventTimestamp=_unique_ts(),
        eventType=event_type,
        actor=actor,
        agentName=agent_name,
        action=action,
        reason=reason,
        beforeState=before_state,
        afterState=after_state,
        createdAt=now,
    )
    table.put_item(Item=event.to_dynamo())
