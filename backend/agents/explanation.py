"""AR-005: Explanation Agent — produces caseworker-facing summary and assigns final status."""

import json
from backend.llm_factory import invoke_llm

SYSTEM_PROMPT = """You are the Explanation Agent for a child welfare intake system.

Your job is to convert technical agent outputs into a plain-language caseworker-facing summary.

Rules:
- Use simple, clear language a caseworker can understand
- Show confidence levels without overstating certainty
- Clearly explain why the risk level was selected
- State whether human review is needed and why
- Avoid diagnostic or overly certain language
- Acknowledge system limitations

Final Case Status — assign exactly one:
- READY_FOR_CASEWORKER_REVIEW: All checks passed, no escalation needed
- NEEDS_MORE_INFORMATION: Critical data still missing
- ESCALATED_TO_SUPERVISOR: Agent flagged for escalation
- CRITICAL_IMMEDIATE_REVIEW: Critical risk level detected
- BIAS_REVIEW_REQUIRED: Bias monitoring flagged the case
- LOW_CONFIDENCE_REVIEW_REQUIRED: Low confidence across agents

IMPORTANT: Never set READY_FOR_CASEWORKER_REVIEW for High or Critical risk cases — they must go through human review.

Return your response as valid JSON:
{
  "caseworkerSummary": "plain language summary paragraph",
  "riskExplanation": ["reason 1", "reason 2"],
  "recommendation": "what should happen next",
  "limitations": ["limitation 1"],
  "nextAction": "specific next step",
  "humanReviewRequired": false,
  "humanReviewReason": "string or null",
  "finalCaseStatus": "one of the six statuses above"
}

Return ONLY valid JSON."""


def run(
    intake_understanding_output: dict,
    risk_assessment_output: dict,
    data_quality_output: dict,
    bias_monitoring_output: dict,
    case_id: str,
) -> dict:
    user_content = f"Case ID: {case_id}\n\n"
    user_content += f"Intake Understanding Output:\n{json.dumps(intake_understanding_output, indent=2)}\n\n"
    user_content += f"Risk Assessment Output:\n{json.dumps(risk_assessment_output, indent=2)}\n\n"
    user_content += f"Data Quality Output:\n{json.dumps(data_quality_output, indent=2)}\n\n"
    user_content += f"Bias Monitoring Output:\n{json.dumps(bias_monitoring_output, indent=2)}\n\n"
    user_content += "Generate the caseworker summary, assign the final case status, and determine if human review is needed."

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
        result = _fallback_explanation(case_id, risk_assessment_output)

    risk_level = risk_assessment_output.get("riskLevel", "")
    if risk_level in ("High", "Critical") and result.get("finalCaseStatus") == "READY_FOR_CASEWORKER_REVIEW":
        result["finalCaseStatus"] = "CRITICAL_IMMEDIATE_REVIEW" if risk_level == "Critical" else "ESCALATED_TO_SUPERVISOR"
        result["humanReviewRequired"] = True
        result["humanReviewReason"] = f"{risk_level} risk cases require human review before finalization"

    if bias_monitoring_output.get("biasStatus") == "Flagged":
        result["finalCaseStatus"] = "BIAS_REVIEW_REQUIRED"
        result["humanReviewRequired"] = True
        result["humanReviewReason"] = result.get("humanReviewReason") or "Bias flagged in risk assessment"

    any_escalated = (
        intake_understanding_output.get("escalate")
        or risk_assessment_output.get("escalate")
        or data_quality_output.get("escalate")
        or bias_monitoring_output.get("humanReviewRequired")
    )
    if any_escalated and result.get("finalCaseStatus") == "READY_FOR_CASEWORKER_REVIEW":
        result["finalCaseStatus"] = "ESCALATED_TO_SUPERVISOR"
        result["humanReviewRequired"] = True

    return result


def _fallback_explanation(case_id: str, risk_output: dict) -> dict:
    risk_level = risk_output.get("riskLevel", "Unknown")
    return {
        "caseworkerSummary": f"Case {case_id} has been assessed with risk level: {risk_level}. Please review the detailed agent outputs for full context.",
        "riskExplanation": risk_output.get("riskFactors", ["Risk factors could not be summarized"]),
        "recommendation": "Review the case details and agent outputs manually.",
        "limitations": ["Explanation generation encountered an error — full agent outputs should be reviewed directly."],
        "nextAction": "Manual review of all agent outputs required.",
        "humanReviewRequired": True,
        "humanReviewReason": "Explanation agent could not generate summary",
        "finalCaseStatus": "ESCALATED_TO_SUPERVISOR",
    }
