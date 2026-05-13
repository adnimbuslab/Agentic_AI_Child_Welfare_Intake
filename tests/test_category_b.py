"""Category B — Intake Message Submission tests (TEST-021 through TEST-025).
NOTE: TEST-002, TEST-003, TEST-022, TEST-024 require a live LLM and are marked with pytest.mark.llm.
"""

import pytest


def test_021_submit_empty_message(client):
    """TEST-021: Empty message text returns HTTP 400.
    Traces To: API-002
    """
    session = client.post("/intake/session", json={"reporterType": "teacher"})
    case_id = session.json()["caseId"]

    res = client.post("/intake/message", json={
        "caseId": case_id,
        "messageText": "",
    })
    assert res.status_code == 400


def test_025_submit_whitespace_only_message(client):
    """TEST-025: Whitespace-only message returns HTTP 400.
    Traces To: API-002
    """
    session = client.post("/intake/session", json={"reporterType": "teacher"})
    case_id = session.json()["caseId"]

    res = client.post("/intake/message", json={
        "caseId": case_id,
        "messageText": "   \n\t  ",
    })
    assert res.status_code == 400


@pytest.mark.llm
def test_002_structured_field_extraction(client):
    """TEST-002: Structured field extraction happy path.
    Traces To: AR-001, FR-003
    """
    session = client.post("/intake/session", json={"reporterType": "teacher"})
    case_id = session.json()["caseId"]

    res = client.post("/intake/message", json={
        "caseId": case_id,
        "messageText": "I am a teacher. One of my students came to school with visible injury and seemed scared to go home.",
    })
    assert res.status_code == 200
    data = res.json()
    assert "agentResponse" in data
    assert "followUpQuestions" in data


@pytest.mark.llm
def test_003_followup_question_generation(client):
    """TEST-003: Follow-up questions generated for missing fields.
    Traces To: FR-004, AR-001, BR-004
    """
    session = client.post("/intake/session", json={"reporterType": "teacher"})
    case_id = session.json()["caseId"]

    res = client.post("/intake/message", json={
        "caseId": case_id,
        "messageText": "I am a teacher. One of my students came to school with visible injury and seemed scared to go home.",
    })
    assert res.status_code == 200
    data = res.json()
    questions = data.get("followUpQuestions", [])
    assert len(questions) > 0


def test_023_xss_payload_stored_literal(client):
    """TEST-023: XSS payload stored as literal text.
    Traces To: API-002, DB-002
    """
    session = client.post("/intake/session", json={"reporterType": "teacher"})
    case_id = session.json()["caseId"]

    xss = "<script>alert('xss')</script> The child was seen."
    from backend.mcp_servers.intake_server import save_intake_message, get_intake_messages
    save_intake_message(case_id, xss, "user", "narrative")
    messages = get_intake_messages(case_id)
    stored = [m for m in messages if "<script>" in m["messageText"]]
    assert len(stored) == 1
    assert stored[0]["messageText"] == xss
