"""MCP-003: Case History MCP Server — prior referrals and history (POC stubs)."""


def get_prior_referrals(child_name: str | None = None, child_dob: str | None = None) -> dict:
    """MCP-003-T1: Retrieve prior referral records. POC returns empty."""
    return {
        "referrals": [],
        "totalCount": 0,
        "message": "No prior referrals found (POC stub).",
    }


def get_case_history(child_name: str | None = None, child_dob: str | None = None) -> dict:
    """MCP-003-T2: Retrieve full prior case history. POC returns empty."""
    return {
        "cases": [],
        "totalCount": 0,
        "message": "No prior case history found (POC stub).",
    }


def get_household_history(address: str | None = None, guardian_name: str | None = None) -> dict:
    """MCP-003-T3: Retrieve household instability history. POC returns empty."""
    return {
        "incidents": [],
        "instabilityScore": 0.0,
        "message": "No household history found (POC stub).",
    }
