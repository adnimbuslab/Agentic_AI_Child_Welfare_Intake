# Agentic AI Child Welfare Intake System — Detailed Specification

**Version:** 1.1  
**Date:** 2026-05-12  
**Status:** Draft  

---

## Table of Contents

1. [Introduction & Scope](#1-introduction--scope)
2. [Requirement Traceability Structure](#2-requirement-traceability-structure)
3. [Business Requirements (BR)](#3-business-requirements-br)
4. [Functional Requirements (FR)](#4-functional-requirements-fr)
5. [Agent Requirements (AR)](#5-agent-requirements-ar)
6. [Human-in-the-Loop Requirements (HITL)](#6-human-in-the-loop-requirements-hitl)
7. [API Requirements (API)](#7-api-requirements-api)
8. [MCP Server Requirements (MCP)](#8-mcp-server-requirements-mcp)
9. [Database Requirements (DB)](#9-database-requirements-db)
10. [Frontend Requirements (FE)](#10-frontend-requirements-fe)
11. [Non-Functional Requirements (NFR)](#11-non-functional-requirements-nfr)
12. [LangGraph Workflow Specification (WF)](#12-langgraph-workflow-specification-wf)
13. [Deployment Requirements (DEP)](#13-deployment-requirements-dep)
14. [Test Requirements (TEST)](#14-test-requirements-test)
15. [Requirement Traceability Matrix](#15-requirement-traceability-matrix)

---

## 1. Introduction & Scope

### 1.1 Purpose

This document provides the detailed specification for the Agentic AI Child Welfare Intake POC. It covers business workflows, functional requirements, technical architecture, agent design, API contracts, database schema, MCP server interfaces, frontend screens, and deployment constraints.

### 1.2 System Overview

The system is a chatbot-based child welfare intake platform. It accepts free-text narratives and supporting documents from reporters, converts unstructured input to structured intake data, assesses child vulnerability/risk, monitors data quality and bias, and produces a human-readable intake summary for caseworker review.

### 1.3 Key Design Principles

- Unstructured-to-structured conversion via LLM agents
- Multi-agent orchestration using LangGraph
- Claude Opus 4.7 for all agent LLM calls; model must be replaceable via configuration
- Agent tools accessed through MCP servers (no direct backend calls from agents)
- Human-in-the-loop at multiple pipeline stages
- Full audit trail for every agent decision
- LocalStack for local AWS simulation; path to real AWS AgentCore

### 1.4 Primary Users

| User Type | Description |
|-----------|-------------|
| Reporter / Intake Submitter | Caseworker, mandated reporter, school/healthcare staff; submits concern details via chatbot |
| Caseworker | Reviews structured output, risk recommendation, data completeness, AI explanation, escalation flags |
| Human Reviewer / Supervisor | Reviews escalated, uncertain, biased, or high-risk cases |

---

## 2. Requirement Traceability Structure

Requirement IDs follow this format:

| Prefix | Domain |
|--------|--------|
| BR | Business Requirement |
| FR | Functional Requirement |
| AR | Agent Requirement |
| HITL | Human-in-the-Loop Requirement |
| API | API Endpoint Requirement |
| MCP | MCP Server / Tool Requirement |
| DB | Database Requirement |
| FE | Frontend Requirement |
| NFR | Non-Functional Requirement |
| WF | LangGraph Workflow Requirement |
| DEP | Deployment Requirement |
| TEST | Test Requirement |

Each requirement entry includes:
- **ID** — unique identifier
- **Title** — short label
- **Description** — full requirement text
- **Priority** — Must / Should / Could
- **Source** — reference to source document section
- **Traces To** — related requirement IDs

---

## 3. Business Requirements (BR)

### BR-001
**Title:** Chatbot-Based Intake Interface  
**Description:** The system must provide a React-based chatbot interface where authorized reporters can submit child welfare intake information. The interface must not require a rigid form at the start; it must accept messy, real-world, unstructured information.  
**Priority:** Must  
**Source:** Business_requirement.md §3  
**Traces To:** FR-001, FE-001, FE-002

---

### BR-002
**Title:** Multi-Modal Intake Submission  
**Description:** The system must accept the following input types from reporters: free-text narratives, images, scanned documents, PDFs, forms, identification documents (e.g., birth certificate, driving licence), videos, and any other supporting files.  
**Priority:** Must  
**Source:** Business_requirement.md §3  
**Traces To:** FR-002, API-003, DB-003

---

### BR-003
**Title:** Unstructured-to-Structured Data Conversion  
**Description:** The system must convert unstructured reporter narratives and uploaded documents into structured intake fields. Extracted fields must include, at minimum: child name, child date of birth, child age, guardian/parent information, reporter information, reporter relationship to child, contact details, address/location, type of concern, description of incident, urgency indicators, prior known concerns, uploaded document metadata, extracted document facts, and per-field confidence scores.  
**Priority:** Must  
**Source:** Business_requirement.md §4  
**Traces To:** FR-003, AR-001

---

### BR-004
**Title:** Missing Data Follow-Up Questions  
**Description:** When required information is missing, the system must generate human-friendly follow-up questions and present them to the reporter via the chatbot interface. The system must ask only necessary questions and must not overwhelm the user.  
**Priority:** Must  
**Source:** Business_requirement.md §5  
**Traces To:** FR-004, AR-001, WF-003

---

### BR-005
**Title:** Risk Assessment  
**Description:** The system must evaluate child vulnerability and assign a risk level (Low, Medium, High, or Critical), a confidence score, an urgency recommendation, and a list of contributing risk factors based on the structured intake data.  
**Priority:** Must  
**Source:** Business_requirement.md §6  
**Traces To:** FR-005, AR-002

---

### BR-006
**Title:** Risk Assessment Input Factors  
**Description:** The Risk Assessment Agent must consider: type of concern, age of child, severity of alleged harm, urgency indicators, prior history, reporter credibility/context, household instability indicators, missing critical information, and immediate safety concerns.  
**Priority:** Must  
**Source:** Business_requirement.md §6  
**Traces To:** AR-002

---

### BR-007
**Title:** Data Quality Validation  
**Description:** The system must validate whether the structured intake data is complete, consistent, and usable before it is sent for risk scoring and caseworker review. Validation must check: required field presence, value conflicts, age/DOB consistency, document readability, extracted value reliability, critical field completeness, and case readiness.  
**Priority:** Must  
**Source:** Business_requirement.md §7  
**Traces To:** FR-006, AR-003

---

### BR-008
**Title:** Bias Monitoring  
**Description:** The system must check whether risk output or recommendation may be influenced by sensitive or inappropriate factors, including: demographic over-reliance, location-based bias, reporter bias, language bias, socioeconomic proxy bias, unfair risk amplification, and inconsistent treatment of similar cases.  
**Priority:** Must  
**Source:** Business_requirement.md §8  
**Traces To:** FR-007, AR-004

---

### BR-009
**Title:** Intake Record Persistence  
**Description:** The system must save a complete intake record to DynamoDB including: raw intake text, uploaded file references, extracted structured fields, missing field history, follow-up Q&A, all agent outputs, risk score, confidence scores, bias check result, data quality score, final explanation, human review status, and audit metadata.  
**Priority:** Must  
**Source:** Business_requirement.md §9  
**Traces To:** FR-008, DB-001 through DB-005

---

### BR-010
**Title:** Caseworker-Facing Explanation  
**Description:** The system must produce a human-readable summary for the caseworker dashboard showing: Case ID, risk level, confidence %, urgency, data quality %, bias check result, reasons for risk level, recommendation (e.g., route to investigation unit), and human review status with reason.  
**Priority:** Must  
**Source:** Business_requirement.md §10  
**Traces To:** FR-009, AR-005, FE-005

---

### BR-011
**Title:** Final Case Status Classification  
**Description:** Every completed intake must be assigned one of the following final statuses: READY_FOR_CASEWORKER_REVIEW, NEEDS_MORE_INFORMATION, ESCALATED_TO_SUPERVISOR, CRITICAL_IMMEDIATE_REVIEW, BIAS_REVIEW_REQUIRED, LOW_CONFIDENCE_REVIEW_REQUIRED.  
**Priority:** Must  
**Source:** Business_requirement.md §11.5  
**Traces To:** FR-010, DB-001

---

### BR-012
**Title:** Audit Trail Preservation  
**Description:** Even when a case is escalated to a human reviewer, the system must save the complete case state and full audit trail before escalation occurs. No agent decision or state transition may be lost.  
**Priority:** Must  
**Source:** Business_requirement.md §9  
**Traces To:** FR-011, DB-005

---

## 4. Functional Requirements (FR)

### FR-001
**Title:** Create Intake Session  
**Description:** The system must allow a reporter to initiate a new intake session, which generates a unique case ID and an empty structured intake record.  
**Priority:** Must  
**Source:** BR-001  
**Traces To:** API-001, DB-001, WF-001

---

### FR-002
**Title:** Document Upload and Storage  
**Description:** The system must accept file uploads (images, PDFs, videos, documents) during an active intake session, store them in S3-compatible storage (LocalStack S3), and save metadata to the IntakeDocuments table.  
**Priority:** Must  
**Source:** BR-002  
**Traces To:** API-003, DB-003, MCP-001

---

### FR-003
**Title:** Structured Field Extraction  
**Description:** The Intake Understanding Agent must process submitted text and uploaded document content to extract structured intake fields. Each extracted field must carry a confidence score between 0 and 1.  
**Priority:** Must  
**Source:** BR-003  
**Traces To:** AR-001, MCP-003

---

### FR-004
**Title:** Interactive Follow-Up Question Loop  
**Description:** After initial extraction, the system must identify missing required fields, generate one or more human-friendly follow-up questions, send those questions to the reporter via the chatbot interface, process the reporter's answers, and repeat extraction until no critical fields are missing or the reporter cannot provide the information.  
**Priority:** Must  
**Source:** BR-004  
**Traces To:** AR-001, WF-003, FE-002

---

### FR-005
**Title:** Risk Scoring  
**Description:** The Risk Assessment Agent must produce a risk level (Low/Medium/High/Critical), a confidence score (0–1), an urgency label, and a list of contributing risk factors for every case that has sufficient structured data.  
**Priority:** Must  
**Source:** BR-005  
**Traces To:** AR-002, MCP-004, WF-004

---

### FR-006
**Title:** Data Quality Scoring  
**Description:** The Data Quality Agent must produce a numeric completeness score (0–1), a list of missing critical fields, a list of detected inconsistencies, and a boolean readiness flag for every intake case.  
**Priority:** Must  
**Source:** BR-007  
**Traces To:** AR-003, WF-006

---

### FR-007
**Title:** Bias Check  
**Description:** The Bias Monitoring Agent must review the risk reasoning and produce a bias status (Passed/Flagged), a bias confidence score, a list of specific flags, and a humanReviewRequired boolean for every risk assessment.  
**Priority:** Must  
**Source:** BR-008  
**Traces To:** AR-004, WF-008

---

### FR-008
**Title:** Case Persistence  
**Description:** After all agents complete and pass their gates, the system must write or update a full intake record in DynamoDB (IntakeCases, AgentOutputs, AuditEvents tables).  
**Priority:** Must  
**Source:** BR-009  
**Traces To:** DB-001, DB-004, DB-005, MCP-001, WF-010

---

### FR-009
**Title:** Caseworker Explanation Generation  
**Description:** The Explanation Agent must transform technical agent outputs into a structured caseworker summary including plain-language risk explanation, recommendation, limitations, and next action.  
**Priority:** Must  
**Source:** BR-010  
**Traces To:** AR-005, FE-005

---

### FR-010
**Title:** Final Case Status Assignment  
**Description:** The system must assign one of the six defined final statuses (BR-011) to every case before routing it to the caseworker dashboard or human review queue.  
**Priority:** Must  
**Source:** BR-011  
**Traces To:** DB-001, WF-011

---

### FR-011
**Title:** Audit Event Logging  
**Description:** Every agent decision, state transition, human action, confidence score, and escalation reason must be written as an immutable event to the AuditEvents table with actor, timestamp, before/after state, and reason.  
**Priority:** Must  
**Source:** BR-012  
**Traces To:** DB-005, MCP-005

---

### FR-012
**Title:** Human Review Action  
**Description:** A human reviewer must be able to accept a case, override risk level, add notes, and update the case status via the Human Review Queue interface.  
**Priority:** Must  
**Source:** Business_requirement.md §11  
**Traces To:** API-006, FE-007, DB-001

---

### FR-013
**Title:** Caseworker Case List  
**Description:** Caseworkers must be able to view a paginated list of all intake cases showing case ID, risk level, status, urgency, data completeness, bias flag, and human review flag.  
**Priority:** Must  
**Source:** Business_requirement.md §13  
**Traces To:** API-005, FE-004

---

### FR-014
**Title:** Case Detail View  
**Description:** Caseworkers must be able to view a full case detail page showing: structured intake summary, uploaded documents, extracted fields with confidence scores, follow-up Q&A, risk explanation, agent confidence scores, and audit timeline.  
**Priority:** Must  
**Source:** Business_requirement.md §13  
**Traces To:** API-004, FE-005, FE-006

---

---

## 5. Agent Requirements (AR)

All agents must use Claude Opus 4.7 as the LLM. The LLM provider and model must be configurable via an environment variable or config file so they can be replaced without code changes.

### AR-001 — Intake Understanding Agent

**Title:** Intake Understanding Agent  
**Source:** Business_requirement.md §4, §5; technical_requirement.md §18.1  
**Traces To:** FR-003, FR-004, MCP-001, MCP-002, MCP-003, MCP-007, WF-002, WF-003

**Responsibilities:**
1. Read and interpret chatbot text messages.
2. Read and interpret extracted document text from uploaded files.
3. Convert unstructured input into the set of structured intake fields defined in BR-003.
4. For each extracted field, assign a confidence score between 0 and 1.
5. Identify which required fields are still missing.
6. Generate human-friendly follow-up questions for each missing required field; limit to the most critical questions per turn to avoid overwhelming the reporter.
7. Return a structured output object on every invocation.

**Required Input:**
```json
{
  "sessionMessages": [{ "role": "user|assistant", "content": "string" }],
  "extractedDocumentTexts": ["string"],
  "currentStructuredFields": {}
}
```

**Required Output:**
```json
{
  "structuredFields": {
    "childName": { "value": "string|null", "confidence": 0.0 },
    "childDob": { "value": "string|null", "confidence": 0.0 },
    "childAge": { "value": "number|null", "confidence": 0.0 },
    "guardianInfo": { "value": "string|null", "confidence": 0.0 },
    "reporterInfo": { "value": "string|null", "confidence": 0.0 },
    "reporterRelationship": { "value": "string|null", "confidence": 0.0 },
    "contactDetails": { "value": "string|null", "confidence": 0.0 },
    "address": { "value": "string|null", "confidence": 0.0 },
    "concernType": { "value": "string|null", "confidence": 0.0 },
    "incidentDescription": { "value": "string|null", "confidence": 0.0 },
    "urgencyIndicators": { "value": ["string"], "confidence": 0.0 },
    "priorConcerns": { "value": "string|null", "confidence": 0.0 }
  },
  "missingRequiredFields": ["string"],
  "followUpQuestions": ["string"],
  "overallConfidenceScore": 0.0,
  "escalate": false,
  "escalationReason": "string|null"
}
```

**Escalation Triggers (must set escalate=true):**
- System cannot parse the narrative at all (overallConfidenceScore < 0.3)
- Document extraction confidence is critically low (< 0.4) across all documents
- Uploaded documents are unreadable
- Reporter provides directly conflicting critical information
- Urgent danger signals present but child identity and location both missing

---

### AR-002 — Risk Assessment Agent

**Title:** Risk Assessment Agent  
**Source:** Business_requirement.md §6; technical_requirement.md §18.2  
**Traces To:** FR-005, MCP-003, MCP-004, WF-004, WF-005

**Responsibilities:**
1. Receive the structured intake fields from AR-001.
2. Evaluate child vulnerability using all factors listed in BR-006.
3. Assign a risk level: Low, Medium, High, or Critical.
4. Assign a confidence score between 0 and 1.
5. Determine urgency label (e.g., "Immediate — within hours", "Within 24 hours", "Within 72 hours", "Routine").
6. List all contributing risk factors that influenced the score.

**Required Input:**
```json
{
  "structuredFields": {},
  "dataQualityScore": 0.0,
  "documentSummaries": ["string"]
}
```

**Required Output:**
```json
{
  "riskLevel": "Low|Medium|High|Critical",
  "confidenceScore": 0.0,
  "urgency": "string",
  "riskFactors": ["string"],
  "escalate": false,
  "escalationReason": "string|null"
}
```

**Escalation Triggers:**
- confidenceScore < 0.6
- riskLevel == "Critical" (always escalate regardless of confidence)
- riskLevel == "High" with dataQualityScore < 0.5
- Immediate safety concern detected but data completeness is poor

---

### AR-003 — Data Quality Agent

**Title:** Data Quality Agent  
**Source:** Business_requirement.md §7; technical_requirement.md §18.3  
**Traces To:** FR-006, WF-006, WF-007

**Responsibilities:**
1. Validate completeness against the required field list from the Knowledge/Policy MCP Server.
2. Detect contradictions (e.g., reported age vs. DOB).
3. Check consistency of all fields against each other.
4. Evaluate document readability scores.
5. Decide whether the case is ready for caseworker review.

**Required Input:**
```json
{
  "structuredFields": {},
  "intakeMessages": [],
  "documentExtractionResults": []
}
```

**Required Output:**
```json
{
  "dataQualityScore": 0.0,
  "missingCriticalFields": ["string"],
  "inconsistencies": [{ "field": "string", "detail": "string" }],
  "readyForReview": true,
  "escalate": false,
  "escalationReason": "string|null"
}
```

**Escalation Triggers:**
- Any critical field still missing AND reporter has already been asked
- dataQualityScore < 0.5 after follow-up rounds
- Documents contradict user-provided information in a critical field
- Identity or relationship cannot be verified from any submitted source

---

### AR-004 — Bias Monitoring Agent

**Title:** Bias Monitoring Agent  
**Source:** Business_requirement.md §8; technical_requirement.md §18.4  
**Traces To:** FR-007, MCP-005, MCP-007, WF-008, WF-009

**Responsibilities:**
1. Review the risk assessment output and its contributing factors.
2. Identify whether any sensitive demographic, socioeconomic, location-based, reporter-based, or language-based attribute appears to be driving the risk score unfairly.
3. Check for inconsistent treatment compared to policy guidelines.
4. Produce a bias status and confidence score.
5. For POC: rule-based checks supplemented by LLM review (not SageMaker Clarify).

**Required Input:**
```json
{
  "riskAssessmentOutput": {},
  "structuredFields": {},
  "biasPolicy": "string"
}
```

**Required Output:**
```json
{
  "biasStatus": "Passed|Flagged",
  "biasConfidence": 0.0,
  "flags": [{ "type": "string", "detail": "string" }],
  "humanReviewRequired": false,
  "escalationReason": "string|null"
}
```

**Escalation Triggers:**
- biasStatus == "Flagged" (always escalate)
- biasConfidence < 0.7 (cannot confirm fairness)
- Sensitive attribute detected in the primary risk factor list

---

### AR-005 — Explanation Agent

**Title:** Explanation Agent  
**Source:** Business_requirement.md §10; technical_requirement.md §18.5  
**Traces To:** FR-009, FE-005, WF-011

**Responsibilities:**
1. Receive all prior agent outputs.
2. Convert technical outputs into simple, plain-language caseworker-facing explanation.
3. Show confidence levels and system limitations without overstating certainty.
4. Clearly explain why the risk level was selected.
5. State whether human review is needed and why.
6. Avoid diagnostic or overly certain language.

**Required Input:**
```json
{
  "intakeUnderstandingOutput": {},
  "riskAssessmentOutput": {},
  "dataQualityOutput": {},
  "biasMonitoringOutput": {},
  "caseId": "string"
}
```

**Required Output:**
```json
{
  "caseworkerSummary": "string",
  "riskExplanation": ["string"],
  "recommendation": "string",
  "limitations": ["string"],
  "nextAction": "string",
  "humanReviewRequired": false,
  "humanReviewReason": "string|null",
  "finalCaseStatus": "READY_FOR_CASEWORKER_REVIEW|NEEDS_MORE_INFORMATION|ESCALATED_TO_SUPERVISOR|CRITICAL_IMMEDIATE_REVIEW|BIAS_REVIEW_REQUIRED|LOW_CONFIDENCE_REVIEW_REQUIRED"
}
```

---

### AR-006 — LLM Configuration Requirement

**Title:** Replaceable LLM Provider  
**Description:** All five agents must obtain their LLM client through a shared factory function that reads model ID and provider from environment variables (e.g., `LLM_MODEL_ID`, `LLM_PROVIDER`). Swapping Claude Opus 4.7 for another model must require only an env-var change, not a code change.  
**Priority:** Must  
**Source:** technical_requirement.md §19 ("Important")  
**Traces To:** DEP-001

---

## 6. Human-in-the-Loop Requirements (HITL)

### HITL-001 — Post-Intake-Understanding Escalation
**Title:** Escalate After Intake Understanding  
**Description:** The LangGraph workflow must route to the Human Review Queue if the Intake Understanding Agent sets `escalate=true` (see AR-001 escalation triggers).  
**Priority:** Must  
**Source:** Business_requirement.md §11.1  
**Traces To:** WF-003, MCP-006, DB-001

---

### HITL-002 — Post-Risk-Assessment Escalation
**Title:** Escalate After Risk Assessment  
**Description:** The LangGraph workflow must route to the Human Review Queue if the Risk Assessment Agent sets `escalate=true` (see AR-002 escalation triggers). Critical risk cases must always be human-reviewed regardless of confidence score.  
**Priority:** Must  
**Source:** Business_requirement.md §11.2  
**Traces To:** WF-005, MCP-006, DB-001

---

### HITL-003 — Post-Data-Quality Escalation
**Title:** Escalate After Data Quality Check  
**Description:** The LangGraph workflow must route to the Human Review Queue if the Data Quality Agent sets `escalate=true` (see AR-003 escalation triggers).  
**Priority:** Must  
**Source:** Business_requirement.md §11.3  
**Traces To:** WF-007, MCP-006, DB-001

---

### HITL-004 — Post-Bias-Monitor Escalation
**Title:** Escalate After Bias Monitoring  
**Description:** The LangGraph workflow must route to the Human Review Queue if the Bias Monitoring Agent sets `humanReviewRequired=true` or if biasStatus == "Flagged".  
**Priority:** Must  
**Source:** Business_requirement.md §11.4  
**Traces To:** WF-009, MCP-006, DB-001

---

### HITL-005 — Final Routing Gate
**Title:** Final Case Routing Checkpoint  
**Description:** Before marking a case READY_FOR_CASEWORKER_REVIEW, the Explanation Agent must evaluate all agent outputs and assign the final case status. Cases with final status other than READY_FOR_CASEWORKER_REVIEW must be routed to the Human Review Queue.  
**Priority:** Must  
**Source:** Business_requirement.md §11.5  
**Traces To:** AR-005, WF-011, FE-007

---

### HITL-006 — Human Review Action API
**Title:** Human Override Action  
**Description:** A supervisor must be able to submit a review decision (approve, override, request more info) with free-text notes via the Human Review Queue UI and API. The system must record the override as an audit event and update the case status.  
**Priority:** Must  
**Source:** Business_requirement.md §11  
**Traces To:** FR-012, API-006, MCP-005

---

### HITL-007 — No Silent AI Finalization
**Title:** AI Must Not Independently Finalize High-Stakes Cases  
**Description:** The system must never set status READY_FOR_CASEWORKER_REVIEW on a High or Critical risk case without first passing through the human review queue. The AI may prioritize and recommend but must not independently finalize such cases.  
**Priority:** Must  
**Source:** Business_requirement.md §11.2  
**Traces To:** WF-005, HITL-002

---

## 7. API Requirements (API)

All endpoints are exposed via LocalStack API Gateway. Lambda functions implement the handlers.

### API-001 — Create Intake Session
**Endpoint:** `POST /intake/session`  
**Lambda:** `CreateIntakeSessionLambda`  
**Request Body:** `{ "reporterType": "string" }`  
**Response:** `{ "caseId": "string", "sessionToken": "string", "createdAt": "ISO8601" }`  
**Description:** Creates a new intake case record in DynamoDB with status `IN_PROGRESS` and returns the caseId for the session.  
**Priority:** Must  
**Traces To:** FR-001, DB-001

---

### API-002 — Submit Intake Message
**Endpoint:** `POST /intake/message`  
**Lambda:** `SubmitIntakeMessageLambda`  
**Request Body:** `{ "caseId": "string", "messageText": "string", "attachmentIds": ["string"] }`  
**Response:** `{ "caseId": "string", "agentResponse": "string", "followUpQuestions": ["string"], "intakeComplete": false }`  
**Description:** Submits a reporter message, triggers the Intake Understanding Agent, and returns the agent's response including follow-up questions if any.  
**Priority:** Must  
**Traces To:** FR-003, FR-004, AR-001, DB-002

---

### API-003 — Upload Intake Document
**Endpoint:** `POST /intake/upload`  
**Lambda:** `UploadIntakeDocumentLambda`  
**Request Body:** `multipart/form-data` with `caseId`, `file`, `documentCategory`  
**Response:** `{ "documentId": "string", "fileName": "string", "extractionStatus": "pending|complete|failed" }`  
**Description:** Uploads a file to LocalStack S3, triggers document text extraction, and saves metadata to IntakeDocuments.  
**Priority:** Must  
**Traces To:** FR-002, DB-003

---

### API-004 — Get Case Summary
**Endpoint:** `GET /intake/{caseId}`  
**Lambda:** `GetCaseSummaryLambda`  
**Response:** Full case record including structured fields, agent outputs, risk score, explanation, audit events.  
**Priority:** Must  
**Traces To:** FR-014, DB-001

---

### API-005 — List Cases
**Endpoint:** `GET /cases`  
**Lambda:** `ListCasesLambda`  
**Query Params:** `status`, `riskLevel`, `page`, `pageSize`  
**Response:** Paginated list of case summaries.  
**Priority:** Must  
**Traces To:** FR-013, DB-001

---

### API-006 — Human Review Action
**Endpoint:** `POST /cases/{caseId}/human-review`  
**Lambda:** `HumanReviewActionLambda`  
**Request Body:** `{ "reviewerId": "string", "action": "approve|override|request_more_info", "overrideRiskLevel": "string|null", "notes": "string" }`  
**Response:** `{ "caseId": "string", "newStatus": "string", "updatedAt": "ISO8601" }`  
**Description:** Records a human reviewer's decision, updates the case status, and writes an audit event.  
**Priority:** Must  
**Traces To:** FR-012, HITL-006, DB-001, DB-005

---

### API-007 — Get Cases Summary (Dashboard Aggregate)
**Endpoint:** `GET /cases/{caseId}/summary`  
**Lambda:** `GetCaseSummaryLambda`  
**Response:** Caseworker-facing explanation output from the Explanation Agent.  
**Priority:** Must  
**Traces To:** FR-009, AR-005

---

## 8. MCP Server Requirements (MCP)

All MCP servers expose tools to LangGraph agents. Agents must call backend resources only through these MCP tools, never directly.

### MCP-001 — Intake MCP Server

**Tools:**

| Tool ID | Tool Name | Description |
|---------|-----------|-------------|
| MCP-001-T1 | `create_intake_case` | Create a new case record in IntakeCases table |
| MCP-001-T2 | `get_intake_case` | Retrieve full case record by caseId |
| MCP-001-T3 | `update_intake_case` | Update case status, risk, or quality fields |
| MCP-001-T4 | `save_structured_intake` | Write extracted structured fields to the case record |
| MCP-001-T5 | `save_intake_message` | Append a message to IntakeMessages |

**Priority:** Must  
**Source:** technical_requirement.md §17.1  
**Traces To:** FR-001, FR-002, FR-008, AR-001

---

### MCP-002 — Contacts MCP Server

**Tools:**

| Tool ID | Tool Name | Description |
|---------|-----------|-------------|
| MCP-002-T1 | `lookup_child_contact` | Look up child contact record by name/DOB |
| MCP-002-T2 | `lookup_guardian_contact` | Look up guardian contact by name/address |
| MCP-002-T3 | `lookup_reporter_contact` | Look up reporter contact by ID or name |
| MCP-002-T4 | `validate_contact_information` | Validate completeness of a contact record |

**Priority:** Should  
**Source:** technical_requirement.md §17.2  
**Traces To:** AR-001, AR-003

---

### MCP-003 — Case History MCP Server

**Tools:**

| Tool ID | Tool Name | Description |
|---------|-----------|-------------|
| MCP-003-T1 | `get_prior_referrals` | Retrieve prior referral records for a child |
| MCP-003-T2 | `get_case_history` | Retrieve full prior case history |
| MCP-003-T3 | `get_household_history` | Retrieve household instability history |

**Priority:** Should  
**Source:** technical_requirement.md §17.3  
**Traces To:** AR-002, BR-006

---

### MCP-004 — Risk Assessment MCP Server

**Tools:**

| Tool ID | Tool Name | Description |
|---------|-----------|-------------|
| MCP-004-T1 | `calculate_risk_score` | Invoke risk scoring logic with structured fields |
| MCP-004-T2 | `get_risk_thresholds` | Retrieve configured risk threshold values |
| MCP-004-T3 | `save_risk_assessment` | Persist risk assessment output to AgentOutputs |

**Priority:** Must  
**Source:** technical_requirement.md §17.4  
**Traces To:** AR-002, FR-005

---

### MCP-005 — Audit & Governance MCP Server

**Tools:**

| Tool ID | Tool Name | Description |
|---------|-----------|-------------|
| MCP-005-T1 | `save_agent_decision` | Write an agent output record to AgentOutputs |
| MCP-005-T2 | `save_confidence_score` | Record a field-level confidence score in AuditEvents |
| MCP-005-T3 | `save_escalation_reason` | Record escalation details in AuditEvents |
| MCP-005-T4 | `save_human_override` | Record a human reviewer's override in AuditEvents |
| MCP-005-T5 | `get_audit_timeline` | Retrieve ordered audit events for a case |

**Priority:** Must  
**Source:** technical_requirement.md §17.5  
**Traces To:** FR-011, HITL-006, DB-004, DB-005

---

### MCP-006 — Notification / Escalation MCP Server

**Tools:**

| Tool ID | Tool Name | Description |
|---------|-----------|-------------|
| MCP-006-T1 | `route_to_human_review` | Place a case in the human review queue with reason |
| MCP-006-T2 | `notify_caseworker` | Send notification to assigned caseworker |
| MCP-006-T3 | `notify_supervisor` | Send notification to supervisor for critical/bias cases |
| MCP-006-T4 | `create_review_task` | Create a task record in the review queue |

**Priority:** Must  
**Source:** technical_requirement.md §17.6  
**Traces To:** HITL-001 through HITL-005

---

### MCP-007 — Knowledge / Policy MCP Server

**Tools:**

| Tool ID | Tool Name | Description |
|---------|-----------|-------------|
| MCP-007-T1 | `get_intake_required_fields` | Return list of mandatory intake fields |
| MCP-007-T2 | `get_mandatory_reporting_rules` | Return mandatory reporting compliance rules |
| MCP-007-T3 | `get_risk_policy_guidelines` | Return risk assessment policy thresholds |
| MCP-007-T4 | `get_bias_monitoring_policy` | Return bias detection rules and sensitive attributes list |
| MCP-007-T5 | `get_human_review_policy` | Return conditions that trigger human review |

**Priority:** Must  
**Source:** technical_requirement.md §17.7  
**Traces To:** AR-001, AR-003, AR-004

---

## 9. Database Requirements (DB)

All tables are DynamoDB tables provisioned on LocalStack.

### DB-001 — IntakeCases Table

**Primary Key:** `PK: caseId` (String)

| Attribute | Type | Required | Description |
|-----------|------|----------|-------------|
| caseId | String | Yes | Unique case identifier (e.g., CW-2026-0001) |
| status | String | Yes | One of six final statuses (BR-011) or IN_PROGRESS |
| riskLevel | String | No | Low / Medium / High / Critical |
| riskConfidence | Number | No | 0–1 |
| urgency | String | No | Urgency label |
| dataQualityScore | Number | No | 0–1 |
| biasStatus | String | No | Passed / Flagged |
| humanReviewRequired | Boolean | No | Whether awaiting human reviewer |
| humanReviewReason | String | No | Reason for human review escalation |
| structuredFields | Map | No | Full extracted structured intake fields |
| missingFieldHistory | List | No | Fields that were missing at various points |
| reporterType | String | No | Reporter's role/type |
| createdAt | String | Yes | ISO 8601 |
| updatedAt | String | Yes | ISO 8601 |

**Priority:** Must  
**Source:** technical_requirement.md §15.1  
**Traces To:** FR-001, FR-008, FR-010

---

### DB-002 — IntakeMessages Table

**Primary Key:** `PK: caseId` (String), `SK: messageTimestamp` (String, ISO 8601)

| Attribute | Type | Required | Description |
|-----------|------|----------|-------------|
| caseId | String | Yes | Foreign key to IntakeCases |
| messageTimestamp | String | Yes | ISO 8601 sort key |
| senderType | String | Yes | user / agent / system |
| messageText | String | Yes | Raw message text |
| messageType | String | Yes | narrative / follow-up-question / follow-up-answer / system |
| attachments | List | No | List of documentIds attached to this message |
| agentGenerated | Boolean | Yes | Whether message was generated by an agent |
| createdAt | String | Yes | ISO 8601 |

**Priority:** Must  
**Source:** technical_requirement.md §15.2  
**Traces To:** FR-003, FR-004

---

### DB-003 — IntakeDocuments Table

**Primary Key:** `PK: caseId` (String), `SK: documentId` (String)

| Attribute | Type | Required | Description |
|-----------|------|----------|-------------|
| caseId | String | Yes | Foreign key to IntakeCases |
| documentId | String | Yes | UUID |
| fileName | String | Yes | Original file name |
| fileType | String | Yes | MIME type |
| storagePath | String | Yes | S3 key in LocalStack |
| extractedText | String | No | Text extracted from document |
| extractionConfidence | Number | No | 0–1 confidence of extraction |
| documentCategory | String | No | identity / incident-report / medical / other |
| createdAt | String | Yes | ISO 8601 |

**Priority:** Must  
**Source:** technical_requirement.md §15.3  
**Traces To:** FR-002, BR-002

---

### DB-004 — AgentOutputs Table

**Primary Key:** `PK: caseId` (String), `SK: agentName#timestamp` (String)

| Attribute | Type | Required | Description |
|-----------|------|----------|-------------|
| caseId | String | Yes | Foreign key to IntakeCases |
| agentName | String | Yes | intake-understanding / risk-assessment / data-quality / bias-monitoring / explanation |
| inputSummary | String | No | Short text summary of input |
| outputJson | Map | Yes | Full agent output object |
| confidenceScore | Number | No | Primary confidence score from this agent |
| status | String | Yes | success / escalated / error |
| escalationReason | String | No | Populated if status=escalated |
| createdAt | String | Yes | ISO 8601 |

**Priority:** Must  
**Source:** technical_requirement.md §15.4  
**Traces To:** FR-011, MCP-005

---

### DB-005 — AuditEvents Table

**Primary Key:** `PK: caseId` (String), `SK: eventTimestamp` (String, ISO 8601 + UUID suffix for uniqueness)

| Attribute | Type | Required | Description |
|-----------|------|----------|-------------|
| caseId | String | Yes | Foreign key to IntakeCases |
| eventTimestamp | String | Yes | ISO 8601 sort key |
| eventType | String | Yes | agent-decision / state-transition / human-override / escalation / field-extraction / bias-flag |
| actor | String | Yes | Agent name or human reviewer ID |
| agentName | String | No | Populated for agent events |
| action | String | Yes | Short action label |
| reason | String | No | Why this event occurred |
| beforeState | Map | No | State snapshot before event |
| afterState | Map | No | State snapshot after event |
| createdAt | String | Yes | ISO 8601 |

**Priority:** Must  
**Source:** technical_requirement.md §15.5  
**Traces To:** FR-011, BR-012

---

## 10. Frontend Requirements (FE)

### FE-001 — Chatbot Intake Interface (Screens)
**Title:** Intake Chat Screen  
**Description:** A React chat interface that presents a conversation thread, a text input area, a file upload button, an intake progress indicator showing percentage of required fields collected, and agent follow-up questions rendered as distinct assistant messages.  
**Priority:** Must  
**Source:** technical_requirement.md §13  
**Traces To:** BR-001, FR-001, FR-004

**Screen Elements:**
- Conversation message list (user messages right-aligned, agent messages left-aligned)
- Text input with send button
- File upload control (accepts images, PDFs, documents, videos)
- Intake progress indicator (0–100%)
- Inline follow-up questions rendered as agent chat bubbles
- Session status banner (IN_PROGRESS / COMPLETE / ESCALATED)

---

### FE-002 — Follow-Up Question Display
**Title:** Inline Follow-Up Questions  
**Description:** Follow-up questions generated by the Intake Understanding Agent must be rendered as individual assistant chat messages. The reporter answers by typing in the same text input. Multiple questions must be presented one at a time or in a minimal set per turn.  
**Priority:** Must  
**Source:** BR-004  
**Traces To:** FR-004, AR-001

---

### FE-003 — File Upload Handling
**Title:** File Upload Progress  
**Description:** When the reporter uploads a document, the UI must display an upload progress indicator and show extraction status (pending / extracted / failed) in the conversation thread once the backend responds.  
**Priority:** Must  
**Source:** BR-002  
**Traces To:** FR-002, API-003

---

### FE-004 — Caseworker Dashboard — Case List
**Title:** Case List View  
**Description:** A paginated table showing all cases with columns: Case ID, Status, Risk Level (colour-coded), Urgency, Data Completeness %, Bias Flag, Human Review Flag, Created At. Supports filtering by status and risk level.  
**Priority:** Must  
**Source:** technical_requirement.md §13  
**Traces To:** FR-013, API-005

---

### FE-005 — Caseworker Dashboard — Explanation Panel
**Title:** Case Explanation View  
**Description:** Displays the Explanation Agent output as a structured card: Case ID, Risk Level badge, Confidence %, Urgency, Data Quality %, Bias Check result, bulleted risk reasons, plain-language recommendation, limitations, and next action.  
**Priority:** Must  
**Source:** BR-010  
**Traces To:** FR-009, AR-005

---

### FE-006 — Case Detail View
**Title:** Case Detail Screen  
**Description:** Full detail view showing: structured intake field table with confidence scores, uploaded documents list (with download links and extraction status), follow-up Q&A thread, all agent output cards, and audit timeline (chronological list of AuditEvents).  
**Priority:** Must  
**Source:** technical_requirement.md §13  
**Traces To:** FR-014, API-004

---

### FE-007 — Human Review Queue
**Title:** Human Review Queue Screen  
**Description:** Lists all escalated cases with escalation reason and type (post-intake / post-risk / post-quality / post-bias / final-gate). Each row links to case detail. Reviewer can submit an action (approve / override / request more info) with notes via an inline form or modal.  
**Priority:** Must  
**Source:** technical_requirement.md §13; HITL-006  
**Traces To:** FR-012, API-006

---

## 11. Non-Functional Requirements (NFR)

### NFR-001 — Response Latency
**Title:** API Response Time  
**Description:** Each API endpoint must return a response within 30 seconds for standard intake messages. Agent pipeline invocations (full multi-agent chain) must complete within 60 seconds.  
**Priority:** Should  
**Source:** General UX quality  
**Traces To:** API-001 through API-007

---

### NFR-002 — LLM Model Replaceability
**Title:** LLM Model Configuration  
**Description:** Every agent must obtain its LLM client from a shared factory that reads `LLM_MODEL_ID` and `LLM_PROVIDER` environment variables. Changing the model must require only an environment variable change.  
**Priority:** Must  
**Source:** technical_requirement.md §19  
**Traces To:** AR-006, DEP-001

---

### NFR-003 — Audit Immutability
**Title:** Immutable Audit Log  
**Description:** AuditEvents records must never be updated or deleted after creation. Corrections are recorded as new events referencing the original.  
**Priority:** Must  
**Source:** BR-012  
**Traces To:** DB-005

---

### NFR-004 — Confidence Thresholds and Abstention
**Title:** Confidence-Based Abstention  
**Description:** Agents must abstain from finalizing a decision and escalate to human review rather than producing an unreliable output when confidence falls below configured thresholds. Thresholds must be configurable without code changes.  
**Priority:** Must  
**Source:** Business_requirement.md §1  
**Traces To:** HITL-001 through HITL-005

---

### NFR-005 — LocalStack Compatibility
**Title:** LocalStack AWS Simulation  
**Description:** All AWS service calls (DynamoDB, S3, API Gateway, Lambda) must work against LocalStack. No hardcoded AWS endpoints; all endpoint URLs must be configurable via environment variables (e.g., `AWS_ENDPOINT_URL`).  
**Priority:** Must  
**Source:** technical_requirement.md §12  
**Traces To:** DEP-001, DEP-002

---

### NFR-006 — Traceable Orchestration
**Title:** Traceable Agent Orchestration  
**Description:** Every node transition in the LangGraph workflow must be logged as an audit event so the complete decision path is reproducible from the AuditEvents table.  
**Priority:** Must  
**Source:** Business_requirement.md §1  
**Traces To:** FR-011, DB-005

---

### NFR-007 — No Direct Backend Access from Agents
**Title:** Agents Use MCP Only  
**Description:** LangGraph agent nodes must never call DynamoDB, S3, Lambda, or any backend service directly. All resource access must go through MCP server tools.  
**Priority:** Must  
**Source:** technical_requirement.md §17  
**Traces To:** MCP-001 through MCP-007

---

## 12. LangGraph Workflow Specification (WF)

### WF-001 — Start: Session Initialisation
**Node:** `start`  
**Description:** LangGraph workflow is triggered when a reporter submits their first intake message. Receives the caseId, initial message text, and any uploaded document IDs.  
**Traces To:** FR-001, API-002

---

### WF-002 — Intake Understanding Node
**Node:** `intake_understanding`  
**Description:** Invokes AR-001. Calls MCP-007-T1 to retrieve required fields list. Calls MCP-001-T2 to get current case state. Runs extraction. Calls MCP-001-T4 to save structured fields. Calls MCP-005-T1 to save agent decision. Returns output to router.  
**Traces To:** AR-001, MCP-001, MCP-005, MCP-007

---

### WF-003 — Follow-Up Question Router
**Node:** `follow_up_router`  
**Description:** If `missingRequiredFields` is non-empty and `escalate=false`, sends follow-up questions back to the reporter and waits for the next intake message (re-enters WF-002 on response). If `escalate=true`, routes to WF-012 (Human Review). If no missing fields, proceeds to WF-004.  
**Traces To:** HITL-001, FR-004

---

### WF-004 — Risk Assessment Node
**Node:** `risk_assessment`  
**Description:** Invokes AR-002. Calls MCP-007-T3 for policy thresholds. Calls MCP-003-T1 for prior referrals. Calls MCP-004-T1 to calculate risk score. Calls MCP-004-T3 to save output. Calls MCP-005-T1 to save agent decision.  
**Traces To:** AR-002, MCP-003, MCP-004, MCP-005

---

### WF-005 — Risk Confidence Gate
**Node:** `risk_gate`  
**Description:** Evaluates risk output. If `escalate=true` (per AR-002 triggers), routes to WF-012. Otherwise proceeds to WF-006.  
**Traces To:** HITL-002, HITL-007

---

### WF-006 — Data Quality Node
**Node:** `data_quality`  
**Description:** Invokes AR-003. Calls MCP-007-T1 for required field list. Evaluates completeness and consistency. Calls MCP-005-T1 to save agent decision.  
**Traces To:** AR-003, MCP-005, MCP-007

---

### WF-007 — Data Quality Gate
**Node:** `quality_gate`  
**Description:** If `escalate=true` (per AR-003 triggers), routes to WF-012. If `readyForReview=false` and additional follow-up is possible, loops back to WF-003. Otherwise proceeds to WF-008.  
**Traces To:** HITL-003

---

### WF-008 — Bias Monitoring Node
**Node:** `bias_monitoring`  
**Description:** Invokes AR-004. Calls MCP-007-T4 for bias policy. Reviews risk reasoning. Calls MCP-005-T1 to save agent decision.  
**Traces To:** AR-004, MCP-005, MCP-007

---

### WF-009 — Bias Gate
**Node:** `bias_gate`  
**Description:** If `humanReviewRequired=true` or `biasStatus=="Flagged"`, routes to WF-012. Otherwise proceeds to WF-010.  
**Traces To:** HITL-004

---

### WF-010 — Save Final Intake Record
**Node:** `save_intake`  
**Description:** Calls MCP-001-T3 to update the IntakeCases record with all final scores and outputs. Calls MCP-005-T1 to log the save event.  
**Traces To:** FR-008, MCP-001, MCP-005

---

### WF-011 — Explanation Node & Final Status
**Node:** `explanation`  
**Description:** Invokes AR-005. Assigns final case status. Calls MCP-006-T2 to notify caseworker if status is READY_FOR_CASEWORKER_REVIEW. If final status requires human review, routes to WF-012.  
**Traces To:** AR-005, HITL-005, MCP-006

---

### WF-012 — Human Review Queue Node
**Node:** `human_review_queue`  
**Description:** Calls MCP-006-T1 to place the case in the human review queue. Calls MCP-006-T3 if riskLevel is Critical. Calls MCP-005-T3 to log the escalation reason. Updates case status. Workflow pauses; resumes when a human reviewer submits action via API-006.  
**Traces To:** HITL-001 through HITL-005, MCP-006

---

### WF-013 — End
**Node:** `end`  
**Description:** Case is in final status. No further agent processing. Audit trail is complete.  
**Traces To:** FR-010, FR-011

---

## 13. Deployment Requirements (DEP)

### DEP-001 — Local Development Stack
**Title:** LocalStack-Based Local Environment  
**Description:** The complete system must run locally using LocalStack for AWS services (DynamoDB, S3, API Gateway, Lambda). A single command (e.g., `docker-compose up`) must start all required services. All environment-specific configuration must be in a `.env` file.  
**Priority:** Must  
**Source:** technical_requirement.md §12  
**Traces To:** NFR-005

---

### DEP-002 — Environment Configuration
**Title:** Environment Variables  
**Description:** The following environment variables must be supported:

| Variable | Description |
|----------|-------------|
| `AWS_ENDPOINT_URL` | LocalStack endpoint URL |
| `AWS_REGION` | AWS region (e.g., us-east-1) |
| `AWS_ACCESS_KEY_ID` | LocalStack dummy key |
| `AWS_SECRET_ACCESS_KEY` | LocalStack dummy secret |
| `LLM_MODEL_ID` | LLM model ID (default: `claude-opus-4-7`) |
| `LLM_PROVIDER` | LLM provider (default: `anthropic`) |
| `ANTHROPIC_API_KEY` | API key for Anthropic |
| `CONFIDENCE_THRESHOLD_INTAKE` | Min confidence to proceed from intake (default: 0.3) |
| `CONFIDENCE_THRESHOLD_RISK` | Min confidence to proceed from risk assessment (default: 0.6) |
| `CONFIDENCE_THRESHOLD_BIAS` | Min confidence to confirm fairness (default: 0.7) |
| `DATA_QUALITY_THRESHOLD` | Min quality score to proceed (default: 0.5) |
| `S3_BUCKET_NAME` | S3 bucket for document storage |

**Priority:** Must  
**Source:** technical_requirement.md §12, §19

---

### DEP-003 — Path to AWS AgentCore
**Title:** Cloud Migration Path  
**Description:** The architecture must be designed so that LocalStack services can be replaced by real AWS services (DynamoDB, S3, API Gateway, Lambda) by changing environment variables only. No code changes should be required to switch from LocalStack to AWS.  
**Priority:** Should  
**Source:** technical_requirement.md §12  
**Traces To:** NFR-005

---

## 14. Test Requirements (TEST)

All test cases must be documented in a `README.md` file within the code repository. The system must be deployed and tested iteratively on LocalStack before handoff. Test cases are grouped by category; IDs are sequential across all categories.

---

### Category A — Session & API Layer

#### TEST-001 — Session Creation Happy Path
**Test Case:** Call `POST /intake/session` with `{ "reporterType": "teacher" }`. Assert: HTTP 200 returned; `caseId` is present and matches pattern `CW-YYYY-NNNN`; IntakeCases record exists in DynamoDB with status=IN_PROGRESS and createdAt/updatedAt populated.  
**Traces To:** API-001, DB-001, FR-001

---

#### TEST-016 — Session Creation — Missing reporterType Field
**Test Case:** Call `POST /intake/session` with an empty body `{}`. Assert: HTTP 400 returned with a validation error message. No DynamoDB record is created.  
**Traces To:** API-001, NFR-005

---

#### TEST-017 — Session Creation — Malformed JSON Body
**Test Case:** Call `POST /intake/session` with body `not-json`. Assert: HTTP 400 returned. No DynamoDB record is created.  
**Traces To:** API-001

---

#### TEST-018 — Case ID Format Uniqueness
**Test Case:** Create two sessions back-to-back. Assert that both caseIds are different and each follows the `CW-YYYY-NNNN` format with the correct current year.  
**Traces To:** FR-001, DB-001

---

#### TEST-019 — Submit Message to Non-Existent Case
**Test Case:** Call `POST /intake/message` with a caseId that was never created. Assert: HTTP 404 returned. No DynamoDB writes occur.  
**Traces To:** API-002

---

#### TEST-020 — Submit Message to Completed Case
**Test Case:** Complete an intake session to final status. Then call `POST /intake/message` again on the same caseId. Assert: HTTP 409 Conflict returned. Case record is not modified.  
**Traces To:** API-002, FR-010

---

### Category B — Intake Message Submission

#### TEST-002 — Structured Field Extraction — Happy Path
**Test Case:** Submit the narrative: "I am a teacher. One of my students came to school with visible injury and seemed scared to go home." Assert that the Intake Understanding Agent extracts at minimum: reporterRelationship=Teacher, concernType containing physical harm, urgencyIndicators non-empty. Each extracted field has a confidence score between 0 and 1.  
**Traces To:** AR-001, FR-003

---

#### TEST-003 — Follow-Up Question Generation
**Test Case:** Following TEST-002, assert that the API response includes followUpQuestions for at least three of: childName, childDob, address, guardianInfo. Assert questions are human-readable sentences, not field-name tokens.  
**Traces To:** FR-004, AR-001, BR-004

---

#### TEST-021 — Submit Empty Message Text
**Test Case:** Call `POST /intake/message` with `messageText: ""`. Assert: HTTP 400 returned. Agent is not invoked. No IntakeMessages record written.  
**Traces To:** API-002

---

#### TEST-022 — Submit Extremely Long Message (>10,000 Characters)
**Test Case:** Call `POST /intake/message` with a messageText of 15,000 characters of plausible narrative text. Assert: HTTP 200 returned; agent processes without crash; extracted fields and confidence scores are present in the response.  
**Traces To:** API-002, AR-001, NFR-001

---

#### TEST-023 — Submit Message with XSS Payload
**Test Case:** Call `POST /intake/message` with `messageText: "<script>alert('xss')</script> The child was seen."`. Assert: message is stored in IntakeMessages as literal text. The API response agentResponse field contains no executable script tags.  
**Traces To:** API-002, DB-002

---

#### TEST-024 — Submit Non-English Language Narrative
**Test Case:** Submit a narrative in Spanish: "Soy maestra. Mi estudiante llegó con una lesión visible y parecía tener miedo de volver a casa." Assert: agent attempts extraction; response returns followUpQuestions; overallConfidenceScore is a number (not null). System does not crash.  
**Traces To:** AR-001, FR-003

---

#### TEST-025 — Submit Whitespace-Only Message
**Test Case:** Call `POST /intake/message` with `messageText: "   \n\t  "`. Assert: HTTP 400 returned. Agent is not invoked.  
**Traces To:** API-002

---

### Category C — Document Upload

#### TEST-004 — File Upload Happy Path
**Test Case:** Upload a sample PDF (containing readable text) to `POST /intake/upload` with valid caseId and documentCategory="incident-report". Assert: HTTP 200 with documentId; S3 object created in LocalStack; IntakeDocuments record written with fileName, fileType, storagePath, and extractionStatus=complete or pending.  
**Traces To:** FR-002, API-003, DB-003

---

#### TEST-026 — Upload to Non-Existent Case
**Test Case:** Upload a file with a caseId that does not exist. Assert: HTTP 404. No S3 object created. No IntakeDocuments record created.  
**Traces To:** API-003

---

#### TEST-027 — Upload Unsupported File Type
**Test Case:** Upload a file with extension `.exe`. Assert: HTTP 400 with message indicating unsupported file type. No S3 object or DynamoDB record created.  
**Traces To:** API-003, BR-002

---

#### TEST-028 — Upload Zero-Byte File
**Test Case:** Upload a file of 0 bytes. Assert: HTTP 400 or the system returns an extractionStatus=failed with a clear reason. System does not crash.  
**Traces To:** API-003

---

#### TEST-029 — Upload Corrupted PDF
**Test Case:** Upload a file with `.pdf` extension but corrupted binary contents. Assert: documentId returned; IntakeDocuments record written with extractionStatus=failed and extractionConfidence=0. Agent gracefully notes document as unreadable.  
**Traces To:** FR-002, AR-001, DB-003

---

#### TEST-030 — Upload Image with No Readable Text
**Test Case:** Upload a JPEG image of a plain white background. Assert: IntakeDocuments record created; extractedText is empty or null; extractionConfidence is 0 or very low. System does not crash or escalate solely on this.  
**Traces To:** FR-002, DB-003

---

#### TEST-031 — Upload After Case Reaches Final Status
**Test Case:** Complete an intake session to a final status. Then attempt to upload a document to the same caseId. Assert: HTTP 409 Conflict. No new S3 object or IntakeDocuments record created.  
**Traces To:** API-003, FR-010

---

### Category D — Intake Understanding Agent

#### TEST-032 — Conflicting Information in Narrative — Escalation
**Test Case:** Submit a narrative containing directly contradictory critical facts: "The child is 5 years old. The child is a 16-year-old teenager." Assert: escalate=true in agent output; escalationReason is non-empty; case is routed to human review queue.  
**Traces To:** AR-001, HITL-001

---

#### TEST-033 — All Required Fields Present in First Message
**Test Case:** Submit a single narrative that contains all required fields (child name, DOB, address, guardian info, reporter info, concern type, incident description). Assert: followUpQuestions is empty or null; missingRequiredFields is empty; workflow proceeds directly to risk assessment without re-entering the follow-up loop.  
**Traces To:** AR-001, WF-003, FR-004

---

#### TEST-034 — Anonymous Reporter
**Test Case:** Submit a narrative: "I don't want to give my name. A child at 123 Main Street has visible bruises and the parents seem threatening." Assert: reporterInfo=null; the system does not escalate solely due to missing reporter identity; follow-up asks for reporter relationship but does not block progress.  
**Traces To:** AR-001, FR-004

---

#### TEST-035 — Multiple Children Mentioned in Narrative
**Test Case:** Submit: "Two children, a 6-year-old boy and a 4-year-old girl, both showed signs of neglect." Assert: agent either extracts both children as separate concern entries or asks a clarifying follow-up question. System does not crash or silently pick one child.  
**Traces To:** AR-001, BR-003

---

#### TEST-036 — Reporter Answers "I Don't Know" to Follow-Up
**Test Case:** After receiving a follow-up question for childDob, submit the answer "I don't know." Assert: childDob remains null; the agent records the answer attempt in follow-up history; workflow does not loop infinitely on the same question.  
**Traces To:** AR-001, FR-004, WF-003

---

#### TEST-037 — Follow-Up Loop Exceeds Maximum Rounds
**Test Case:** Configure or simulate a scenario where critical fields remain missing after 5 rounds of follow-up. Assert: on the 6th invocation the agent sets escalate=true with escalationReason referencing max follow-up rounds exceeded; case is routed to human review with status NEEDS_MORE_INFORMATION.  
**Traces To:** AR-001, HITL-001, WF-003

---

#### TEST-038 — All Uploaded Documents Have Empty Extracted Text
**Test Case:** Attach three documents to a session, all with extractedText=null. Submit a minimal narrative. Assert: agent proceeds using only narrative text; documentExtractionResults are reflected in the lower confidence scores; no escalation triggered solely by empty documents unless combined with missing critical fields.  
**Traces To:** AR-001, FR-003, DB-003

---

#### TEST-039 — Urgent Danger Signal with Missing Identity and Location
**Test Case:** Submit: "A child is being beaten right now. I don't know who they are or where they live." Assert: escalate=true; escalationReason mentions immediate danger + missing identity/location; case is immediately routed to human review without completing the follow-up loop.  
**Traces To:** AR-001, HITL-001, WF-003

---

#### TEST-040 — Follow-Up Answer Contradicts Original Narrative
**Test Case:** Initial narrative states address as "45 Oak Street." Follow-up answer for address is "No, it's 12 Pine Avenue." Assert: inconsistency is detected and noted in the structuredFields or escalation reason; the newer value is used or the contradiction is flagged for human review.  
**Traces To:** AR-001, AR-003, FR-004

---

### Category E — Risk Assessment Agent

#### TEST-005 — Risk Assessment Output Structure
**Test Case:** Provide a complete set of structured intake fields. Assert: agent returns riskLevel (one of Low/Medium/High/Critical), confidenceScore (0.0–1.0), urgency (non-empty string), and riskFactors (non-empty list). All fields are present and correctly typed.  
**Traces To:** AR-002, FR-005

---

#### TEST-006 — Critical Risk Always Escalates
**Test Case:** Provide intake data designed to yield riskLevel=Critical (e.g., infant, immediate physical danger, prior referrals, household instability all present). Assert: escalate=true regardless of confidenceScore; case status is set to CRITICAL_IMMEDIATE_REVIEW; AuditEvents record written.  
**Traces To:** HITL-002, HITL-007, WF-005

---

#### TEST-041 — Risk Assessment for Infant (Age < 1)
**Test Case:** Submit intake with childAge=0 (infant) and a concern type of physical harm. Assert: age factor appears in riskFactors; riskLevel is at least Medium; urgency reflects the elevated vulnerability of a very young child.  
**Traces To:** AR-002, BR-006

---

#### TEST-042 — Risk Assessment with All Maximum Risk Factors
**Test Case:** Provide intake with: infant age, severe physical harm, immediate danger indicator, prior referrals found via MCP-003, household instability present. Assert: riskLevel=Critical, escalate=true, all five contributing factor types appear in riskFactors list.  
**Traces To:** AR-002, BR-006, HITL-002

---

#### TEST-043 — Low-Severity Case Produces Low Risk Without Escalation
**Test Case:** Submit: teenager (age 16), concern type=truancy concern, no urgency indicators, no prior referrals, complete data, dataQualityScore=0.9. Assert: riskLevel=Low, confidenceScore > 0.6, escalate=false. Workflow continues without routing to human review.  
**Traces To:** AR-002, WF-005

---

#### TEST-044 — Prior Referral History Increases Risk Level
**Test Case:** Provide two otherwise-identical intake cases: one with MCP-003 returning prior referrals and one returning none. Assert: the case with prior referrals has a higher riskLevel or higher confidenceScore; prior referrals appear in riskFactors.  
**Traces To:** AR-002, MCP-003, BR-006

---

#### TEST-045 — Risk Confidence at Exact Boundary (0.6)
**Test Case:** Craft a scenario where the agent's confidenceScore is exactly 0.60. Assert: because the threshold is `< 0.6` (strictly less than), a confidenceScore of 0.60 does NOT trigger escalation. Workflow continues to data quality stage.  
**Traces To:** AR-002, NFR-004, DEP-002

---

#### TEST-046 — MCP Case History Tool Returns Timeout Error
**Test Case:** Simulate MCP-003 `get_prior_referrals` returning a timeout/error. Assert: the agent handles the error gracefully; escalationReason notes that prior history was unavailable; riskLevel is still computed from available data; case is escalated to human review with reason "prior history lookup failed."  
**Traces To:** AR-002, MCP-003, HITL-002

---

#### TEST-047 — High Risk with Poor Data Quality Escalates
**Test Case:** Submit intake yielding riskLevel=High with dataQualityScore=0.4 (below 0.5 threshold). Assert: escalate=true; escalationReason notes high risk with insufficient data quality; case routed to ESCALATED_TO_SUPERVISOR.  
**Traces To:** AR-002, HITL-002, WF-005

---

#### TEST-048 — High Risk, Good Data Quality Does Not Escalate at Risk Gate
**Test Case:** Submit intake yielding riskLevel=High, confidenceScore=0.85, dataQualityScore=0.85. Assert: escalate=false at risk gate; workflow proceeds to data quality agent. (Note: HITL-007 will still require human review before final approval.)  
**Traces To:** AR-002, WF-005, HITL-007

---

### Category F — Data Quality Agent

#### TEST-007 — Data Quality Score with Missing Non-Critical Fields
**Test Case:** Submit intake where non-critical fields (e.g., priorConcerns, reporterInfo) are null but all critical fields (childName, address, concernType) are present. Assert: dataQualityScore is between 0 and 1 (not 0 or 1); missingCriticalFields is empty; readyForReview=true.  
**Traces To:** AR-003, FR-006

---

#### TEST-051 — All Fields Complete and Consistent
**Test Case:** Provide structuredFields where all required fields are populated, child age matches DOB, and documents corroborate text. Assert: dataQualityScore >= 0.85; missingCriticalFields is empty; inconsistencies is empty; readyForReview=true.  
**Traces To:** AR-003, FR-006

---

#### TEST-052 — Age and DOB Inconsistency Detected
**Test Case:** Provide structuredFields with childAge=8 but childDob indicating the child is 12. Assert: inconsistencies list contains an entry referencing both the age and DOB fields with a detail explaining the mismatch. readyForReview may still be true unless inconsistency is critical.  
**Traces To:** AR-003, BR-007

---

#### TEST-053 — Document Text Contradicts User-Supplied Address
**Test Case:** User says address is "45 Oak Street" but extracted document text contains "12 Pine Avenue." Assert: inconsistencies list contains entry for the address field. If address is critical, escalate=true is considered.  
**Traces To:** AR-003, BR-007, HITL-003

---

#### TEST-054 — Data Quality Score at Exact Threshold Boundary (0.5)
**Test Case:** Craft a scenario where the computed dataQualityScore is exactly 0.50. Assert: because the threshold is `< 0.5` (strictly less than), a score of exactly 0.50 does NOT trigger escalation.  
**Traces To:** AR-003, NFR-004, DEP-002

---

#### TEST-055 — Non-Critical Fields Missing Do Not Block Review
**Test Case:** All critical fields present; optional fields (priorConcerns, reporterInfo) absent. Assert: readyForReview=true; escalate=false; workflow continues to bias monitoring.  
**Traces To:** AR-003, WF-007

---

#### TEST-056 — Critical Field Missing After Max Follow-Up Rounds
**Test Case:** Simulate a case where childAddress remains null after 5 follow-up rounds. Assert: escalate=true on the next quality check; escalationReason references missing critical field and exhausted follow-up; case routed to NEEDS_MORE_INFORMATION.  
**Traces To:** AR-003, HITL-003

---

#### TEST-057 — All Document Extraction Confidence Below 0.4
**Test Case:** Provide documentExtractionResults where all documents have extractionConfidence < 0.4. Assert: inconsistencies or missingCriticalFields reflect the low-confidence document data; dataQualityScore is lowered accordingly; quality agent does not silently accept document-derived values as reliable.  
**Traces To:** AR-003, BR-007

---

#### TEST-058 — Empty Structured Fields Input
**Test Case:** Invoke the Data Quality Agent with structuredFields={}. Assert: dataQualityScore=0 (or near 0); missingCriticalFields contains all required fields; readyForReview=false; escalate=true with reason "no intake data present."  
**Traces To:** AR-003, NFR-004

---

### Category G — Bias Monitoring Agent

#### TEST-008 — Neighbourhood Socioeconomic Proxy Language
**Test Case:** Provide riskFactors=["Family lives in a high-crime area", "Neighbourhood associated with poverty"]. Assert: biasStatus=Flagged; humanReviewRequired=true; flags list contains a socioeconomic-proxy flag; case routed to BIAS_REVIEW_REQUIRED.  
**Traces To:** AR-004, HITL-004, WF-009

---

#### TEST-059 — Clean Risk Factors Pass Bias Check
**Test Case:** Provide riskFactors=["Physical harm indicators described by reporter", "Child is under 5 years old", "Prior referrals found"]. Assert: biasStatus=Passed; humanReviewRequired=false; flags list is empty; workflow continues to save stage.  
**Traces To:** AR-004, WF-009

---

#### TEST-060 — Race or Ethnicity Referenced in Risk Explanation
**Test Case:** Provide riskFactors=["Child belongs to a minority ethnic group commonly associated with neglect cases"]. Assert: biasStatus=Flagged; flags entry contains type="demographic"; humanReviewRequired=true.  
**Traces To:** AR-004, BR-008, HITL-004

---

#### TEST-061 — Reporter Relationship Used as Negative Risk Amplifier
**Test Case:** Provide riskFactors=["Reporter is a family member, making this report less credible"]. Assert: biasStatus=Flagged; flags entry contains type="reporter-bias"; humanReviewRequired=true.  
**Traces To:** AR-004, BR-008

---

#### TEST-062 — Language or Accent Referenced in Risk Explanation
**Test Case:** Provide riskFactors=["Reporter's limited English suggests credibility issues with the account"]. Assert: biasStatus=Flagged; flags entry contains type="language-bias"; humanReviewRequired=true.  
**Traces To:** AR-004, BR-008

---

#### TEST-063 — Bias Confidence at Exact Threshold Boundary (0.7)
**Test Case:** Craft a scenario where biasConfidence is exactly 0.70. Assert: because the threshold is `< 0.7` (strictly less than), a biasConfidence of 0.70 does NOT trigger escalation due to low confidence alone.  
**Traces To:** AR-004, NFR-004, DEP-002

---

#### TEST-064 — Multiple Simultaneous Bias Flags
**Test Case:** Provide riskFactors containing both a neighbourhood proxy and a language-bias reference. Assert: both flags appear in the flags list with distinct types; biasStatus=Flagged; all flags are preserved in the AgentOutputs record.  
**Traces To:** AR-004, DB-004

---

#### TEST-065 — Empty Risk Factors List
**Test Case:** Provide riskAssessmentOutput with riskFactors=[]. Assert: biasStatus=Passed; biasConfidence=1.0 (nothing to flag); humanReviewRequired=false. Workflow continues.  
**Traces To:** AR-004

---

---

### Category H — Explanation Agent

#### TEST-009 — Explanation Agent Full Output
**Test Case:** After a successful pipeline run, call `GET /cases/{caseId}/summary`. Assert: caseworkerSummary, riskExplanation (list), recommendation, limitations (list), and nextAction are all non-empty. finalCaseStatus matches the actual case status in IntakeCases.  
**Traces To:** AR-005, FR-009

---

#### TEST-066 — Low Risk Clean Case Produces Concise Summary
**Test Case:** Run a pipeline for a Low risk, all-Passed case. Assert: caseworkerSummary is concise (does not include escalation language); recommendation reflects routine follow-up; limitations list is short; humanReviewRequired=false.  
**Traces To:** AR-005, FR-009

---

#### TEST-067 — Escalated Case Explanation Includes Escalation Reason
**Test Case:** Run a pipeline that reaches the human review queue. After human review, call the summary endpoint. Assert: humanReviewRequired=true (or was=true); humanReviewReason is a non-empty string explaining why human review was triggered.  
**Traces To:** AR-005, HITL-005

---

#### TEST-068 — Explanation When a Prior Agent Errored
**Test Case:** Simulate one AgentOutputs record with status=error for the bias-monitoring agent. Invoke the Explanation Agent. Assert: limitations list contains a statement about the bias monitoring stage being unavailable; caseworkerSummary does not claim bias was checked; humanReviewRequired=true.  
**Traces To:** AR-005, NFR-004

---

#### TEST-069 — High Risk and Low Data Quality Creates Noted Contradiction
**Test Case:** Provide riskAssessmentOutput with riskLevel=High and dataQualityOutput with dataQualityScore=0.4. Assert: caseworkerSummary or limitations explicitly notes that the high risk assessment is based on incomplete data; recommendation is cautious.  
**Traces To:** AR-005, BR-010

---

#### TEST-070 — Critical Case Summary Uses Urgent Language
**Test Case:** Provide inputs where finalCaseStatus=CRITICAL_IMMEDIATE_REVIEW. Assert: nextAction contains language indicating immediate response (e.g., "immediate", "within hours"); recommendation does not use routine language.  
**Traces To:** AR-005, BR-010

---

### Category I — Human-in-the-Loop Flows

#### TEST-010 — Human Reviewer Overrides Risk Level
**Test Case:** Escalate a case with riskLevel=High. Submit human-review action `override` with overrideRiskLevel=Low and notes="Reviewed in person, situation resolved." Assert: IntakeCases riskLevel updated to Low; AuditEvents record with eventType=human-override written; beforeState.riskLevel=High; afterState.riskLevel=Low.  
**Traces To:** HITL-006, FR-012, API-006, DB-005

---

#### TEST-013 — Low Confidence Intake Escalation
**Test Case:** Submit a completely unintelligible or contradictory narrative that forces overallConfidenceScore < 0.3. Assert: escalate=true; case is routed to human review; final case status is LOW_CONFIDENCE_REVIEW_REQUIRED or NEEDS_MORE_INFORMATION.  
**Traces To:** HITL-001, AR-001

---

#### TEST-071 — Post-Intake Escalation Produces Correct Status
**Test Case:** Trigger escalation from the Intake Understanding Agent due to low confidence (TEST-013 scenario). Assert: case status=LOW_CONFIDENCE_REVIEW_REQUIRED (not BIAS_REVIEW_REQUIRED or CRITICAL_IMMEDIATE_REVIEW); escalationReason in AuditEvents matches the intake escalation trigger.  
**Traces To:** HITL-001, WF-003, FR-010

---

#### TEST-072 — Post-Risk Escalation for High Risk with Poor Data Quality
**Test Case:** Trigger escalation from the Risk gate (riskLevel=High, dataQualityScore=0.4). Assert: case status=ESCALATED_TO_SUPERVISOR; AuditEvents escalation event references both the risk level and the data quality score.  
**Traces To:** HITL-002, WF-005, AR-002

---

#### TEST-073 — Post-Quality Escalation After Max Follow-Up
**Test Case:** Trigger escalation from the Data Quality gate (critical field never supplied). Assert: case status=NEEDS_MORE_INFORMATION; both the quality agent escalation reason and the max-rounds reason appear in AuditEvents.  
**Traces To:** HITL-003, WF-007

---

#### TEST-074 — Post-Bias Escalation Produces Correct Status
**Test Case:** Trigger bias flag (TEST-008 scenario). Assert: case status=BIAS_REVIEW_REQUIRED (not ESCALATED_TO_SUPERVISOR or other status); biasStatus=Flagged is recorded in IntakeCases.  
**Traces To:** HITL-004, WF-009, FR-010

---

#### TEST-075 — Human Reviewer Approves Escalated Case
**Test Case:** Case is in status ESCALATED_TO_SUPERVISOR. Human reviewer submits action=approve with notes. Assert: case status updated to READY_FOR_CASEWORKER_REVIEW; AuditEvents human-override event written with actor=reviewer; case appears in caseworker dashboard.  
**Traces To:** HITL-006, FR-012, API-006

---

#### TEST-076 — Human Reviewer Requests More Information
**Test Case:** Case is in human review queue. Human reviewer submits action=request_more_info with notes="Need to verify guardian identity." Assert: case status=NEEDS_MORE_INFORMATION; AuditEvents record written; reporter is (conceptually) notified to provide more information.  
**Traces To:** HITL-006, FR-012, MCP-006

---

#### TEST-077 — Human Review Action on Non-Escalated Case
**Test Case:** Take a case that is in status=IN_PROGRESS (not yet escalated). Call `POST /cases/{caseId}/human-review`. Assert: HTTP 409 Conflict returned. Case status is not changed. No AuditEvents record written for this invalid attempt.  
**Traces To:** API-006, HITL-006

---

#### TEST-078 — HITL-007 Enforcement: High Risk Cannot Be Auto-Finalized
**Test Case:** Attempt to programmatically set a High risk case to READY_FOR_CASEWORKER_REVIEW (bypass the human review queue). Assert: the system rejects this state transition; status cannot move directly from a High risk escalated state to READY_FOR_CASEWORKER_REVIEW without a human-review action.  
**Traces To:** HITL-007, HITL-002, WF-005

---

#### TEST-079 — Concurrent Human Review Actions on Same Case
**Test Case:** Two reviewers simultaneously submit review actions for the same caseId (simulated concurrent requests). Assert: exactly one request succeeds (HTTP 200); the second returns HTTP 409 Conflict. The AuditEvents table contains exactly one human-override event for the case. Case status reflects only the winning action.  
**Traces To:** HITL-006, NFR-003

---

### Category J — LangGraph Workflow Routing

#### TEST-011 — Audit Trail Completeness Across All Nodes
**Test Case:** Run a full pipeline (including escalation and human review). Retrieve all AuditEvents for the caseId. Assert events exist with eventType entries covering: field-extraction (intake node), state-transition (each gate), agent-decision (each agent), escalation (human review routing), and human-override (reviewer action). No node is missing from the trail.  
**Traces To:** FR-011, NFR-006, DB-005

---

#### TEST-080 — Happy Path Traverses Nodes in Correct Order
**Test Case:** Run a full pipeline that passes all gates. From AuditEvents, verify the state-transition events appear in order: intake_understanding → risk_assessment → data_quality → bias_monitoring → save_intake → explanation → end. No node is visited out of sequence.  
**Traces To:** WF-001 through WF-013, NFR-006

---

#### TEST-081 — Follow-Up Loop Re-Enters Intake Node Correctly
**Test Case:** Submit an initial narrative missing three required fields. After receiving follow-up questions, answer one field. Assert: the next API call re-invokes the intake_understanding node; structuredFields in the new output includes the newly provided field; remaining missing fields generate new follow-up questions.  
**Traces To:** WF-002, WF-003, FR-004

---

#### TEST-082 — No Follow-Up Loop When Fields Are Complete
**Test Case:** Submit a narrative containing all required fields (TEST-033). Assert from AuditEvents: follow_up_router node transitions directly to risk_assessment node; no re-invocation of intake_understanding occurs before risk assessment.  
**Traces To:** WF-003, WF-004

---

#### TEST-083 — Critical Risk Bypasses Quality and Bias Gates
**Test Case:** Run a pipeline with riskLevel=Critical. Assert from AuditEvents: workflow routes directly from risk_gate to human_review_queue; data_quality and bias_monitoring nodes are NOT executed before the human review routing.  
**Traces To:** WF-005, HITL-002, HITL-007

---

#### TEST-084 — Agent Exception Routes to Human Review
**Test Case:** Simulate the Risk Assessment Agent throwing an unhandled exception. Assert: workflow catches the error; case is routed to human_review_queue; AuditEvents contains an escalation event with reason referencing the agent error; case status is ESCALATED_TO_SUPERVISOR or LOW_CONFIDENCE_REVIEW_REQUIRED (not left as IN_PROGRESS).  
**Traces To:** WF-005, HITL-002, NFR-004

---

#### TEST-085 — Quality Gate Loops Back When Not Ready
**Test Case:** First data quality check returns readyForReview=false and escalate=false (some critical fields missing but follow-up rounds not exhausted). Assert from AuditEvents: quality_gate transitions back to follow_up_router; the next user message re-runs intake_understanding. Loop terminates after the field is supplied.  
**Traces To:** WF-007, WF-003

---

#### TEST-086 — Workflow State Is Isolated Per Case
**Test Case:** Run two concurrent intake sessions (caseId-A and caseId-B) with different narratives. Assert: structuredFields, agentOutputs, and AuditEvents for caseId-A contain no data from caseId-B's session and vice versa.  
**Traces To:** WF-001, DB-001, NFR-005

---

### Category K — Database & Persistence

#### TEST-092 — AuditEvents Sort Key Uniqueness for Simultaneous Events
**Test Case:** Write two AuditEvents for the same caseId at the exact same millisecond (simulated). Assert: both records are stored; the sort keys are unique (ISO8601 + UUID suffix prevents collision); neither record overwrites the other.  
**Traces To:** DB-005, NFR-003

---

#### TEST-093 — IntakeCases Update Preserves createdAt
**Test Case:** Update an IntakeCases record (change status, riskLevel). Retrieve the record. Assert: createdAt value is identical to the value at session creation time; updatedAt reflects the latest change timestamp.  
**Traces To:** DB-001

---

#### TEST-094 — AgentOutputs Appends on Multiple Invocations
**Test Case:** Run the intake_understanding agent twice on the same case (two follow-up rounds). Assert: AgentOutputs table contains two records for the case with the same PK (caseId) but different SK (agentName#timestamp). Neither record overwrites the other.  
**Traces To:** DB-004, MCP-005

---

#### TEST-095 — IntakeDocuments Created Even on Extraction Failure
**Test Case:** Upload a corrupted PDF (TEST-029). Assert: IntakeDocuments record is written with extractionStatus=failed; storagePath is populated (file is stored); extractedText is null. The record exists for audit purposes.  
**Traces To:** DB-003, BR-009

---

#### TEST-096 — IntakeMessages Stores Correct Sender and Type
**Test Case:** After one round of intake (user narrative + agent follow-up), query IntakeMessages for the case. Assert: user narrative message has senderType=user and messageType=narrative; agent follow-up message has senderType=agent, agentGenerated=true, and messageType=follow-up-question.  
**Traces To:** DB-002, FR-004

---

### Category L — API Validation & Error Handling

#### TEST-014 — Caseworker Case List API
**Test Case:** Create at least 3 intake cases with different risk levels. Call `GET /cases`. Assert: all three cases appear in the response; each has correct riskLevel and status fields; pagination metadata is present.  
**Traces To:** FR-013, API-005

---

#### TEST-097 — Empty Case List Returns 200 Not 404
**Test Case:** On a clean LocalStack environment with no cases, call `GET /cases`. Assert: HTTP 200 returned with an empty list (e.g., `{ "cases": [], "totalCount": 0 }`). Not a 404 or 500.  
**Traces To:** API-005, FR-013

---

#### TEST-098 — Case List Pagination Returns Correct Page
**Test Case:** Create 15 cases. Call `GET /cases?page=2&pageSize=5`. Assert: response contains cases 6–10 (second page); first-page items are not repeated; totalCount reflects all 15 cases.  
**Traces To:** API-005, FR-013

---

#### TEST-099 — Case List Filter by Risk Level
**Test Case:** Create cases with riskLevel=Low, Medium, and High. Call `GET /cases?riskLevel=High`. Assert: only the High risk case is returned; Low and Medium cases are excluded.  
**Traces To:** API-005, FR-013

---

#### TEST-100 — Case List Filter by Status
**Test Case:** Create cases with status=IN_PROGRESS and status=CRITICAL_IMMEDIATE_REVIEW. Call `GET /cases?status=CRITICAL_IMMEDIATE_REVIEW`. Assert: only the CRITICAL_IMMEDIATE_REVIEW case is returned.  
**Traces To:** API-005, FR-013

---

#### TEST-101 — Human Review Action with Invalid Action Value
**Test Case:** Call `POST /cases/{caseId}/human-review` with `action="delete_case"` (not a valid enum value). Assert: HTTP 400 returned with a message identifying the invalid action value. Case status is not changed.  
**Traces To:** API-006

---

#### TEST-102 — Non-Existent Case ID Returns 404 Not 500
**Test Case:** Call `GET /intake/FAKE-CASE-ID`, `GET /cases/FAKE-CASE-ID/summary`, and `POST /cases/FAKE-CASE-ID/human-review`. Assert: all three return HTTP 404. No Lambda crashes (no 500 errors).  
**Traces To:** API-002, API-004, API-006

---

#### TEST-103 — Malformed JSON on Any POST Endpoint
**Test Case:** Send `POST /intake/session` with body `{invalid json`. Assert: HTTP 400 returned with a parse error message. No DynamoDB writes occur.  
**Traces To:** API-001

---

#### TEST-104 — Request Body Exceeding 1MB
**Test Case:** Send `POST /intake/message` with a messageText of ~2MB of text. Assert: system returns HTTP 413 (Request Entity Too Large) or HTTP 400 with a size limit error. Lambda does not crash or timeout silently.  
**Traces To:** API-002, NFR-001

---

### Category M — Security & Input Safety

#### TEST-105 — NoSQL Injection in Message Text
**Test Case:** Submit messageText containing `{"$gt": "", "$where": "function(){return true;}"}`. Assert: the value is stored as a literal string in IntakeMessages; DynamoDB query behavior is not altered; agent receives the text as plain input without query manipulation.  
**Traces To:** API-002, DB-002

---

#### TEST-106 — XSS Payload Stored as Plain Text
**Test Case:** Submit messageText=`<script>alert('xss')</script>I am a teacher`. Assert: the string is stored verbatim in DynamoDB; when retrieved via `GET /intake/{caseId}`, the agentResponse and structuredFields contain escaped or literal text, never raw HTML that would execute in a browser.  
**Traces To:** API-002, DB-002, FE-006

---

#### TEST-107 — Path Traversal in Case ID URL Parameter
**Test Case:** Call `GET /intake/../../../etc/passwd`. Assert: HTTP 400 or 404 returned; no file system access is attempted; the Lambda does not expose any OS-level information.  
**Traces To:** API-004

---

#### TEST-108 — Injection Attempt in documentCategory Field
**Test Case:** Upload a file with documentCategory=`"; DROP TABLE IntakeCases; --"`. Assert: the value is stored as a literal string in IntakeDocuments.documentCategory; no DynamoDB table is affected; request completes normally or returns 400 if category is validated against an enum.  
**Traces To:** API-003, DB-003

---

#### TEST-109 — Oversized File Upload
**Test Case:** Upload a file exceeding 50MB. Assert: HTTP 413 returned or the system gracefully rejects the upload with a file-size error message. Memory usage does not spike; Lambda does not timeout silently.  
**Traces To:** API-003

---

### Category N — LLM Configuration & Threshold Behaviour

#### TEST-012 — LLM Model Replaceability
**Test Case:** Set `LLM_MODEL_ID=claude-haiku-4-5-20251001` in the environment. Run a full intake cycle. Assert: all five agents produce valid, correctly-structured JSON outputs; no hardcoded Opus model reference prevents the system from working.  
**Traces To:** AR-006, NFR-002, DEP-002

---

#### TEST-110 — Intake Confidence Threshold Environment Variable
**Test Case:** Set `CONFIDENCE_THRESHOLD_INTAKE=0.9`. Submit a narrative that would normally score 0.6 (not escalated at default 0.3). Assert: with the raised threshold, the agent now sets escalate=true and the case is routed to human review, demonstrating the threshold is read from env, not hardcoded.  
**Traces To:** AR-001, NFR-004, DEP-002

---

#### TEST-111 — Risk Confidence Threshold Environment Variable
**Test Case:** Set `CONFIDENCE_THRESHOLD_RISK=0.9`. Run a risk assessment that would normally score 0.75 (not escalated at default 0.6). Assert: with the raised threshold, escalate=true is set at the risk gate, demonstrating the threshold is configurable.  
**Traces To:** AR-002, NFR-004, DEP-002

---

#### TEST-112 — Missing ANTHROPIC_API_KEY Produces Clear Error
**Test Case:** Start the system without `ANTHROPIC_API_KEY` set. Attempt to invoke any agent. Assert: the system returns an informative error message identifying the missing API key, not a cryptic 500 crash. The error is logged in AuditEvents as an agent error.  
**Traces To:** AR-006, DEP-002

---

#### TEST-113 — Invalid API Key Handled Gracefully
**Test Case:** Set `ANTHROPIC_API_KEY=invalid_key`. Submit an intake message. Assert: the agent call fails with a clear authentication error; the workflow routes the case to human review with escalationReason noting LLM authentication failure; the system does not produce a 500 crash.  
**Traces To:** AR-006, HITL-002, WF-012

---

### Category O — LocalStack & Deployment

#### TEST-114 — Clean Startup from docker-compose up
**Test Case:** On a machine where LocalStack has not been previously started in this project, run `docker-compose up`. Assert: all five DynamoDB tables are created automatically; the S3 bucket defined in `S3_BUCKET_NAME` is created; all Lambda functions are deployed; the API Gateway is reachable at the configured port. No manual provisioning steps are required.  
**Traces To:** DEP-001, DEP-002, NFR-005

---

#### TEST-115 — DynamoDB Tables Auto-Created on Startup
**Test Case:** Start from a clean LocalStack state. Immediately call `POST /intake/session`. Assert: the IntakeCases table exists and the record is written. Repeat for each of the five tables by exercising the relevant API endpoints.  
**Traces To:** DEP-001, DB-001 through DB-005

---

#### TEST-116 — S3 Bucket Auto-Created on Startup
**Test Case:** Start from a clean LocalStack state. Call `POST /intake/upload` with a valid file. Assert: the S3 object is written to the bucket named by `S3_BUCKET_NAME`; the bucket was created automatically without manual CLI steps.  
**Traces To:** DEP-001, FR-002

---

#### TEST-117 — LocalStack Data Persists Across Restarts
**Test Case:** Create an intake session and submit a message. Stop LocalStack (`docker-compose down`), then restart (`docker-compose up`). Assert: the IntakeCases record and IntakeMessages record from before the restart are still present in DynamoDB (persistent volume mount is working).  
**Traces To:** DEP-001, NFR-005

---

### Category P — End-to-End Scenarios

#### TEST-015 — End-to-End Golden Path
**Test Case:** Run a complete intake scenario: (1) create session, (2) submit the teacher narrative, (3) upload a sample readable PDF, (4) answer follow-up questions, (5) verify pipeline runs to completion, (6) verify final status is READY_FOR_CASEWORKER_REVIEW, (7) retrieve caseworker summary — assert all explanation fields are non-empty, (8) retrieve AuditEvents — assert events exist for every workflow node.  
**Traces To:** All FR, AR, WF, HITL requirements

---

#### TEST-118 — End-to-End Worst-Case Path (Escalation at Every Stage)
**Test Case:** Engineer inputs that trigger escalation at: intake (conflicting info), then after human un-escalation trigger risk escalation (High risk, low quality), then after second human action trigger bias flag. Assert: each escalation is recorded with the correct status; the final approved case has a complete AuditEvents trail showing every escalation and reviewer action; final status is READY_FOR_CASEWORKER_REVIEW after all three human reviews.  
**Traces To:** HITL-001 through HITL-006, WF-012

---

#### TEST-119 — End-to-End with Document Upload Contributing Critical Fields
**Test Case:** Submit a minimal narrative (only concern type mentioned). Upload a PDF that contains the child's name, DOB, and address. Assert: after document extraction, the intake_understanding agent extracts these fields from the document; follow-up questions for name/DOB/address are not generated (already resolved); pipeline proceeds with higher confidence.  
**Traces To:** FR-002, FR-003, AR-001, WF-002

---

#### TEST-120 — End-to-End Low Risk Case Completes Without Escalation
**Test Case:** Submit a complete, low-risk intake (teenager, minor concern, all fields supplied, no history). Assert: no HITL routing occurs at any stage; finalCaseStatus=READY_FOR_CASEWORKER_REVIEW is set by the Explanation Agent; caseworker summary reflects a routine recommendation; AuditEvents contains no escalation events.  
**Traces To:** AR-001 through AR-005, HITL-001 through HITL-005, WF-013

---

#### TEST-121 — End-to-End Critical Case Resolved by Human Reviewer
**Test Case:** Submit intake yielding riskLevel=Critical. Verify case is routed to human review with status CRITICAL_IMMEDIATE_REVIEW. Human reviewer approves. Assert: case status transitions to READY_FOR_CASEWORKER_REVIEW; caseworker explanation reflects the critical risk level and the human review outcome; notify_supervisor was called (MCP-006-T3); AuditEvents trail is complete.  
**Traces To:** HITL-002, HITL-006, AR-005, MCP-006

---

#### TEST-122 — Concurrent Sessions Do Not Cross-Contaminate
**Test Case:** Run two complete intake sessions simultaneously for different cases (Case A: teacher scenario; Case B: medical worker scenario). Assert: structuredFields, agentOutputs, AuditEvents, and IntakeMessages for Case A contain no data from Case B and vice versa. Both cases complete successfully.  
**Traces To:** WF-001, DB-001, NFR-005

## 15. Requirement Traceability Matrix

| Req ID | Title | Traces From | Traces To |
|--------|-------|-------------|-----------|
| BR-001 | Chatbot Intake Interface | Business_requirement.md §3 | FR-001, FE-001, FE-002 |
| BR-002 | Multi-Modal Submission | Business_requirement.md §3 | FR-002, API-003, DB-003 |
| BR-003 | Unstructured-to-Structured | Business_requirement.md §4 | FR-003, AR-001 |
| BR-004 | Missing Data Follow-Up | Business_requirement.md §5 | FR-004, AR-001, WF-003 |
| BR-005 | Risk Assessment | Business_requirement.md §6 | FR-005, AR-002 |
| BR-006 | Risk Input Factors | Business_requirement.md §6 | AR-002 |
| BR-007 | Data Quality Validation | Business_requirement.md §7 | FR-006, AR-003 |
| BR-008 | Bias Monitoring | Business_requirement.md §8 | FR-007, AR-004 |
| BR-009 | Record Persistence | Business_requirement.md §9 | FR-008, DB-001 to DB-005 |
| BR-010 | Caseworker Explanation | Business_requirement.md §10 | FR-009, AR-005, FE-005 |
| BR-011 | Final Case Statuses | Business_requirement.md §11.5 | FR-010, DB-001 |
| BR-012 | Audit Trail | Business_requirement.md §9 | FR-011, DB-005 |
| FR-001 | Create Session | BR-001 | API-001, DB-001, WF-001 |
| FR-002 | Document Upload | BR-002 | API-003, DB-003, MCP-001 |
| FR-003 | Field Extraction | BR-003 | AR-001, MCP-003 |
| FR-004 | Follow-Up Loop | BR-004 | AR-001, WF-003, FE-002 |
| FR-005 | Risk Scoring | BR-005 | AR-002, MCP-004, WF-004 |
| FR-006 | Quality Scoring | BR-007 | AR-003, WF-006 |
| FR-007 | Bias Check | BR-008 | AR-004, WF-008 |
| FR-008 | Case Persistence | BR-009 | DB-001, DB-004, DB-005, MCP-001, WF-010 |
| FR-009 | Explanation Generation | BR-010 | AR-005, FE-005 |
| FR-010 | Final Status Assignment | BR-011 | DB-001, WF-011 |
| FR-011 | Audit Event Logging | BR-012 | DB-005, MCP-005 |
| FR-012 | Human Review Action | Business_requirement.md §11 | API-006, FE-007, DB-001 |
| FR-013 | Case List | Business_requirement.md §13 | API-005, FE-004 |
| FR-014 | Case Detail | Business_requirement.md §13 | API-004, FE-005, FE-006 |
| AR-001 | Intake Understanding Agent | FR-003, FR-004 | MCP-001, MCP-002, MCP-003, MCP-007, WF-002, WF-003 |
| AR-002 | Risk Assessment Agent | FR-005 | MCP-003, MCP-004, WF-004, WF-005 |
| AR-003 | Data Quality Agent | FR-006 | WF-006, WF-007 |
| AR-004 | Bias Monitoring Agent | FR-007 | MCP-005, MCP-007, WF-008, WF-009 |
| AR-005 | Explanation Agent | FR-009 | FE-005, WF-011 |
| AR-006 | LLM Replaceability | technical_requirement.md §19 | DEP-001 |
| HITL-001 | Post-Intake Escalation | Business_requirement.md §11.1 | WF-003, MCP-006, DB-001 |
| HITL-002 | Post-Risk Escalation | Business_requirement.md §11.2 | WF-005, MCP-006, DB-001 |
| HITL-003 | Post-Quality Escalation | Business_requirement.md §11.3 | WF-007, MCP-006, DB-001 |
| HITL-004 | Post-Bias Escalation | Business_requirement.md §11.4 | WF-009, MCP-006, DB-001 |
| HITL-005 | Final Routing Gate | Business_requirement.md §11.5 | AR-005, WF-011, FE-007 |
| HITL-006 | Human Override | Business_requirement.md §11 | FR-012, API-006, MCP-005 |
| HITL-007 | No Silent AI Finalization | Business_requirement.md §11.2 | WF-005, HITL-002 |
| WF-001 | Start Node | FR-001 | API-002 |
| WF-002 | Intake Understanding Node | AR-001 | MCP-001, MCP-005, MCP-007 |
| WF-003 | Follow-Up Router | FR-004, HITL-001 | AR-001 |
| WF-004 | Risk Assessment Node | AR-002 | MCP-003, MCP-004, MCP-005 |
| WF-005 | Risk Gate | HITL-002, HITL-007 | WF-006, WF-012 |
| WF-006 | Data Quality Node | AR-003 | MCP-005, MCP-007 |
| WF-007 | Quality Gate | HITL-003 | WF-008, WF-012 |
| WF-008 | Bias Monitoring Node | AR-004 | MCP-005, MCP-007 |
| WF-009 | Bias Gate | HITL-004 | WF-010, WF-012 |
| WF-010 | Save Final Record | FR-008 | MCP-001, MCP-005 |
| WF-011 | Explanation & Final Status | AR-005, HITL-005 | MCP-006 |
| WF-012 | Human Review Queue Node | HITL-001 to HITL-005 | MCP-006 |
| WF-013 | End | FR-010 | — |
| TEST-001 | Session Creation Happy Path | API-001, DB-001, FR-001 | — |
| TEST-002 | Extraction Happy Path | AR-001, FR-003 | — |
| TEST-003 | Follow-Up Question Generation | FR-004, AR-001, BR-004 | — |
| TEST-004 | File Upload Happy Path | FR-002, API-003, DB-003 | — |
| TEST-005 | Risk Assessment Output Structure | AR-002, FR-005 | — |
| TEST-006 | Critical Risk Always Escalates | HITL-002, HITL-007, WF-005 | — |
| TEST-007 | Data Quality Score with Missing Non-Critical Fields | AR-003, FR-006 | — |
| TEST-008 | Neighbourhood Socioeconomic Bias Flag | AR-004, HITL-004, WF-009 | — |
| TEST-009 | Explanation Agent Full Output | AR-005, FR-009 | — |
| TEST-010 | Human Reviewer Overrides Risk Level | HITL-006, FR-012, API-006, DB-005 | — |
| TEST-011 | Audit Trail Completeness Across All Nodes | FR-011, NFR-006, DB-005 | — |
| TEST-012 | LLM Model Replaceability | AR-006, NFR-002, DEP-002 | — |
| TEST-013 | Low Confidence Intake Escalation | HITL-001, AR-001 | — |
| TEST-014 | Caseworker Case List API | FR-013, API-005 | — |
| TEST-015 | End-to-End Golden Path | All FR, AR, WF, HITL | — |
| TEST-016 | Session Creation — Missing reporterType | API-001, NFR-005 | — |
| TEST-017 | Session Creation — Malformed JSON | API-001 | — |
| TEST-018 | Case ID Format Uniqueness | FR-001, DB-001 | — |
| TEST-019 | Submit Message to Non-Existent Case | API-002 | — |
| TEST-020 | Submit Message to Completed Case | API-002, FR-010 | — |
| TEST-021 | Submit Empty Message Text | API-002 | — |
| TEST-022 | Submit Extremely Long Message | API-002, AR-001, NFR-001 | — |
| TEST-023 | Submit Message with XSS Payload | API-002, DB-002 | — |
| TEST-024 | Non-English Language Narrative | AR-001, FR-003 | — |
| TEST-025 | Submit Whitespace-Only Message | API-002 | — |
| TEST-026 | Upload to Non-Existent Case | API-003 | — |
| TEST-027 | Upload Unsupported File Type | API-003, BR-002 | — |
| TEST-028 | Upload Zero-Byte File | API-003 | — |
| TEST-029 | Upload Corrupted PDF | FR-002, AR-001, DB-003 | — |
| TEST-030 | Upload Image with No Readable Text | FR-002, DB-003 | — |
| TEST-031 | Upload After Case Reaches Final Status | API-003, FR-010 | — |
| TEST-032 | Conflicting Information Triggers Escalation | AR-001, HITL-001 | — |
| TEST-033 | All Required Fields Present on First Message | AR-001, WF-003, FR-004 | — |
| TEST-034 | Anonymous Reporter | AR-001, FR-004 | — |
| TEST-035 | Multiple Children Mentioned | AR-001, BR-003 | — |
| TEST-036 | Reporter Answers "I Don't Know" to Follow-Up | AR-001, FR-004, WF-003 | — |
| TEST-037 | Follow-Up Loop Exceeds Maximum Rounds | AR-001, HITL-001, WF-003 | — |
| TEST-038 | All Documents Have Empty Extracted Text | AR-001, FR-003, DB-003 | — |
| TEST-039 | Urgent Danger + Missing Identity Triggers Immediate Escalation | AR-001, HITL-001, WF-003 | — |
| TEST-040 | Follow-Up Answer Contradicts Original Narrative | AR-001, AR-003, FR-004 | — |
| TEST-041 | Risk Assessment for Infant (Age < 1) | AR-002, BR-006 | — |
| TEST-042 | Risk Assessment with All Maximum Risk Factors | AR-002, BR-006, HITL-002 | — |
| TEST-043 | Low-Severity Case Produces Low Risk | AR-002, WF-005 | — |
| TEST-044 | Prior Referral History Increases Risk Level | AR-002, MCP-003, BR-006 | — |
| TEST-045 | Risk Confidence at Exact Boundary (0.6) | AR-002, NFR-004, DEP-002 | — |
| TEST-046 | MCP Case History Tool Timeout Error | AR-002, MCP-003, HITL-002 | — |
| TEST-047 | High Risk with Poor Data Quality Escalates | AR-002, HITL-002, WF-005 | — |
| TEST-048 | High Risk Good Quality Does Not Escalate at Risk Gate | AR-002, WF-005, HITL-007 | — |
| TEST-051 | All Fields Complete and Consistent | AR-003, FR-006 | — |
| TEST-052 | Age and DOB Inconsistency Detected | AR-003, BR-007 | — |
| TEST-053 | Document Text Contradicts User-Supplied Address | AR-003, BR-007, HITL-003 | — |
| TEST-054 | Data Quality Score at Exact Threshold Boundary (0.5) | AR-003, NFR-004, DEP-002 | — |
| TEST-055 | Non-Critical Fields Missing Do Not Block Review | AR-003, WF-007 | — |
| TEST-056 | Critical Field Missing After Max Follow-Up | AR-003, HITL-003 | — |
| TEST-057 | All Document Extraction Confidence Below 0.4 | AR-003, BR-007 | — |
| TEST-058 | Empty Structured Fields Input | AR-003, NFR-004 | — |
| TEST-059 | Clean Risk Factors Pass Bias Check | AR-004, WF-009 | — |
| TEST-060 | Race or Ethnicity Referenced in Risk Explanation | AR-004, BR-008, HITL-004 | — |
| TEST-061 | Reporter Relationship Used as Negative Amplifier | AR-004, BR-008 | — |
| TEST-062 | Language or Accent Referenced in Risk Explanation | AR-004, BR-008 | — |
| TEST-063 | Bias Confidence at Exact Threshold Boundary (0.7) | AR-004, NFR-004, DEP-002 | — |
| TEST-064 | Multiple Simultaneous Bias Flags | AR-004, DB-004 | — |
| TEST-065 | Empty Risk Factors List | AR-004 | — |
| TEST-066 | Low Risk Clean Case Produces Concise Summary | AR-005, FR-009 | — |
| TEST-067 | Escalated Case Explanation Includes Escalation Reason | AR-005, HITL-005 | — |
| TEST-068 | Explanation When Prior Agent Errored | AR-005, NFR-004 | — |
| TEST-069 | High Risk and Low Data Quality Noted Contradiction | AR-005, BR-010 | — |
| TEST-070 | Critical Case Summary Uses Urgent Language | AR-005, BR-010 | — |
| TEST-071 | Post-Intake Escalation Produces Correct Status | HITL-001, WF-003, FR-010 | — |
| TEST-072 | Post-Risk Escalation for High Risk Poor Quality | HITL-002, WF-005, AR-002 | — |
| TEST-073 | Post-Quality Escalation After Max Follow-Up | HITL-003, WF-007 | — |
| TEST-074 | Post-Bias Escalation Produces Correct Status | HITL-004, WF-009, FR-010 | — |
| TEST-075 | Human Reviewer Approves Escalated Case | HITL-006, FR-012, API-006 | — |
| TEST-076 | Human Reviewer Requests More Information | HITL-006, FR-012, MCP-006 | — |
| TEST-077 | Human Review Action on Non-Escalated Case | API-006, HITL-006 | — |
| TEST-078 | HITL-007 Enforcement: High Risk Cannot Be Auto-Finalized | HITL-007, HITL-002, WF-005 | — |
| TEST-079 | Concurrent Human Review Actions on Same Case | HITL-006, NFR-003 | — |
| TEST-080 | Happy Path Traverses Nodes in Correct Order | WF-001 through WF-013, NFR-006 | — |
| TEST-081 | Follow-Up Loop Re-Enters Intake Node Correctly | WF-002, WF-003, FR-004 | — |
| TEST-082 | No Follow-Up Loop When Fields Are Complete | WF-003, WF-004 | — |
| TEST-083 | Critical Risk Bypasses Quality and Bias Gates | WF-005, HITL-002, HITL-007 | — |
| TEST-084 | Agent Exception Routes to Human Review | WF-005, HITL-002, NFR-004 | — |
| TEST-085 | Quality Gate Loops Back When Not Ready | WF-007, WF-003 | — |
| TEST-086 | Workflow State Isolated Per Case | WF-001, DB-001, NFR-005 | — |
| TEST-092 | AuditEvents Sort Key Uniqueness | DB-005, NFR-003 | — |
| TEST-093 | IntakeCases Update Preserves createdAt | DB-001 | — |
| TEST-094 | AgentOutputs Appends on Multiple Invocations | DB-004, MCP-005 | — |
| TEST-095 | IntakeDocuments Created Even on Extraction Failure | DB-003, BR-009 | — |
| TEST-096 | IntakeMessages Stores Correct Sender and Type | DB-002, FR-004 | — |
| TEST-097 | Empty Case List Returns 200 Not 404 | API-005, FR-013 | — |
| TEST-098 | Case List Pagination Returns Correct Page | API-005, FR-013 | — |
| TEST-099 | Case List Filter by Risk Level | API-005, FR-013 | — |
| TEST-100 | Case List Filter by Status | API-005, FR-013 | — |
| TEST-101 | Human Review Action with Invalid Action Value | API-006 | — |
| TEST-102 | Non-Existent Case ID Returns 404 Not 500 | API-002, API-004, API-006 | — |
| TEST-103 | Malformed JSON on Any POST Endpoint | API-001 | — |
| TEST-104 | Request Body Exceeding 1MB | API-002, NFR-001 | — |
| TEST-105 | NoSQL Injection in Message Text | API-002, DB-002 | — |
| TEST-106 | XSS Payload Stored as Plain Text | API-002, DB-002, FE-006 | — |
| TEST-107 | Path Traversal in Case ID URL Parameter | API-004 | — |
| TEST-108 | Injection Attempt in documentCategory Field | API-003, DB-003 | — |
| TEST-109 | Oversized File Upload | API-003 | — |
| TEST-110 | Intake Confidence Threshold Environment Variable | AR-001, NFR-004, DEP-002 | — |
| TEST-111 | Risk Confidence Threshold Environment Variable | AR-002, NFR-004, DEP-002 | — |
| TEST-112 | Missing ANTHROPIC_API_KEY Produces Clear Error | AR-006, DEP-002 | — |
| TEST-113 | Invalid API Key Handled Gracefully | AR-006, HITL-002, WF-012 | — |
| TEST-114 | Clean Startup from docker-compose up | DEP-001, DEP-002, NFR-005 | — |
| TEST-115 | DynamoDB Tables Auto-Created on Startup | DEP-001, DB-001 through DB-005 | — |
| TEST-116 | S3 Bucket Auto-Created on Startup | DEP-001, FR-002 | — |
| TEST-117 | LocalStack Data Persists Across Restarts | DEP-001, NFR-005 | — |
| TEST-118 | End-to-End Worst-Case Path | HITL-001 through HITL-006, WF-012 | — |
| TEST-119 | End-to-End with Document Upload Contributing Critical Fields | FR-002, FR-003, AR-001, WF-002 | — |
| TEST-120 | End-to-End Low Risk Case No Escalation | AR-001 through AR-005, HITL-001 through HITL-005 | — |
| TEST-121 | End-to-End Critical Case Resolved by Human Reviewer | HITL-002, HITL-006, AR-005, MCP-006 | — |
| TEST-122 | Concurrent Sessions Do Not Cross-Contaminate | WF-001, DB-001, NFR-005 | — |

---

*End of Specification — Version 1.1 — 2026-05-12*
