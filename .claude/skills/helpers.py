"""
Helpers for Claude Code skills in the Child Welfare Intake project.
Provides utilities for test validation, requirement tracing, and LocalStack checks.
"""

import json
import re
from typing import Optional


REQUIREMENT_PREFIXES = ["BR", "FR", "AR", "HITL", "API", "MCP", "DB", "FE", "NFR", "WF", "DEP", "TEST"]
CASE_ID_PATTERN = re.compile(r"^CW-\d{4}-\d{4}$")
VALID_RISK_LEVELS = {"Low", "Medium", "High", "Critical"}
VALID_CASE_STATUSES = {
    "IN_PROGRESS",
    "READY_FOR_CASEWORKER_REVIEW",
    "NEEDS_MORE_INFORMATION",
    "ESCALATED_TO_SUPERVISOR",
    "CRITICAL_IMMEDIATE_REVIEW",
    "BIAS_REVIEW_REQUIRED",
    "LOW_CONFIDENCE_REVIEW_REQUIRED",
}
VALID_AGENT_NAMES = {
    "intake-understanding",
    "risk-assessment",
    "data-quality",
    "bias-monitoring",
    "explanation",
}


def validate_case_id(case_id: str) -> bool:
    return bool(CASE_ID_PATTERN.match(case_id))


def validate_risk_level(level: str) -> bool:
    return level in VALID_RISK_LEVELS


def validate_case_status(status: str) -> bool:
    return status in VALID_CASE_STATUSES


def validate_confidence_score(score: float) -> bool:
    return isinstance(score, (int, float)) and 0.0 <= score <= 1.0


def validate_agent_output_shape(agent_name: str, output: dict) -> list[str]:
    errors = []
    if agent_name not in VALID_AGENT_NAMES:
        errors.append(f"Unknown agent name: {agent_name}")
        return errors

    required_keys = {
        "intake-understanding": ["structuredFields", "missingRequiredFields", "followUpQuestions", "overallConfidenceScore", "escalate"],
        "risk-assessment": ["riskLevel", "confidenceScore", "urgency", "riskFactors", "escalate"],
        "data-quality": ["dataQualityScore", "missingCriticalFields", "inconsistencies", "readyForReview", "escalate"],
        "bias-monitoring": ["biasStatus", "biasConfidence", "flags", "humanReviewRequired"],
        "explanation": ["caseworkerSummary", "riskExplanation", "recommendation", "limitations", "nextAction", "finalCaseStatus"],
    }

    for key in required_keys.get(agent_name, []):
        if key not in output:
            errors.append(f"Missing required key '{key}' in {agent_name} output")

    return errors


def extract_requirement_ids(text: str) -> list[str]:
    pattern = re.compile(r"\b(" + "|".join(REQUIREMENT_PREFIXES) + r")-\d{3}\b")
    return sorted(set(pattern.findall(text) if not pattern.findall(text) else [m.group() for m in pattern.finditer(text)]))


def format_localstack_endpoint(service: str, endpoint_url: Optional[str] = None) -> str:
    base = endpoint_url or "http://localhost:4566"
    return base
