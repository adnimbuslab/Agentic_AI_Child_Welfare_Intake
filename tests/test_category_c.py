"""Category C — Document Upload tests (TEST-004, TEST-026 through TEST-031)."""

import io


def test_004_file_upload_happy_path(client):
    """TEST-004: File upload happy path.
    Traces To: FR-002, API-003, DB-003
    """
    session = client.post("/intake/session", json={"reporterType": "teacher"})
    case_id = session.json()["caseId"]

    file_content = b"This is a test text document with intake information."
    res = client.post("/intake/upload", data={
        "caseId": case_id,
        "documentCategory": "incident-report",
    }, files={"file": ("test_report.txt", io.BytesIO(file_content), "text/plain")})

    assert res.status_code == 200
    data = res.json()
    assert "documentId" in data
    assert data["fileName"] == "test_report.txt"
    assert data["extractionStatus"] in ("pending", "complete")


def test_026_upload_to_nonexistent_case(client):
    """TEST-026: Upload to non-existent case returns 404.
    Traces To: API-003
    """
    res = client.post("/intake/upload", data={
        "caseId": "CW-0000-9999",
        "documentCategory": "other",
    }, files={"file": ("doc.txt", io.BytesIO(b"data"), "text/plain")})
    assert res.status_code == 404


def test_027_upload_unsupported_file_type(client):
    """TEST-027: Unsupported file type (.exe) returns 400.
    Traces To: API-003, BR-002
    """
    session = client.post("/intake/session", json={"reporterType": "teacher"})
    case_id = session.json()["caseId"]

    res = client.post("/intake/upload", data={
        "caseId": case_id,
        "documentCategory": "other",
    }, files={"file": ("malware.exe", io.BytesIO(b"\x00\x01"), "application/octet-stream")})
    assert res.status_code == 400


def test_028_upload_zero_byte_file(client):
    """TEST-028: Zero-byte file returns 400.
    Traces To: API-003
    """
    session = client.post("/intake/session", json={"reporterType": "teacher"})
    case_id = session.json()["caseId"]

    res = client.post("/intake/upload", data={
        "caseId": case_id,
        "documentCategory": "other",
    }, files={"file": ("empty.txt", io.BytesIO(b""), "text/plain")})
    assert res.status_code == 400


def test_031_upload_after_final_status(client):
    """TEST-031: Upload after case reaches final status returns 409.
    Traces To: API-003, FR-010
    """
    session = client.post("/intake/session", json={"reporterType": "teacher"})
    case_id = session.json()["caseId"]

    from backend.mcp_servers.intake_server import update_intake_case
    update_intake_case(case_id, {"status": "READY_FOR_CASEWORKER_REVIEW"})

    res = client.post("/intake/upload", data={
        "caseId": case_id,
        "documentCategory": "other",
    }, files={"file": ("doc.txt", io.BytesIO(b"data"), "text/plain")})
    assert res.status_code == 409
