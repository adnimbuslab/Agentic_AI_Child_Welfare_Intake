from enum import Enum
from typing import Optional
from pydantic import BaseModel


class SenderType(str, Enum):
    USER = "user"
    AGENT = "agent"
    SYSTEM = "system"


class MessageType(str, Enum):
    NARRATIVE = "narrative"
    FOLLOW_UP_QUESTION = "follow-up-question"
    FOLLOW_UP_ANSWER = "follow-up-answer"
    SYSTEM = "system"


class IntakeMessage(BaseModel):
    caseId: str
    messageTimestamp: str
    senderType: SenderType
    messageText: str
    messageType: MessageType
    attachments: Optional[list[str]] = None
    agentGenerated: bool = False
    createdAt: str = ""

    def to_dynamo(self) -> dict:
        return self.model_dump(exclude_none=True)

    @classmethod
    def from_dynamo(cls, item: dict) -> "IntakeMessage":
        return cls(**item)
