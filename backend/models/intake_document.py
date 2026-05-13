from enum import Enum
from typing import Optional
from pydantic import BaseModel


class ExtractionStatus(str, Enum):
    PENDING = "pending"
    COMPLETE = "complete"
    FAILED = "failed"


ALLOWED_MIME_TYPES = {
    "application/pdf",
    "image/jpeg",
    "image/png",
    "image/gif",
    "image/bmp",
    "image/tiff",
    "video/mp4",
    "video/mpeg",
    "text/plain",
    "application/msword",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
}

BLOCKED_EXTENSIONS = {".exe", ".bat", ".cmd", ".ps1", ".sh", ".com", ".msi", ".scr"}


class IntakeDocument(BaseModel):
    caseId: str
    documentId: str
    fileName: str
    fileType: str
    storagePath: str
    extractedText: Optional[str] = None
    extractionConfidence: Optional[float] = None
    extractionStatus: ExtractionStatus = ExtractionStatus.PENDING
    documentCategory: Optional[str] = None
    createdAt: str = ""

    def to_dynamo(self) -> dict:
        item = self.model_dump(exclude_none=True)
        if self.extractionConfidence is not None:
            item["extractionConfidence"] = str(self.extractionConfidence)
        return item

    @classmethod
    def from_dynamo(cls, item: dict) -> "IntakeDocument":
        if "extractionConfidence" in item and isinstance(item["extractionConfidence"], str):
            item["extractionConfidence"] = float(item["extractionConfidence"])
        return cls(**item)
