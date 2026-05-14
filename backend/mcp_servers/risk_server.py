"""MCP-004: Risk Assessment MCP Server — risk scoring and persistence."""

import uuid
from datetime import datetime, timezone
from backend.db import get_table, sanitize_for_dynamo
from backend.config import CONFIDENCE_THRESHOLD_RISK


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def calculate_risk_score(structured_fields: dict, data_quality_score: float = 0.0) -> dict:
    """MCP-004-T1: Invoke risk scoring logic. Returns structured risk factors for agent to evaluate."""
    concern_type = ""
    child_age = None
    urgency_indicators = []

    if structured_fields:
        ct = structured_fields.get("concernType", {})
        concern_type = (ct.get("value") or "") if isinstance(ct, dict) else str(ct or "")
        age_field = structured_fields.get("childAge", {})
        age_val = age_field.get("value") if isinstance(age_field, dict) else age_field
        if age_val is not None:
            try:
                child_age = int(age_val)
            except (ValueError, TypeError):
                pass
        urg = structured_fields.get("urgencyIndicators", {})
        urgency_indicators = urg.get("value", []) if isinstance(urg, dict) else []

    risk_factors = []
    score = 0.0

    harm_keywords = ["physical", "harm", "abuse", "injury", "violence", "assault", "sexual"]
    if any(kw in concern_type.lower() for kw in harm_keywords):
        risk_factors.append("Physical/sexual harm indicators present")
        score += 0.3

    if child_age is not None and child_age < 5:
        risk_factors.append(f"Child is under 5 years old (age: {child_age})")
        score += 0.2

    if urgency_indicators:
        risk_factors.append(f"Urgency indicators: {', '.join(urgency_indicators)}")
        score += 0.15

    neglect_keywords = ["neglect", "hungry", "dirty", "unsupervised", "malnourished"]
    if any(kw in concern_type.lower() for kw in neglect_keywords):
        risk_factors.append("Neglect indicators present")
        score += 0.2

    if data_quality_score < 0.5:
        risk_factors.append("Low data quality may affect assessment accuracy")
        score += 0.05

    score = min(score, 1.0)

    if score >= 0.7:
        risk_level = "Critical"
    elif score >= 0.5:
        risk_level = "High"
    elif score >= 0.3:
        risk_level = "Medium"
    else:
        risk_level = "Low"

    return {
        "calculatedRiskLevel": risk_level,
        "calculatedScore": round(score, 2),
        "riskFactors": risk_factors,
        "inputFieldCount": len(structured_fields) if structured_fields else 0,
    }


def get_risk_thresholds() -> dict:
    """MCP-004-T2: Retrieve configured risk threshold values."""
    return {
        "confidenceThreshold": CONFIDENCE_THRESHOLD_RISK,
        "criticalAlwaysEscalate": True,
        "highWithLowQualityEscalate": True,
        "highQualityThreshold": 0.5,
    }


def save_risk_assessment(case_id: str, risk_output: dict) -> dict:
    """MCP-004-T3: Persist risk assessment output to AgentOutputs."""
    table = get_table("AgentOutputs")
    now = _now()
    item = {
        "caseId": case_id,
        "agentNameTimestamp": f"risk-assessment#{now}#{uuid.uuid4().hex[:8]}",
        "agentName": "risk-assessment",
        "outputJson": risk_output,
        "confidenceScore": str(risk_output.get("confidenceScore", 0)),
        "status": "escalated" if risk_output.get("escalate") else "success",
        "escalationReason": risk_output.get("escalationReason"),
        "createdAt": now,
    }
    item = {k: v for k, v in item.items() if v is not None}
    table.put_item(Item=sanitize_for_dynamo(item))
    return {"saved": True, "caseId": case_id}
