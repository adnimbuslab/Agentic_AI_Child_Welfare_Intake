"""MCP-001: Intake MCP Server — CRUD for IntakeCases and IntakeMessages."""

import uuid
from datetime import datetime, timezone
from backend.db import get_table
from backend.models.intake_case import IntakeCase, CaseStatus
from backend.models.intake_message import IntakeMessage, SenderType, MessageType


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _generate_case_id() -> str:
    year = datetime.now(timezone.utc).year
    seq = uuid.uuid4().int % 10000
    return f"CW-{year}-{seq:04d}"


def create_intake_case(reporter_type: str) -> dict:
    """MCP-001-T1: Create a new case record."""
    table = get_table("IntakeCases")
    now = _now()
    case = IntakeCase(
        caseId=_generate_case_id(),
        status=CaseStatus.IN_PROGRESS,
        reporterType=reporter_type,
        createdAt=now,
        updatedAt=now,
    )
    table.put_item(Item=case.to_dynamo())
    return case.model_dump()


def get_intake_case(case_id: str) -> dict | None:
    """MCP-001-T2: Retrieve full case record."""
    table = get_table("IntakeCases")
    resp = table.get_item(Key={"caseId": case_id})
    item = resp.get("Item")
    if not item:
        return None
    return IntakeCase.from_dynamo(item).model_dump()


def update_intake_case(case_id: str, updates: dict) -> dict:
    """MCP-001-T3: Update case fields."""
    table = get_table("IntakeCases")
    updates["updatedAt"] = _now()
    expr_parts = []
    expr_values = {}
    expr_names = {}
    for i, (key, val) in enumerate(updates.items()):
        alias = f"#k{i}"
        placeholder = f":v{i}"
        expr_parts.append(f"{alias} = {placeholder}")
        expr_names[alias] = key
        expr_values[placeholder] = val
    table.update_item(
        Key={"caseId": case_id},
        UpdateExpression="SET " + ", ".join(expr_parts),
        ExpressionAttributeNames=expr_names,
        ExpressionAttributeValues=expr_values,
    )
    return get_intake_case(case_id)


def save_structured_intake(case_id: str, structured_fields: dict) -> dict:
    """MCP-001-T4: Write extracted structured fields."""
    return update_intake_case(case_id, {"structuredFields": structured_fields})


def save_intake_message(
    case_id: str,
    message_text: str,
    sender_type: str,
    message_type: str,
    agent_generated: bool = False,
    attachments: list[str] | None = None,
) -> dict:
    """MCP-001-T5: Append a message to IntakeMessages."""
    table = get_table("IntakeMessages")
    now = _now()
    ts = now + "#" + uuid.uuid4().hex[:8]
    msg = IntakeMessage(
        caseId=case_id,
        messageTimestamp=ts,
        senderType=SenderType(sender_type),
        messageText=message_text,
        messageType=MessageType(message_type),
        agentGenerated=agent_generated,
        attachments=attachments,
        createdAt=now,
    )
    table.put_item(Item=msg.to_dynamo())
    return msg.model_dump()


def get_intake_messages(case_id: str) -> list[dict]:
    """Retrieve all messages for a case, ordered by timestamp."""
    table = get_table("IntakeMessages")
    resp = table.query(
        KeyConditionExpression="caseId = :cid",
        ExpressionAttributeValues={":cid": case_id},
        ScanIndexForward=True,
    )
    return [IntakeMessage.from_dynamo(item).model_dump() for item in resp.get("Items", [])]
