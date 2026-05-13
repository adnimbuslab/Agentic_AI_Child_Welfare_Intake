"""MCP-007: Knowledge / Policy MCP Server — rules, thresholds, and policies."""

from backend.config import (
    CONFIDENCE_THRESHOLD_INTAKE,
    CONFIDENCE_THRESHOLD_RISK,
    CONFIDENCE_THRESHOLD_BIAS,
    DATA_QUALITY_THRESHOLD,
)


def get_intake_required_fields() -> dict:
    """MCP-007-T1: Return list of mandatory intake fields."""
    return {
        "requiredFields": [
            "childName",
            "childDob",
            "childAge",
            "guardianInfo",
            "reporterInfo",
            "reporterRelationship",
            "contactDetails",
            "address",
            "concernType",
            "incidentDescription",
        ],
        "criticalFields": [
            "childName",
            "concernType",
            "incidentDescription",
        ],
        "optionalFields": [
            "urgencyIndicators",
            "priorConcerns",
        ],
    }


def get_mandatory_reporting_rules() -> dict:
    """MCP-007-T2: Return mandatory reporting compliance rules."""
    return {
        "rules": [
            "All suspected child abuse or neglect must be reported.",
            "Reporter identity is encouraged but not required to proceed.",
            "Immediate danger cases must be flagged as Critical.",
            "Cases involving children under 5 require heightened scrutiny.",
            "Prior referral history must be checked when available.",
        ]
    }


def get_risk_policy_guidelines() -> dict:
    """MCP-007-T3: Return risk assessment policy thresholds."""
    return {
        "riskLevels": {
            "Critical": "Immediate danger to child safety. Requires within-hours response.",
            "High": "Significant concern. Requires response within 24 hours.",
            "Medium": "Moderate concern. Requires response within 72 hours.",
            "Low": "Low concern. Routine follow-up.",
        },
        "confidenceThreshold": CONFIDENCE_THRESHOLD_RISK,
        "criticalAlwaysEscalate": True,
        "highWithPoorDataEscalate": True,
        "dataQualityThresholdForHigh": DATA_QUALITY_THRESHOLD,
        "factorsToConsider": [
            "type of concern",
            "age of child",
            "severity of alleged harm",
            "urgency indicators",
            "prior history",
            "reporter credibility/context",
            "household instability indicators",
            "missing critical information",
            "immediate safety concerns",
        ],
    }


def get_bias_monitoring_policy() -> dict:
    """MCP-007-T4: Return bias detection rules and sensitive attributes."""
    return {
        "sensitiveAttributes": [
            "race",
            "ethnicity",
            "religion",
            "nationality",
            "language",
            "socioeconomic status",
            "neighborhood",
            "housing type",
            "immigration status",
        ],
        "biasChecks": [
            "demographic over-reliance",
            "location-based bias",
            "reporter bias",
            "language bias",
            "socioeconomic proxy bias",
            "unfair risk amplification",
            "inconsistent treatment of similar cases",
        ],
        "confidenceThreshold": CONFIDENCE_THRESHOLD_BIAS,
        "flaggedAlwaysEscalate": True,
    }


def get_human_review_policy() -> dict:
    """MCP-007-T5: Return conditions that trigger human review."""
    return {
        "triggers": [
            {
                "stage": "post-intake",
                "conditions": [
                    f"overallConfidenceScore < {CONFIDENCE_THRESHOLD_INTAKE}",
                    "document extraction confidence < 0.4 across all documents",
                    "uploaded documents are unreadable",
                    "reporter provides directly conflicting critical information",
                    "urgent danger but child identity and location both missing",
                ],
            },
            {
                "stage": "post-risk",
                "conditions": [
                    f"confidenceScore < {CONFIDENCE_THRESHOLD_RISK}",
                    "riskLevel == Critical (always)",
                    f"riskLevel == High AND dataQualityScore < {DATA_QUALITY_THRESHOLD}",
                    "immediate safety concern with poor data completeness",
                ],
            },
            {
                "stage": "post-quality",
                "conditions": [
                    "critical field still missing after reporter follow-up",
                    f"dataQualityScore < {DATA_QUALITY_THRESHOLD} after follow-up",
                    "documents contradict user information on critical field",
                    "identity or relationship unverifiable",
                ],
            },
            {
                "stage": "post-bias",
                "conditions": [
                    "biasStatus == Flagged (always)",
                    f"biasConfidence < {CONFIDENCE_THRESHOLD_BIAS}",
                    "sensitive attribute in primary risk factor list",
                ],
            },
        ]
    }
