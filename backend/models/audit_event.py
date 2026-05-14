from enum import Enum
from typing import Optional
from pydantic import BaseModel


class EventType(str, Enum):
    AGENT_DECISION = "agent-decision"
    STATE_TRANSITION = "state-transition"
    HUMAN_OVERRIDE = "human-override"
    ESCALATION = "escalation"
    FIELD_EXTRACTION = "field-extraction"
    BIAS_FLAG = "bias-flag"


class AuditEvent(BaseModel):
    caseId: str
    eventTimestamp: str
    eventType: EventType
    actor: str
    agentName: Optional[str] = None
    action: str
    reason: Optional[str] = None
    beforeState: Optional[dict] = None
    afterState: Optional[dict] = None
    createdAt: str = ""

    def to_dynamo(self) -> dict:
        from backend.db import sanitize_for_dynamo
        return sanitize_for_dynamo(self.model_dump(exclude_none=True))

    @classmethod
    def from_dynamo(cls, item: dict) -> "AuditEvent":
        return cls(**item)
