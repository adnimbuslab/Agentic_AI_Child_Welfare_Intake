from enum import Enum
from typing import Optional
from pydantic import BaseModel


class AgentName(str, Enum):
    INTAKE_UNDERSTANDING = "intake-understanding"
    RISK_ASSESSMENT = "risk-assessment"
    DATA_QUALITY = "data-quality"
    BIAS_MONITORING = "bias-monitoring"
    EXPLANATION = "explanation"


class AgentStatus(str, Enum):
    SUCCESS = "success"
    ESCALATED = "escalated"
    ERROR = "error"


class AgentOutput(BaseModel):
    caseId: str
    agentNameTimestamp: str
    agentName: str
    inputSummary: Optional[str] = None
    outputJson: dict
    confidenceScore: Optional[float] = None
    status: AgentStatus = AgentStatus.SUCCESS
    escalationReason: Optional[str] = None
    createdAt: str = ""

    def to_dynamo(self) -> dict:
        from backend.db import sanitize_for_dynamo
        item = self.model_dump(exclude_none=True)
        if self.confidenceScore is not None:
            item["confidenceScore"] = str(self.confidenceScore)
        return sanitize_for_dynamo(item)

    @classmethod
    def from_dynamo(cls, item: dict) -> "AgentOutput":
        if "confidenceScore" in item and isinstance(item["confidenceScore"], str):
            item["confidenceScore"] = float(item["confidenceScore"])
        return cls(**item)
