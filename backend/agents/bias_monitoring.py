"""AR-004: Bias Monitoring Agent — checks risk reasoning for fairness."""

import json
from backend.llm_factory import invoke_llm, parse_llm_json
from backend.config import CONFIDENCE_THRESHOLD_BIAS

SYSTEM_PROMPT = """You are the Bias Monitoring Agent for a child welfare intake system.

Your job is to review the risk assessment output and check for unfair bias in the reasoning.

Check for these bias types:
- Demographic over-reliance (race, ethnicity, religion, nationality)
- Location-based bias (neighborhood, zip code used as risk proxy)
- Reporter bias (assumptions based on reporter type)
- Language bias (penalizing non-English speakers)
- Socioeconomic proxy bias (housing, income level as risk factor)
- Unfair risk amplification (compounding bias from multiple factors)
- Inconsistent treatment (similar cases getting different risk levels)

ESCALATION RULES — set humanReviewRequired=true if:
- biasStatus is "Flagged" (ALWAYS escalate flagged cases)
- biasConfidence < 0.7 (cannot confidently confirm fairness)
- Sensitive attribute detected in the primary risk factor list

Return your response as valid JSON:
{
  "biasStatus": "Passed|Flagged",
  "biasConfidence": 0.0,
  "flags": [{"type": "bias type", "detail": "explanation"}],
  "humanReviewRequired": false,
  "escalationReason": "string or null"
}

Return ONLY valid JSON."""


def run(risk_assessment_output: dict, structured_fields: dict, bias_policy: dict | None = None) -> dict:
    user_content = f"Risk assessment output:\n{json.dumps(risk_assessment_output, indent=2)}\n"
    user_content += f"\nStructured intake fields:\n{json.dumps(structured_fields, indent=2)}\n"

    if bias_policy:
        user_content += f"\nBias monitoring policy:\n{json.dumps(bias_policy, indent=2)}\n"

    user_content += "\nReview the risk reasoning for any unfair bias. Check all bias types listed in your instructions."

    raw = invoke_llm(
        system_prompt=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": user_content}],
    )

    try:
        result = parse_llm_json(raw)
    except (json.JSONDecodeError, IndexError, ValueError):
        result = {
            "biasStatus": "Flagged",
            "biasConfidence": 0.0,
            "flags": [{"type": "parsing-error", "detail": "Could not parse bias assessment — flagging for human review"}],
            "humanReviewRequired": True,
            "escalationReason": "Failed to parse bias monitoring response",
        }

    if result.get("biasStatus") == "Flagged":
        result["humanReviewRequired"] = True
        result["escalationReason"] = result.get("escalationReason") or "Bias flagged — requires human review"

    if result.get("biasConfidence", 0.0) < CONFIDENCE_THRESHOLD_BIAS:
        result["humanReviewRequired"] = True
        result["escalationReason"] = result.get("escalationReason") or f"Bias confidence {result.get('biasConfidence', 0)} below threshold {CONFIDENCE_THRESHOLD_BIAS}"

    return result
