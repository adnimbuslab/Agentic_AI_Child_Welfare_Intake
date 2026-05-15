"""Duplicate Case Detector — weighted fuzzy matching to find existing cases for the same child."""

import re
from backend.llm_factory import invoke_llm, parse_llm_json

MATCH_WEIGHTS = {
    "ssn": 0.30,
    "child_name": 0.20,
    "child_dob": 0.20,
    "guardian_name": 0.10,
    "address": 0.10,
    "child_age": 0.05,
    "contact": 0.05,
}

# When SSN is missing from both records, redistribute its weight proportionally
SSN_REDISTRIBUTION = {
    "child_name": 0.30,
    "child_dob": 0.30,
    "guardian_name": 0.15,
    "address": 0.15,
    "child_age": 0.05,
    "contact": 0.05,
}

CONFIDENCE_HIGH = 0.75
CONFIDENCE_AUTO = 0.90

LLM_MATCH_PROMPT = """You are a record-matching assistant for a child welfare system.

Compare the NEW intake record against each EXISTING case record. For each existing case, determine how likely they refer to the SAME CHILD.

Score each field match from 0.0 to 1.0:
- 1.0 = exact or near-exact match
- 0.7-0.9 = likely the same (e.g., "Emma Johnson" vs "Emma M. Johnson", or "142 Oak St" vs "142 Oak Street")
- 0.3-0.6 = partial match (e.g., same first name different last name, same street different city)
- 0.0 = no match or field missing

Return ONLY valid JSON array. One object per existing case:
[
  {
    "existingCaseId": "CW-YYYY-NNNN",
    "fieldScores": {
      "ssn": 0.0,
      "child_name": 0.0,
      "child_dob": 0.0,
      "child_age": 0.0,
      "guardian_name": 0.0,
      "address": 0.0,
      "contact": 0.0
    },
    "reasoning": "one sentence explaining why this is or isn't a match"
  }
]

If no existing cases are provided, return an empty array: []
Return ONLY valid JSON."""


def _get_field_value(fields: dict, key: str) -> str | None:
    field = fields.get(key, {})
    if isinstance(field, dict):
        return field.get("value")
    return field


def _normalize(val: str | None) -> str:
    if val is None:
        return ""
    return re.sub(r'\s+', ' ', str(val)).strip().lower()


def _normalize_date(val: str | None) -> str:
    if val is None:
        return ""
    s = re.sub(r'[,\-/.]', ' ', str(val)).strip().lower()
    return re.sub(r'\s+', ' ', s)


def _simple_similarity(a: str | None, b: str | None) -> float:
    """Quick string similarity without LLM — used as pre-filter."""
    a_norm = _normalize(a)
    b_norm = _normalize(b)
    if not a_norm or not b_norm:
        return 0.0
    if a_norm == b_norm:
        return 1.0
    if a_norm in b_norm or b_norm in a_norm:
        return 0.8
    a_words = set(a_norm.split())
    b_words = set(b_norm.split())
    if not a_words or not b_words:
        return 0.0
    overlap = len(a_words & b_words) / max(len(a_words), len(b_words))
    return round(overlap, 2)


def _compute_weighted_score(field_scores: dict) -> float:
    ssn_score = field_scores.get("ssn") or 0.0
    if ssn_score > 0:
        weights = MATCH_WEIGHTS
    else:
        weights = SSN_REDISTRIBUTION
    total = 0.0
    for field, weight in weights.items():
        score = field_scores.get(field) or 0.0
        total += weight * float(score)
    return round(total, 3)


def pre_filter_candidates(new_fields: dict, existing_cases: list[dict]) -> list[dict]:
    """Fast pre-filter: keep cases with at least one meaningful field overlap."""
    new_name = _normalize(_get_field_value(new_fields, "childName"))
    new_dob = _normalize_date(_get_field_value(new_fields, "childDob"))
    new_ssn = _normalize(_get_field_value(new_fields, "childSsn"))

    candidates = []
    for case in existing_cases:
        sf = case.get("structuredFields") or {}
        if not sf:
            continue

        if new_ssn:
            existing_ssn = _normalize(_get_field_value(sf, "childSsn"))
            if existing_ssn and new_ssn == existing_ssn:
                candidates.append(case)
                continue

        existing_name = _normalize(_get_field_value(sf, "childName"))
        existing_dob = _normalize_date(_get_field_value(sf, "childDob"))

        name_sim = _simple_similarity(new_name, existing_name)
        dob_match = 1.0 if (new_dob and existing_dob and new_dob == existing_dob) else 0.0

        if name_sim >= 0.5 or (name_sim > 0 and dob_match > 0):
            candidates.append(case)

    return candidates


def _build_comparison_prompt(new_fields: dict, candidates: list[dict]) -> str:
    def format_record(fields: dict) -> str:
        parts = []
        for key in ["childName", "childDob", "childAge", "childSsn", "guardianInfo", "address", "contactDetails"]:
            val = _get_field_value(fields, key)
            if val is not None:
                parts.append(f"  {key}: {val}")
        return "\n".join(parts) if parts else "  (no fields)"

    text = "NEW INTAKE RECORD:\n"
    text += format_record(new_fields) + "\n\n"
    text += "EXISTING CASE RECORDS:\n"

    for case in candidates:
        cid = case.get("caseId", "?")
        sf = case.get("structuredFields", {})
        text += f"\n--- {cid} ---\n"
        text += format_record(sf) + "\n"

    text += "\nCompare the new record against each existing case and score field-by-field."
    return text


def find_duplicates(new_fields: dict, existing_cases: list[dict], current_case_id: str | None = None) -> list[dict]:
    """Find potential duplicate cases using weighted fuzzy matching.

    Returns list of matches sorted by confidence (highest first).
    Each match: { caseId, confidence, fieldScores, reasoning, confirmationRequired }
    """
    filtered = [c for c in existing_cases if c.get("caseId") != current_case_id]
    candidates = pre_filter_candidates(new_fields, filtered)

    if not candidates:
        return []

    prompt_text = _build_comparison_prompt(new_fields, candidates)

    try:
        raw = invoke_llm(
            system_prompt=LLM_MATCH_PROMPT,
            messages=[{"role": "user", "content": prompt_text}],
        )
        llm_results = parse_llm_json(raw)
    except Exception:
        llm_results = _fallback_scoring(new_fields, candidates)

    if isinstance(llm_results, dict):
        llm_results = [llm_results]

    matches = []
    for item in llm_results:
        field_scores = item.get("fieldScores", {})
        confidence = _compute_weighted_score(field_scores)

        if confidence < 0.15:
            continue

        case_id = item.get("existingCaseId", "?")
        matches.append({
            "caseId": case_id,
            "confidence": confidence,
            "fieldScores": field_scores,
            "reasoning": item.get("reasoning", ""),
            "confirmationRequired": CONFIDENCE_HIGH <= confidence < CONFIDENCE_AUTO,
            "autoMatch": confidence >= CONFIDENCE_AUTO,
        })

    matches.sort(key=lambda x: x["confidence"], reverse=True)
    return matches


def _fallback_scoring(new_fields: dict, candidates: list[dict]) -> list:
    """Score without LLM if the LLM call fails."""
    results = []
    for case in candidates:
        sf = case.get("structuredFields", {})
        scores = {
            "ssn": 1.0 if (_normalize(_get_field_value(new_fields, "childSsn"))
                           and _normalize(_get_field_value(new_fields, "childSsn")) == _normalize(_get_field_value(sf, "childSsn")))
                   else 0.0,
            "child_name": _simple_similarity(_get_field_value(new_fields, "childName"), _get_field_value(sf, "childName")),
            "child_dob": 1.0 if _normalize_date(_get_field_value(new_fields, "childDob")) == _normalize_date(_get_field_value(sf, "childDob")) and _normalize_date(_get_field_value(new_fields, "childDob")) else 0.0,
            "child_age": 1.0 if _get_field_value(new_fields, "childAge") == _get_field_value(sf, "childAge") and _get_field_value(new_fields, "childAge") is not None else 0.0,
            "guardian_name": _simple_similarity(_get_field_value(new_fields, "guardianInfo"), _get_field_value(sf, "guardianInfo")),
            "address": _simple_similarity(_get_field_value(new_fields, "address"), _get_field_value(sf, "address")),
            "contact": _simple_similarity(_get_field_value(new_fields, "contactDetails"), _get_field_value(sf, "contactDetails")),
        }
        results.append({
            "existingCaseId": case.get("caseId"),
            "fieldScores": scores,
            "reasoning": "Scored using fallback string matching",
        })
    return results
