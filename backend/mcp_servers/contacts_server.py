"""MCP-002: Contacts MCP Server — contact lookup and validation (POC stubs)."""


def lookup_child_contact(name: str | None = None, dob: str | None = None) -> dict:
    """MCP-002-T1: Look up child contact by name/DOB. POC returns stub."""
    return {
        "found": False,
        "message": "No prior child contact record found (POC stub).",
        "searchCriteria": {"name": name, "dob": dob},
    }


def lookup_guardian_contact(name: str | None = None, address: str | None = None) -> dict:
    """MCP-002-T2: Look up guardian contact. POC returns stub."""
    return {
        "found": False,
        "message": "No prior guardian contact record found (POC stub).",
        "searchCriteria": {"name": name, "address": address},
    }


def lookup_reporter_contact(reporter_id: str | None = None, name: str | None = None) -> dict:
    """MCP-002-T3: Look up reporter contact. POC returns stub."""
    return {
        "found": False,
        "message": "No prior reporter contact record found (POC stub).",
        "searchCriteria": {"reporterId": reporter_id, "name": name},
    }


def validate_contact_information(contact: dict) -> dict:
    """MCP-002-T4: Validate contact record completeness."""
    required = ["name"]
    missing = [f for f in required if not contact.get(f)]
    return {
        "valid": len(missing) == 0,
        "missingFields": missing,
    }
