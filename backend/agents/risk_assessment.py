"""AR-002: Risk Assessment Agent — evaluates child vulnerability and assigns risk level."""

import json
from backend.llm_factory import invoke_llm
from backend.config import CONFIDENCE_THRESHOLD_RISK, DATA_QUALITY_THRESHOLD

SYSTEM_PROMPT = """You are the Risk Assessment Agent for a child welfare intake system.

Your job is to evaluate child vulnerability using structured intake data and assign a risk level.

Consider these factors:
- Type of concern
- Age of child (children under 5 are higher risk)
- Severity of alleged harm
- Urgency indicators
- Prior history
- Reporter credibility/context
- Household instability indicators
- Missing critical information
- Immediate safety concerns

Risk Levels:
- Critical: Immediate danger. Response within hours.
- High: Significant concern. Response within 24 hours.
- Medium: Moderate concern. Response within 72 hours.
- Low: Low concern. Routine follow-up.

ESCALATION RULES — set escalate=true if:
- Your confidenceScore < 0.6
- riskLevel is "Critical" (ALWAYS escalate Critical, regardless of confidence)
- riskLevel is "High" AND dataQualityScore < 0.5
- Immediate safety concern detected but data completeness is poor

Return your response as valid JSON:
{
  "riskLevel": "Low|Medium|High|Critical",
  "confidenceScore": 0.0,
  "urgency": "string describing urgency",
  "riskFactors": ["list of contributing factors"],
  "escalate": false,
  "escalationReason": "string or null"
}

Return ONLY valid JSON."""


def run(structured_fields: dict, data_quality_score: float = 0.0, document_summaries: list[str] | None = None) -> dict:
    user_content = f"Structured intake fields:\n{json.dumps(structured_fields, indent=2)}\n"
    user_content += f"\nData quality score: {data_quality_score}\n"

    if document_summaries:
        user_content += "\nDocument summaries:\n"
        for s in document_summaries:
            user_content += f"- {s}\n"

    user_content += "\nAssess the risk level, provide contributing factors, and determine urgency."

    raw = invoke_llm(
        system_prompt=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": user_content}],
    )

    try:
        cleaned = raw.strip()
        if cleaned.startswith("```"):
            cleaned = cleaned.split("\n", 1)[1]
            if cleaned.endswith("```"):
                cleaned = cleaned[:-3]
        result = json.loads(cleaned)
    except (json.JSONDecodeError, IndexError):
        result = {
            "riskLevel": "Medium",
            "confidenceScore": 0.4,
            "urgency": "Within 72 hours — unable to parse full assessment",
            "riskFactors": ["Assessment parsing failed — defaulting to Medium"],
            "escalate": True,
            "escalationReason": "Failed to parse LLM risk assessment response",
        }

    risk_level = result.get("riskLevel", "Medium")
    confidence = result.get("confidenceScore", 0.0)

    if risk_level == "Critical":
        result["escalate"] = True
        result["escalationReason"] = result.get("escalationReason") or "Critical risk cases always require human review"

    if confidence < CONFIDENCE_THRESHOLD_RISK:
        result["escalate"] = True
        result["escalationReason"] = result.get("escalationReason") or f"Risk confidence {confidence} below threshold {CONFIDENCE_THRESHOLD_RISK}"

    if risk_level == "High" and data_quality_score < DATA_QUALITY_THRESHOLD:
        result["escalate"] = True
        result["escalationReason"] = result.get("escalationReason") or f"High risk with low data quality ({data_quality_score})"

    return result
