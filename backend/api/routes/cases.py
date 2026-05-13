"""Cases API routes: API-004, API-005, API-007."""

from fastapi import APIRouter, HTTPException, Query
from backend.mcp_servers import intake_server, audit_server
from backend.db import get_table

router = APIRouter()


# --- API-004: Get Case Summary ---

@router.get("/{caseId}")
def get_case_summary(caseId: str):
    case = intake_server.get_intake_case(caseId)
    if not case:
        raise HTTPException(status_code=404, detail=f"Case {caseId} not found")

    agent_table = get_table("AgentOutputs")
    agent_resp = agent_table.query(
        KeyConditionExpression="caseId = :cid",
        ExpressionAttributeValues={":cid": caseId},
        ScanIndexForward=True,
    )
    agent_outputs = agent_resp.get("Items", [])

    audit_events = audit_server.get_audit_timeline(caseId)

    doc_table = get_table("IntakeDocuments")
    doc_resp = doc_table.query(
        KeyConditionExpression="caseId = :cid",
        ExpressionAttributeValues={":cid": caseId},
    )
    documents = doc_resp.get("Items", [])

    messages = intake_server.get_intake_messages(caseId)

    return {
        "case": case,
        "agentOutputs": agent_outputs,
        "auditEvents": audit_events,
        "documents": documents,
        "messages": messages,
    }


# --- API-005: List Cases ---

@router.get("")
def list_cases(
    status: str | None = Query(None),
    riskLevel: str | None = Query(None),
    page: int = Query(1, ge=1),
    pageSize: int = Query(20, ge=1, le=100),
):
    table = get_table("IntakeCases")
    scan_kwargs = {}

    filter_parts = []
    expr_values = {}
    expr_names = {}

    if status:
        filter_parts.append("#s = :status")
        expr_values[":status"] = status
        expr_names["#s"] = "status"

    if riskLevel:
        filter_parts.append("riskLevel = :risk")
        expr_values[":risk"] = riskLevel

    if filter_parts:
        scan_kwargs["FilterExpression"] = " AND ".join(filter_parts)
        scan_kwargs["ExpressionAttributeValues"] = expr_values
        if expr_names:
            scan_kwargs["ExpressionAttributeNames"] = expr_names

    resp = table.scan(**scan_kwargs)
    items = resp.get("Items", [])

    items.sort(key=lambda x: x.get("createdAt", ""), reverse=True)

    start = (page - 1) * pageSize
    end = start + pageSize
    page_items = items[start:end]

    summaries = []
    for item in page_items:
        summaries.append({
            "caseId": item.get("caseId"),
            "status": item.get("status"),
            "riskLevel": item.get("riskLevel"),
            "urgency": item.get("urgency"),
            "dataQualityScore": item.get("dataQualityScore"),
            "biasStatus": item.get("biasStatus"),
            "humanReviewRequired": item.get("humanReviewRequired"),
            "createdAt": item.get("createdAt"),
        })

    return {
        "cases": summaries,
        "totalCount": len(items),
        "page": page,
        "pageSize": pageSize,
    }


# --- API-007: Get Case Explanation Summary ---

@router.get("/{caseId}/summary")
def get_case_explanation(caseId: str):
    case = intake_server.get_intake_case(caseId)
    if not case:
        raise HTTPException(status_code=404, detail=f"Case {caseId} not found")

    agent_table = get_table("AgentOutputs")
    resp = agent_table.query(
        KeyConditionExpression="caseId = :cid AND begins_with(agentNameTimestamp, :prefix)",
        ExpressionAttributeValues={
            ":cid": caseId,
            ":prefix": "explanation#",
        },
        ScanIndexForward=False,
        Limit=1,
    )
    items = resp.get("Items", [])
    if not items:
        return {
            "caseId": caseId,
            "explanation": None,
            "message": "No explanation generated yet",
        }

    return {
        "caseId": caseId,
        "explanation": items[0].get("outputJson", {}),
    }
