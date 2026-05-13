from enum import Enum
from typing import Optional
from pydantic import BaseModel
from datetime import datetime


class CaseStatus(str, Enum):
    IN_PROGRESS = "IN_PROGRESS"
    READY_FOR_CASEWORKER_REVIEW = "READY_FOR_CASEWORKER_REVIEW"
    NEEDS_MORE_INFORMATION = "NEEDS_MORE_INFORMATION"
    ESCALATED_TO_SUPERVISOR = "ESCALATED_TO_SUPERVISOR"
    CRITICAL_IMMEDIATE_REVIEW = "CRITICAL_IMMEDIATE_REVIEW"
    BIAS_REVIEW_REQUIRED = "BIAS_REVIEW_REQUIRED"
    LOW_CONFIDENCE_REVIEW_REQUIRED = "LOW_CONFIDENCE_REVIEW_REQUIRED"


class RiskLevel(str, Enum):
    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High"
    CRITICAL = "Critical"


class IntakeCase(BaseModel):
    caseId: str
    status: CaseStatus = CaseStatus.IN_PROGRESS
    riskLevel: Optional[RiskLevel] = None
    riskConfidence: Optional[float] = None
    urgency: Optional[str] = None
    dataQualityScore: Optional[float] = None
    biasStatus: Optional[str] = None
    humanReviewRequired: Optional[bool] = None
    humanReviewReason: Optional[str] = None
    structuredFields: Optional[dict] = None
    missingFieldHistory: Optional[list] = None
    reporterType: Optional[str] = None
    followUpRound: int = 0
    createdAt: str = ""
    updatedAt: str = ""

    def to_dynamo(self) -> dict:
        item = self.model_dump(exclude_none=True)
        if self.riskConfidence is not None:
            item["riskConfidence"] = str(self.riskConfidence)
        if self.dataQualityScore is not None:
            item["dataQualityScore"] = str(self.dataQualityScore)
        return item

    @classmethod
    def from_dynamo(cls, item: dict) -> "IntakeCase":
        if "riskConfidence" in item and isinstance(item["riskConfidence"], str):
            item["riskConfidence"] = float(item["riskConfidence"])
        if "dataQualityScore" in item and isinstance(item["dataQualityScore"], str):
            item["dataQualityScore"] = float(item["dataQualityScore"])
        return cls(**item)
