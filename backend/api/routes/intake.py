"""Intake API routes: API-001, API-002, API-003."""

import os
import uuid
from datetime import datetime, timezone
from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from pydantic import BaseModel

from backend.mcp_servers import intake_server, audit_server
from backend.models.intake_case import CaseStatus
from backend.models.intake_document import BLOCKED_EXTENSIONS, IntakeDocument, ExtractionStatus
from backend.workflow.intake_workflow import compile_workflow
from backend.s3 import upload_file
from backend.db import get_table
from backend.config import S3_BUCKET_NAME

router = APIRouter()


class CreateSessionRequest(BaseModel):
    reporterType: str


class SubmitMessageRequest(BaseModel):
    caseId: str
    messageText: str
    attachmentIds: list[str] | None = None


# --- API-001: Create Intake Session ---

@router.post("/session")
def create_session(req: CreateSessionRequest):
    if not req.reporterType or not req.reporterType.strip():
        raise HTTPException(status_code=400, detail="reporterType is required")

    case = intake_server.create_intake_case(req.reporterType.strip())

    audit_server.save_agent_decision(
        case_id=case["caseId"],
        agent_name="system",
        output_json={"action": "session_created", "reporterType": req.reporterType},
    )

    return {
        "caseId": case["caseId"],
        "sessionToken": uuid.uuid4().hex,
        "createdAt": case["createdAt"],
    }


# --- API-002: Submit Intake Message ---

@router.post("/message")
def submit_message(req: SubmitMessageRequest):
    if not req.messageText or not req.messageText.strip():
        raise HTTPException(status_code=400, detail="messageText cannot be empty")

    case = intake_server.get_intake_case(req.caseId)
    if not case:
        raise HTTPException(status_code=404, detail=f"Case {req.caseId} not found")

    if case["status"] != CaseStatus.IN_PROGRESS:
        raise HTTPException(status_code=409, detail=f"Case {req.caseId} is no longer in progress (status: {case['status']})")

    intake_server.save_intake_message(
        case_id=req.caseId,
        message_text=req.messageText,
        sender_type="user",
        message_type="narrative" if case.get("followUpRound", 0) == 0 else "follow-up-answer",
    )

    messages = intake_server.get_intake_messages(req.caseId)
    session_messages = [
        {"role": "user" if m["senderType"] == "user" else "assistant", "content": m["messageText"]}
        for m in messages
    ]

    doc_table = get_table("IntakeDocuments")
    doc_resp = doc_table.query(
        KeyConditionExpression="caseId = :cid",
        ExpressionAttributeValues={":cid": req.caseId},
    )
    doc_texts = [
        d.get("extractedText", "") for d in doc_resp.get("Items", [])
        if d.get("extractedText")
    ]

    workflow = compile_workflow()
    result = workflow.invoke({
        "case_id": req.caseId,
        "session_messages": session_messages,
        "extracted_document_texts": doc_texts if doc_texts else None,
        "follow_up_round": case.get("followUpRound", 0),
    })

    intake_output = result.get("intake_output", {})
    follow_up_questions = intake_output.get("followUpQuestions", [])
    explanation_output = result.get("explanation_output")

    agent_response = ""
    if result.get("needs_followup") and follow_up_questions:
        agent_response = "I need a bit more information to proceed:\n" + "\n".join(f"- {q}" for q in follow_up_questions)
    elif result.get("escalated"):
        agent_response = "Thank you for providing this information. Your case has been escalated for review by a supervisor."
    elif explanation_output:
        agent_response = "Thank you. Your intake has been completed and is being reviewed."
    else:
        agent_response = "Thank you for the information. Processing your intake."

    intake_complete = result.get("final_status") is not None and not result.get("needs_followup", False)

    return {
        "caseId": req.caseId,
        "agentResponse": agent_response,
        "followUpQuestions": follow_up_questions,
        "intakeComplete": intake_complete,
    }


# --- API-003: Upload Intake Document ---

@router.post("/upload")
async def upload_document(
    caseId: str = Form(...),
    documentCategory: str = Form("other"),
    file: UploadFile = File(...),
):
    case = intake_server.get_intake_case(caseId)
    if not case:
        raise HTTPException(status_code=404, detail=f"Case {caseId} not found")

    if case["status"] != CaseStatus.IN_PROGRESS:
        raise HTTPException(status_code=409, detail=f"Case {caseId} is no longer in progress")

    ext = os.path.splitext(file.filename or "")[1].lower()
    if ext in BLOCKED_EXTENSIONS:
        raise HTTPException(status_code=400, detail=f"Unsupported file type: {ext}")

    content = await file.read()
    if len(content) == 0:
        raise HTTPException(status_code=400, detail="File is empty (0 bytes)")

    document_id = uuid.uuid4().hex
    s3_key = f"{caseId}/{document_id}/{file.filename}"
    storage_path = upload_file(content, s3_key, file.content_type or "application/octet-stream")

    extraction_status = ExtractionStatus.PENDING
    extracted_text = None
    extraction_confidence = None

    if file.content_type and file.content_type.startswith("text/"):
        try:
            extracted_text = content.decode("utf-8", errors="replace")
            extraction_confidence = 0.9
            extraction_status = ExtractionStatus.COMPLETE
        except Exception:
            extraction_status = ExtractionStatus.FAILED
            extraction_confidence = 0.0

    now = datetime.now(timezone.utc).isoformat()
    doc = IntakeDocument(
        caseId=caseId,
        documentId=document_id,
        fileName=file.filename or "unknown",
        fileType=file.content_type or "application/octet-stream",
        storagePath=storage_path,
        extractedText=extracted_text,
        extractionConfidence=extraction_confidence,
        extractionStatus=extraction_status,
        documentCategory=documentCategory,
        createdAt=now,
    )

    table = get_table("IntakeDocuments")
    table.put_item(Item=doc.to_dynamo())

    return {
        "documentId": document_id,
        "fileName": file.filename,
        "extractionStatus": extraction_status.value,
    }
