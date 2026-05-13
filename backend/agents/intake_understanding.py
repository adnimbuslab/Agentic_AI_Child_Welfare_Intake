"""AR-001: Intake Understanding Agent — extracts structured fields from unstructured input."""

import json
from backend.llm_factory import invoke_llm
from backend.config import CONFIDENCE_THRESHOLD_INTAKE

SYSTEM_PROMPT = """You are the Intake Understanding Agent for a child welfare intake system.

Your job is to extract structured intake fields from unstructured reporter narratives and document texts.

For each field you extract, assign a confidence score between 0.0 and 1.0.
Identify which required fields are still missing.
Generate human-friendly follow-up questions for missing required fields — limit to the 3 most critical per turn.

Required fields: childName, childDob, childAge, guardianInfo, reporterInfo, reporterRelationship, contactDetails, address, concernType, incidentDescription
Optional fields: urgencyIndicators, priorConcerns

ESCALATION RULES — set escalate=true if:
- You cannot parse the narrative at all (overallConfidenceScore < 0.3)
- Document extraction confidence is critically low (< 0.4) across all documents
- Uploaded documents are unreadable
- Reporter provides directly conflicting critical information
- Urgent danger signals present but child identity AND location are both missing

Return your response as valid JSON matching this exact schema:
{
  "structuredFields": {
    "childName": {"value": "string or null", "confidence": 0.0},
    "childDob": {"value": "string or null", "confidence": 0.0},
    "childAge": {"value": "number or null", "confidence": 0.0},
    "guardianInfo": {"value": "string or null", "confidence": 0.0},
    "reporterInfo": {"value": "string or null", "confidence": 0.0},
    "reporterRelationship": {"value": "string or null", "confidence": 0.0},
    "contactDetails": {"value": "string or null", "confidence": 0.0},
    "address": {"value": "string or null", "confidence": 0.0},
    "concernType": {"value": "string or null", "confidence": 0.0},
    "incidentDescription": {"value": "string or null", "confidence": 0.0},
    "urgencyIndicators": {"value": [], "confidence": 0.0},
    "priorConcerns": {"value": "string or null", "confidence": 0.0}
  },
  "missingRequiredFields": [],
  "followUpQuestions": [],
  "overallConfidenceScore": 0.0,
  "escalate": false,
  "escalationReason": null
}

Return ONLY valid JSON. No markdown, no explanation outside the JSON."""


def run(
    session_messages: list[dict],
    extracted_document_texts: list[str] | None = None,
    current_structured_fields: dict | None = None,
) -> dict:
    user_content = "Session messages:\n"
    for msg in session_messages:
        user_content += f"[{msg.get('role', 'user')}]: {msg.get('content', '')}\n"

    if extracted_document_texts:
        user_content += "\nExtracted document texts:\n"
        for i, text in enumerate(extracted_document_texts):
            user_content += f"Document {i+1}: {text[:2000]}\n"

    if current_structured_fields:
        user_content += f"\nCurrently extracted fields:\n{json.dumps(current_structured_fields, indent=2)}\n"

    user_content += "\nExtract all structured fields, identify missing required fields, and generate follow-up questions."

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
        result = _fallback_result()
        result["escalate"] = True
        result["escalationReason"] = "Failed to parse LLM response"

    if result.get("overallConfidenceScore", 0) < CONFIDENCE_THRESHOLD_INTAKE:
        result["escalate"] = True
        if not result.get("escalationReason"):
            result["escalationReason"] = f"Overall confidence {result.get('overallConfidenceScore', 0)} below threshold {CONFIDENCE_THRESHOLD_INTAKE}"

    return result


def _fallback_result() -> dict:
    fields = {}
    for name in [
        "childName", "childDob", "childAge", "guardianInfo", "reporterInfo",
        "reporterRelationship", "contactDetails", "address", "concernType",
        "incidentDescription", "priorConcerns",
    ]:
        fields[name] = {"value": None, "confidence": 0.0}
    fields["urgencyIndicators"] = {"value": [], "confidence": 0.0}

    return {
        "structuredFields": fields,
        "missingRequiredFields": [
            "childName", "childDob", "childAge", "guardianInfo", "reporterInfo",
            "reporterRelationship", "contactDetails", "address", "concernType",
            "incidentDescription",
        ],
        "followUpQuestions": [],
        "overallConfidenceScore": 0.0,
        "escalate": False,
        "escalationReason": None,
    }
