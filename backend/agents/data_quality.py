"""AR-003: Data Quality Agent — validates completeness, consistency, and readiness."""

import json
from backend.llm_factory import invoke_llm, parse_llm_json
from backend.config import DATA_QUALITY_THRESHOLD

SYSTEM_PROMPT = """You are the Data Quality Agent for a child welfare intake system.

Your job is to validate whether the structured intake data is complete, consistent, and usable.

Check for:
- Required field presence (childName, childDob, childAge, guardianInfo, reporterInfo, reporterRelationship, contactDetails, address, concernType, incidentDescription)
- Value conflicts (e.g., reported age vs. DOB mismatch)
- Age/DOB consistency
- Document readability
- Extracted value reliability
- Critical field completeness
- Case readiness for caseworker review

ESCALATION RULES — set escalate=true if:
- Any critical field still missing AND reporter has already been asked
- dataQualityScore < 0.5 after follow-up rounds
- Documents contradict user-provided information in a critical field
- Identity or relationship cannot be verified from any submitted source

Return your response as valid JSON:
{
  "dataQualityScore": 0.0,
  "missingCriticalFields": [],
  "inconsistencies": [{"field": "fieldName", "detail": "description"}],
  "readyForReview": true,
  "escalate": false,
  "escalationReason": "string or null"
}

Return ONLY valid JSON."""


def run(
    structured_fields: dict,
    intake_messages: list[dict] | None = None,
    document_extraction_results: list[dict] | None = None,
    follow_up_round: int = 0,
) -> dict:
    user_content = f"Structured fields:\n{json.dumps(structured_fields, indent=2)}\n"
    user_content += f"\nFollow-up round: {follow_up_round}\n"

    if intake_messages:
        user_content += f"\nMessage count: {len(intake_messages)}\n"

    if document_extraction_results:
        user_content += f"\nDocument extraction results: {len(document_extraction_results)} documents\n"
        for doc in document_extraction_results:
            user_content += f"- {doc.get('fileName', 'unknown')}: status={doc.get('extractionStatus', 'unknown')}\n"

    user_content += "\nValidate completeness, detect inconsistencies, and determine if the case is ready for review."

    raw = invoke_llm(
        system_prompt=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": user_content}],
    )

    try:
        result = parse_llm_json(raw)
    except (json.JSONDecodeError, IndexError, ValueError):
        result = {
            "dataQualityScore": 0.3,
            "missingCriticalFields": ["unknown — parsing failed"],
            "inconsistencies": [],
            "readyForReview": False,
            "escalate": True,
            "escalationReason": "Failed to parse data quality assessment",
        }

    quality_score = result.get("dataQualityScore", 0.0)

    if quality_score < DATA_QUALITY_THRESHOLD and follow_up_round > 0:
        result["escalate"] = True
        result["escalationReason"] = result.get("escalationReason") or f"Data quality {quality_score} below threshold after {follow_up_round} follow-up rounds"

    return result
