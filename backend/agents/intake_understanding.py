"""AR-001: Intake Understanding Agent — extracts structured fields from unstructured input."""

import json
from backend.llm_factory import invoke_llm, parse_llm_json
from backend.config import CONFIDENCE_THRESHOLD_INTAKE

SYSTEM_PROMPT = """You are the Intake Understanding Agent for a child welfare intake system.

Your job is to extract structured intake fields from unstructured reporter narratives and document texts.

INSTRUCTIONS:
1. Read the reporter's message carefully. Extract every piece of information into the correct field.
2. For each field you extract, assign a confidence score between 0.0 and 1.0.
3. A field is "present" if any relevant information was provided, even partially.
4. Only list a field in missingRequiredFields if NO information at all was provided for it.
5. Generate follow-up questions ONLY for truly missing fields — max 3 per turn.
6. If reporter says "I don't know" for a field, set value to null and do NOT ask about it again.
7. If reporter says they don't want to give their name or wishes to remain anonymous, set reporterInfo value to null or empty string. Do NOT set it to their statement.

Required fields: childName, childDob, childAge, guardianInfo, reporterInfo, reporterRelationship, contactDetails, address, concernType, incidentDescription
Optional fields: urgencyIndicators, priorConcerns

ESCALATION RULES — you MUST set escalate=true if ANY of these are true:
- The reporter provides CONFLICTING information (e.g., says child is 5 years old AND 16 years old)
- You cannot parse the narrative at all (overallConfidenceScore < 0.3)
- Document extraction confidence is critically low (< 0.4) across all documents
- Urgent danger signals present but child identity AND location are both missing

CONFLICT DETECTION: If the reporter states two different values for the same field (different ages, different names, contradictory descriptions), this is conflicting information and you MUST escalate.

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
        result = parse_llm_json(raw)
    except (json.JSONDecodeError, IndexError, ValueError):
        result = _fallback_result()
        result["escalate"] = True
        result["escalationReason"] = "Failed to parse LLM response"

    result = _post_process(result, session_messages)

    if result.get("overallConfidenceScore", 0) < CONFIDENCE_THRESHOLD_INTAKE:
        result["escalate"] = True
        if not result.get("escalationReason"):
            result["escalationReason"] = f"Overall confidence {result.get('overallConfidenceScore', 0)} below threshold {CONFIDENCE_THRESHOLD_INTAKE}"

    return result


def _post_process(result: dict, session_messages: list[dict]) -> dict:
    raw_questions = result.get("followUpQuestions", [])
    normalized = []
    for q in raw_questions:
        if isinstance(q, dict):
            normalized.append(q.get("question", q.get("text", str(q))))
        else:
            normalized.append(str(q))
    result["followUpQuestions"] = normalized

    fields = result.get("structuredFields", {})

    reporter_info = fields.get("reporterInfo", {})
    reporter_val = reporter_info.get("value") if isinstance(reporter_info, dict) else reporter_info
    if reporter_val and isinstance(reporter_val, str):
        anon_phrases = ["don't want to give", "anonymous", "don't want to share", "prefer not", "wish not"]
        if any(p in reporter_val.lower() for p in anon_phrases):
            if isinstance(reporter_info, dict):
                fields["reporterInfo"]["value"] = None
            else:
                fields["reporterInfo"] = None

    user_text = " ".join(m.get("content", "") for m in session_messages if m.get("role") == "user").lower()
    if _detect_conflicts(user_text):
        result["escalate"] = True
        if not result.get("escalationReason"):
            result["escalationReason"] = "Conflicting information detected in reporter narrative"

    missing = result.get("missingRequiredFields", [])
    required = ["childName", "childDob", "childAge", "guardianInfo", "reporterInfo",
                 "reporterRelationship", "contactDetails", "address", "concernType", "incidentDescription"]
    cleaned_missing = []
    for field_name in missing:
        field_data = fields.get(field_name, {})
        val = field_data.get("value") if isinstance(field_data, dict) else field_data
        if val is None or val == "" or val == []:
            cleaned_missing.append(field_name)
    result["missingRequiredFields"] = cleaned_missing

    result["structuredFields"] = fields
    return result


def _detect_conflicts(text: str) -> bool:
    import re
    ages = re.findall(r'(?:is|age[d]?)\s+(\d{1,2})\s*(?:year|yr)', text)
    ages += re.findall(r'(\d{1,2})-year-old', text)
    if len(set(ages)) > 1:
        return True
    return False


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
