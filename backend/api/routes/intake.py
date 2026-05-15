"""Intake API routes: API-001, API-002, API-003, plus duplicate confirmation."""

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
from backend.db import get_table, sanitize_for_dynamo
from backend.config import S3_BUCKET_NAME

router = APIRouter()


class CreateSessionRequest(BaseModel):
    reporterType: str


class SubmitMessageRequest(BaseModel):
    caseId: str
    messageText: str
    attachmentIds: list[str] | None = None


class ConfirmMatchRequest(BaseModel):
    caseId: str
    matchedCaseId: str


class DenyMatchRequest(BaseModel):
    caseId: str


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
    duplicate_matches = result.get("duplicate_matches", [])
    duplicate_pending = result.get("duplicate_pending_confirmation", False)

    agent_response = ""
    if duplicate_pending and duplicate_matches:
        top = duplicate_matches[0]
        agent_response = (
            f"I found a potential matching case ({top['caseId']}) with "
            f"{top['confidence']:.0%} confidence. {top.get('reasoning', '')}\n\n"
            f"Is this the same child you are reporting about? "
            f"If yes, I'll update the existing case instead of creating a new one."
        )
    elif result.get("needs_followup") and follow_up_questions:
        agent_response = "I need a bit more information to proceed:\n" + "\n".join(f"- {q}" for q in follow_up_questions)
    elif result.get("escalated"):
        agent_response = "Thank you for providing this information. Your case has been escalated for review by a supervisor."
    elif explanation_output:
        agent_response = "Thank you. Your intake has been completed and is being reviewed."
    else:
        agent_response = "Thank you for the information. Processing your intake."

    intake_complete = result.get("final_status") is not None and not result.get("needs_followup", False)

    response = {
        "caseId": req.caseId,
        "agentResponse": agent_response,
        "followUpQuestions": follow_up_questions,
        "intakeComplete": intake_complete,
    }

    if duplicate_pending and duplicate_matches:
        response["duplicateMatch"] = {
            "matchedCaseId": duplicate_matches[0]["caseId"],
            "confidence": duplicate_matches[0]["confidence"],
            "reasoning": duplicate_matches[0].get("reasoning", ""),
            "fieldScores": duplicate_matches[0].get("fieldScores", {}),
            "confirmationRequired": True,
        }

    return response


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


# --- API-004: Confirm Duplicate Match ---

@router.post("/confirm-match")
def confirm_match(req: ConfirmMatchRequest):
    new_case = intake_server.get_intake_case(req.caseId)
    if not new_case:
        raise HTTPException(status_code=404, detail=f"Case {req.caseId} not found")

    matched_case = intake_server.get_intake_case(req.matchedCaseId)
    if not matched_case:
        raise HTTPException(status_code=404, detail=f"Matched case {req.matchedCaseId} not found")

    new_fields = new_case.get("structuredFields") or {}
    existing_fields = matched_case.get("structuredFields") or {}

    merged = _merge_structured_fields(existing_fields, new_fields)
    intake_server.update_intake_case(req.matchedCaseId, {"structuredFields": merged})

    messages = intake_server.get_intake_messages(req.caseId)
    for msg in messages:
        if msg.get("senderType") == "user":
            intake_server.save_intake_message(
                case_id=req.matchedCaseId,
                message_text=msg["messageText"],
                sender_type="user",
                message_type="follow-up-answer",
            )

    intake_server.update_intake_case(req.caseId, {
        "status": "MERGED",
        "humanReviewReason": f"Merged into {req.matchedCaseId} by reporter confirmation",
    })

    audit_server.save_agent_decision(
        case_id=req.caseId,
        agent_name="system",
        output_json={
            "action": "duplicate_confirmed",
            "mergedInto": req.matchedCaseId,
        },
    )

    audit_server.save_agent_decision(
        case_id=req.matchedCaseId,
        agent_name="system",
        output_json={
            "action": "case_updated_from_duplicate",
            "mergedFrom": req.caseId,
        },
    )

    workflow = compile_workflow()
    matched_messages = intake_server.get_intake_messages(req.matchedCaseId)
    session_messages = [
        {"role": "user" if m["senderType"] == "user" else "assistant", "content": m["messageText"]}
        for m in matched_messages
    ]

    result = workflow.invoke({
        "case_id": req.matchedCaseId,
        "session_messages": session_messages,
        "follow_up_round": matched_case.get("followUpRound", 0),
    })

    return {
        "action": "merged",
        "originalCaseId": req.caseId,
        "mergedIntoCaseId": req.matchedCaseId,
        "agentResponse": f"Thank you for confirming. I've updated the existing case {req.matchedCaseId} with the new information you provided.",
    }


# --- API-005: Deny Duplicate Match ---

@router.post("/deny-match")
def deny_match(req: DenyMatchRequest):
    case = intake_server.get_intake_case(req.caseId)
    if not case:
        raise HTTPException(status_code=404, detail=f"Case {req.caseId} not found")

    audit_server.save_agent_decision(
        case_id=req.caseId,
        agent_name="system",
        output_json={"action": "duplicate_denied"},
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

    if result.get("needs_followup") and follow_up_questions:
        agent_response = "I need a bit more information to proceed:\n" + "\n".join(f"- {q}" for q in follow_up_questions)
    elif result.get("escalated"):
        agent_response = "Your case has been escalated for review by a supervisor."
    elif explanation_output:
        agent_response = "Thank you. Your intake has been completed and is being reviewed."
    else:
        agent_response = "Understood — this is a new case. Processing your intake."

    return {
        "action": "new_case",
        "caseId": req.caseId,
        "agentResponse": agent_response,
        "intakeComplete": result.get("final_status") is not None and not result.get("needs_followup", False),
    }


def _merge_structured_fields(existing: dict, new: dict) -> dict:
    """Merge new fields into existing, preferring higher-confidence values."""
    merged = dict(existing)
    for key, new_val in new.items():
        if not isinstance(new_val, dict):
            if new_val is not None:
                merged[key] = new_val
            continue
        new_actual = new_val.get("value")
        new_conf = new_val.get("confidence", 0)
        if new_actual is None:
            continue
        existing_val = merged.get(key, {})
        if isinstance(existing_val, dict):
            existing_actual = existing_val.get("value")
            existing_conf = existing_val.get("confidence", 0)
            if existing_actual is None or new_conf > existing_conf:
                merged[key] = new_val
        else:
            merged[key] = new_val
    return merged
