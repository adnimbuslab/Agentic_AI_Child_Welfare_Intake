"""MCP-003: Case History MCP Server — prior referrals, history, and duplicate search."""

from backend.db import get_table, deserialize_from_dynamo


def get_prior_referrals(child_name: str | None = None, child_dob: str | None = None) -> dict:
    """MCP-003-T1: Retrieve prior referral records."""
    cases = search_existing_cases()
    matching = []
    for case in cases:
        sf = case.get("structuredFields") or {}
        if not sf:
            continue
        cn = sf.get("childName", {})
        name_val = (cn.get("value") if isinstance(cn, dict) else cn) or ""
        if child_name and child_name.lower() in name_val.lower():
            matching.append({
                "caseId": case.get("caseId"),
                "childName": name_val,
                "status": case.get("status"),
                "riskLevel": case.get("riskLevel"),
            })
    return {
        "referrals": matching,
        "totalCount": len(matching),
    }


def get_case_history(child_name: str | None = None, child_dob: str | None = None) -> dict:
    """MCP-003-T2: Retrieve full prior case history."""
    cases = search_existing_cases()
    return {
        "cases": cases,
        "totalCount": len(cases),
    }


def get_household_history(address: str | None = None, guardian_name: str | None = None) -> dict:
    """MCP-003-T3: Retrieve household instability history. POC returns empty."""
    return {
        "incidents": [],
        "instabilityScore": 0.0,
        "message": "No household history found (POC stub).",
    }


def search_existing_cases() -> list[dict]:
    """Scan IntakeCases for all cases that have structuredFields populated."""
    table = get_table("IntakeCases")
    items = []
    resp = table.scan(
        FilterExpression="attribute_exists(structuredFields)",
    )
    items.extend(resp.get("Items", []))
    while "LastEvaluatedKey" in resp:
        resp = table.scan(
            FilterExpression="attribute_exists(structuredFields)",
            ExclusiveStartKey=resp["LastEvaluatedKey"],
        )
        items.extend(resp.get("Items", []))
    return [deserialize_from_dynamo(item) for item in items]
