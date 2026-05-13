"""Category A — Session & API Layer tests (TEST-001, TEST-016 through TEST-020)."""

import re


def test_001_session_creation_happy_path(client):
    """TEST-001: Session creation happy path.
    Traces To: API-001, DB-001, FR-001
    """
    res = client.post("/intake/session", json={"reporterType": "teacher"})
    assert res.status_code == 200
    data = res.json()
    assert "caseId" in data
    assert re.match(r"^CW-\d{4}-\d{4}$", data["caseId"])
    assert "sessionToken" in data
    assert "createdAt" in data


def test_016_session_creation_missing_reporter_type(client):
    """TEST-016: Missing reporterType returns HTTP 400.
    Traces To: API-001, NFR-005
    """
    res = client.post("/intake/session", json={})
    assert res.status_code == 422 or res.status_code == 400


def test_017_session_creation_malformed_json(client):
    """TEST-017: Malformed JSON returns HTTP 400/422.
    Traces To: API-001
    """
    res = client.post("/intake/session", content=b"not-json", headers={"Content-Type": "application/json"})
    assert res.status_code in (400, 422)


def test_018_case_id_uniqueness(client):
    """TEST-018: Two sessions produce unique case IDs.
    Traces To: FR-001, DB-001
    """
    r1 = client.post("/intake/session", json={"reporterType": "teacher"})
    r2 = client.post("/intake/session", json={"reporterType": "nurse"})
    assert r1.status_code == 200
    assert r2.status_code == 200
    assert r1.json()["caseId"] != r2.json()["caseId"]


def test_019_submit_message_nonexistent_case(client):
    """TEST-019: Message to non-existent case returns 404.
    Traces To: API-002
    """
    res = client.post("/intake/message", json={
        "caseId": "CW-0000-9999",
        "messageText": "test message",
    })
    assert res.status_code == 404


def test_020_submit_message_to_completed_case(client):
    """TEST-020: Message to completed case returns 409.
    Traces To: API-002, FR-010
    """
    session = client.post("/intake/session", json={"reporterType": "teacher"})
    case_id = session.json()["caseId"]

    from backend.mcp_servers.intake_server import update_intake_case
    update_intake_case(case_id, {"status": "READY_FOR_CASEWORKER_REVIEW"})

    res = client.post("/intake/message", json={
        "caseId": case_id,
        "messageText": "late message",
    })
    assert res.status_code == 409
