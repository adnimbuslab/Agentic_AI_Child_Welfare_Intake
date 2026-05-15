# Business Workflow: Agentic AI Child Welfare Intake System

## 1. System Overview

The Agentic AI Child Welfare Intake System is a chatbot-based platform that transforms the traditionally manual, form-driven child welfare intake process into an intelligent, conversational workflow. The system accepts unstructured narratives and supporting documents from reporters, converts them into structured intake records through multi-agent orchestration, assesses child risk, monitors for data quality and bias, and produces actionable summaries for caseworkers — all while maintaining human oversight at critical decision points.

The system is built on three foundational design principles:

1. **Conversational intake over rigid forms** — reporters provide information naturally; the system extracts structure from narrative.
2. **Multi-agent orchestration** — five specialized AI agents handle distinct analytical responsibilities, connected through a directed acyclic workflow graph.
3. **Human-in-the-loop at every critical gate** — the AI assists and recommends, but never autonomously finalizes high-risk decisions.

---

## 2. Primary Users and Roles

| Role | Description | System Interaction |
|------|-------------|-------------------|
| **Reporter / Intake Submitter** | Caseworker, mandated reporter (teacher, healthcare worker), law enforcement, or community member submitting a concern | Interacts via chatbot: submits free-text narrative, uploads documents, answers follow-up questions |
| **Caseworker** | Reviews structured intake output and decides on next action | Views case dashboard: risk level, confidence scores, data quality, AI-generated explanation, recommendations |
| **Supervisor / Human Reviewer** | Reviews escalated cases where AI confidence is low, bias is flagged, or risk is critical | Accesses human review queue: can accept, override risk level, add notes, reclassify status |

---

## 3. End-to-End Business Workflow

The workflow progresses through 13 distinct stages, organized into four phases: **Intake Collection**, **Intelligent Analysis**, **Quality and Fairness Assurance**, and **Decision and Routing**.

### Phase 1: Intake Collection

#### Stage 1 — Session Initiation (WF-001)

The reporter opens the chatbot interface and initiates a new intake session. The system generates a unique case identifier (format: `CW-YYYY-NNNN`) and creates an empty intake record. No structured data exists at this point — the system simply opens a channel for the reporter to communicate.

```
Reporter → [Start Intake Session] → System generates CW-2026-0042
```

#### Stage 2 — Narrative Submission and Field Extraction (WF-002)

The reporter submits their concern as free-text narrative. Unlike traditional systems that require filling out predefined forms, the reporter can describe the situation in their own words:

> *"I'm a teacher at Lincoln Elementary. One of my students, Emma, age 7, came to school yesterday with bruises on her arms and seemed afraid to go home. Her father picks her up most days and I've noticed she flinches when he approaches."*

The **Intake Understanding Agent (AR-001)** processes this narrative and extracts structured fields with per-field confidence scores:

| Extracted Field | Value | Confidence |
|----------------|-------|------------|
| Child Name | Emma | 0.95 |
| Child Age | 7 | 0.90 |
| Reporter Type | Teacher | 0.98 |
| Reporter Relationship | Teacher at child's school | 0.95 |
| Concern Type | Suspected physical abuse | 0.88 |
| Urgency Indicators | Visible injuries, fear of caregiver | 0.85 |
| Guardian Info | Father (primary pickup) | 0.70 |
| Child DOB | *Missing* | — |
| Address | *Missing* | — |
| Contact Details | *Missing* | — |

The system also accepts multi-modal inputs: images, scanned documents, PDFs, identification documents, and videos. Uploaded documents are stored and their content is extracted to supplement the narrative.

#### Stage 3 — Duplicate Detection (WF-002b)

Before proceeding with follow-up questions, the system checks whether this report may relate to an existing case. The **Duplicate Detection Engine** compares extracted fields against all existing cases using weighted fuzzy matching:

| Match Factor | Weight (with SSN) | Weight (without SSN) |
|-------------|-------------------|---------------------|
| SSN | 30% | Redistributed |
| Child Name | 20% | 30% |
| Child DOB | 20% | 30% |
| Guardian Name | 10% | 15% |
| Address | 10% | 15% |
| Child Age | 5% | 5% |
| Contact Info | 5% | 5% |

Three outcomes are possible:

- **No match** (confidence < 75%): Proceed as a new case.
- **Probable match** (75%–90%): Pause workflow, ask the reporter or caseworker to confirm or deny the match.
- **Auto-match** (> 90%): Automatically link to the existing case and merge new information.

When a match is confirmed, the system merges structured fields — retaining the value with the higher confidence score for each field — and continues processing the combined record.

#### Stage 4 — Interactive Follow-Up Questions (WF-003)

If required fields are missing, the system generates human-friendly follow-up questions rather than silently proceeding with incomplete data:

> *"Thank you for sharing this information. To help us respond appropriately, could you please provide:"*
> - *"Do you know Emma's date of birth or approximate birthday?"*
> - *"What is the address where Emma lives, or the school's address?"*
> - *"Is there a phone number where we could reach you if we have additional questions?"*

The follow-up loop has the following rules:
- Questions are limited to the most critical missing fields per round (avoids overwhelming the reporter).
- A maximum number of follow-up rounds is enforced (configurable; default: 3 rounds).
- If critical fields remain missing after maximum rounds, the case is escalated to human review.
- The reporter can decline to answer ("I don't want to share that") and the system proceeds with available data.

Each round of follow-up feeds back into the Intake Understanding Agent, which re-extracts and updates structured fields with cumulative context.

---

### Phase 2: Intelligent Analysis

#### Stage 5 — Risk Assessment (WF-004)

Once sufficient structured data is available, the **Risk Assessment Agent (AR-002)** evaluates child vulnerability. The agent considers nine factor categories:

1. **Type of concern** — physical abuse, neglect, sexual abuse, emotional abuse, exploitation
2. **Age of child** — younger children receive higher risk weighting
3. **Severity of alleged harm** — visible injuries, medical indicators, chronic patterns
4. **Urgency indicators** — immediate danger signals, fear behaviors, active threats
5. **Prior history** — previous referrals, open cases, known family involvement
6. **Reporter credibility/context** — mandated reporters, direct witnesses, anonymous tips
7. **Household instability indicators** — substance abuse mentions, domestic violence, housing instability
8. **Missing critical information** — gaps that prevent adequate assessment
9. **Immediate safety concerns** — child currently in danger, no safe caregiver available

The agent produces a structured risk output:

| Output Field | Example Value |
|-------------|---------------|
| Risk Level | High |
| Confidence Score | 0.87 |
| Urgency | Within 24 hours |
| Contributing Factors | Physical harm indicators, child under 10, visible injuries, fear of caregiver |

**Risk levels and their meaning:**

| Level | Definition | Typical Response |
|-------|-----------|-----------------|
| **Low** | Concern noted but no immediate safety threat | Routine follow-up within 5 business days |
| **Medium** | Potential risk that warrants investigation | Follow-up within 72 hours |
| **High** | Significant risk indicators present | Investigation within 24 hours |
| **Critical** | Immediate danger to child safety | Emergency response, always escalated to supervisor |

#### Stage 6 — Risk Confidence Gate (WF-005)

An automated gate evaluates whether the risk assessment is reliable enough to proceed:

- **Confidence < 0.6**: Escalate to human review (model is uncertain).
- **Risk Level = Critical**: Always escalate to human review regardless of confidence.
- **Risk Level = High AND Data Quality < 0.5**: Escalate (high risk on poor data).
- **Otherwise**: Proceed to data quality validation.

---

### Phase 3: Quality and Fairness Assurance

#### Stage 7 — Data Quality Validation (WF-006)

The **Data Quality Agent (AR-003)** performs a comprehensive validation of the structured intake record:

- **Completeness check**: Are all required fields populated?
- **Consistency check**: Does the reported age match the date of birth? Do geographic details align?
- **Document verification**: Are uploaded documents readable and their extracted content reliable?
- **Cross-reference check**: Do extracted fields from multiple sources (narrative, documents, follow-ups) agree?

Output:

| Output Field | Example Value |
|-------------|---------------|
| Data Quality Score | 0.82 (82% complete) |
| Missing Critical Fields | [childDob, address] |
| Inconsistencies | None detected |
| Ready for Review | Yes |

#### Stage 8 — Data Quality Gate (WF-007)

- **Data Quality Score < 0.5** after follow-up rounds: Escalate to human review.
- **Critical fields still missing AND reporter already asked**: Escalate.
- **Document contradictions in critical fields**: Escalate.
- **Case not ready for review**: Route back for additional follow-up.
- **Otherwise**: Proceed to bias monitoring.

#### Stage 9 — Bias Monitoring (WF-008)

The **Bias Monitoring Agent (AR-004)** acts as a fairness checkpoint, reviewing whether the risk assessment may have been influenced by inappropriate factors:

| Bias Category | What It Checks |
|--------------|----------------|
| Demographic over-reliance | Risk driven by race, ethnicity, or gender rather than factual indicators |
| Location-based bias | Neighborhood or zip code used as a risk proxy |
| Reporter bias | Credibility weighted unfairly based on reporter demographics |
| Language bias | Non-English speakers or non-standard language penalized |
| Socioeconomic proxy bias | Poverty-correlated factors treated as abuse indicators |
| Inconsistent treatment | Similar cases receiving different risk levels |

Output:

| Output Field | Example Value |
|-------------|---------------|
| Bias Status | Passed / Flagged |
| Bias Confidence | 0.92 |
| Flags | [] or ["Risk explanation relies on neighborhood socioeconomic indicators"] |
| Human Review Required | false / true |

#### Stage 10 — Bias Gate (WF-009)

- **Bias Status = Flagged**: Escalate to human review with specific bias concerns.
- **Bias Confidence < threshold**: Escalate for fairness verification.
- **Otherwise**: Proceed to save the intake record.

---

### Phase 4: Decision and Routing

#### Stage 11 — Save Final Intake Record (WF-010)

The system persists the complete intake record to the database, including:

- Raw narrative text and conversation history
- Uploaded file references and extraction results
- All structured fields with confidence scores
- Full follow-up question and answer history
- All agent outputs (intake, risk, quality, bias)
- Risk scores and contributing factors
- Bias check results
- Data quality scores
- Human review status and audit metadata

Every field, decision, and state transition throughout the workflow has been logged as an immutable audit event, creating a complete decision trail.

#### Stage 12 — Explanation Generation (WF-011)

The **Explanation Agent (AR-005)** transforms technical agent outputs into a human-readable caseworker summary:

```
Case ID: CW-2026-0042
Risk Level: High
Confidence: 87%
Urgency: Within 24 hours
Data Quality: 82% Complete
Bias Check: Passed

Why this case is rated High risk:
1. Reporter (mandated — teacher) describes visible physical injuries
2. Child exhibits fear-based behavior toward primary caregiver
3. Pattern suggests ongoing harm, not isolated incident
4. Child is under 10 years old (elevated vulnerability)

Recommendation:
Route to investigation unit for in-person assessment within 24 hours.

Limitations:
- Child's exact address not confirmed; school address available
- No prior referral history found (may indicate first report or data gap)

Human Review: Not required
```

#### Stage 13 — Final Status Assignment and Routing (WF-012/WF-013)

Every case receives one of six final statuses:

| Status | Meaning | Routing |
|--------|---------|---------|
| `READY_FOR_CASEWORKER_REVIEW` | All checks passed, case is complete | Caseworker dashboard |
| `NEEDS_MORE_INFORMATION` | Missing data that follow-up couldn't resolve | Reporter re-engagement queue |
| `ESCALATED_TO_SUPERVISOR` | Agent confidence too low or high-risk flags | Supervisor review queue |
| `CRITICAL_IMMEDIATE_REVIEW` | Immediate child safety threat detected | Emergency supervisor queue + notification |
| `BIAS_REVIEW_REQUIRED` | Potential fairness concerns in risk assessment | Bias review specialist queue |
| `LOW_CONFIDENCE_REVIEW_REQUIRED` | Model uncertainty across multiple agents | Senior reviewer queue |

---

## 4. Human-in-the-Loop Decision Points

Human oversight is embedded at five distinct points in the workflow, not only at the end. This ensures that AI assists but never independently finalizes critical decisions.

```
                    HITL-1                HITL-2           HITL-3          HITL-4        HITL-5
                      |                    |                 |               |             |
  Intake → Extraction → Duplicate → Risk → Risk Gate → Quality → Quality Gate → Bias → Bias Gate → Save → Explain → Final Gate
                      |                    |                 |               |             |
                      v                    v                 v               v             v
                 [Can't parse       [Low confidence    [Critical fields  [Bias flagged  [Final human
                  narrative;         or Critical risk;   still missing;    or fairness    review before
                  conflicting        High risk + poor    documents         uncertain]     routing]
                  info; urgent       data quality]       contradict
                  + identity                             user data]
                  unknown]
```

### HITL-1: After Intake Understanding
**Triggers:** Narrative unparseable (confidence < 0.3), documents unreadable, conflicting critical information, urgent danger signals but child identity/location missing.

### HITL-2: After Risk Assessment
**Triggers:** Risk confidence < 0.6, risk level is Critical (always), High risk with data quality < 0.5, immediate safety concern with poor data.

### HITL-3: After Data Quality Check
**Triggers:** Critical fields missing after reporter exhausted, data quality < 0.5 after all follow-up rounds, documents contradict user information, identity unverifiable.

### HITL-4: After Bias Monitoring
**Triggers:** Bias flagged in risk reasoning, sensitive demographic factors in risk explanation, inconsistent treatment detected, fairness cannot be confirmed.

### HITL-5: After Explanation / Before Final Routing
**Triggers:** Explanation agent determines case needs human sign-off, final status requires supervisor approval.

---

## 5. Workflow State Diagram

```
                              +-----------------------+
                              |   Session Initiation  |
                              |       (WF-001)        |
                              +-----------+-----------+
                                          |
                                          v
                              +-----------+-----------+
                              |  Intake Understanding |
                              |   Agent (WF-002)      |
                              |   [Field Extraction]  |
                              +-----------+-----------+
                                          |
                                          v
                              +-----------+-----------+
                              | Duplicate Detection   |
                              |      (WF-002b)        |
                              +-----------+-----------+
                                     /    |    \
                           No Match /     |     \ Auto-Match
                                  /      |      \
                                 v       v       v
                          [Continue] [Confirm?] [Merge & Continue]
                                 \       |       /
                                  \      |      /
                                   v     v     v
                              +-----------+-----------+
                              |  Follow-Up Question   |
                 +----------->|   Loop (WF-003)       |<-----------+
                 |            +-----------+-----------+            |
                 |                   /    |    \                   |
                 |       Missing   /     |     \  All fields      |
                 |       fields   /      |      \ present         |
                 |               v       v       v                |
                 |        [Ask Follow-up] | [Max rounds]          |
                 |              |         |      |                |
                 |              |         v      |                |
                 |              |   [HITL: Human |                |
                 |              |    Review]     |                |
                 |              v                v                |
                 |     [Reporter Answers] ------+                 |
                 |              |                                  |
                 +----<---------+                                  |
                                                                   |
                              +-----------+-----------+            |
                              |  Risk Assessment      |            |
                              |   Agent (WF-004)      |            |
                              +-----------+-----------+            |
                                          |                        |
                                          v                        |
                              +-----------+-----------+            |
                              |   Risk Confidence     |            |
                              |    Gate (WF-005)      |            |
                              +----+-------------+----+            |
                                   |             |                 |
                              Pass |             | Fail            |
                                   v             v                 |
                              +----+----+  +-----+------+          |
                              |  Data   |  | HITL:      |          |
                              | Quality |  | Human      |          |
                              | (WF-006)|  | Review     |          |
                              +----+----+  +------------+          |
                                   |                               |
                                   v                               |
                              +----+-------------+                 |
                              | Quality Gate     |                 |
                              |   (WF-007)       |                 |
                              +--+---------+--+--+                 |
                                 |         |  |                    |
                            Pass |    Fail |  | Not Ready          |
                                 v         v  +------>-------------+
                              +--+---+  +--+--------+
                              | Bias |  | HITL:     |
                              | Mon. |  | Human     |
                              |(WF-08)| | Review    |
                              +--+---+  +-----------+
                                 |
                                 v
                              +--+-------------+
                              | Bias Gate      |
                              |   (WF-009)     |
                              +--+----------+--+
                                 |          |
                            Pass |     Flag |
                                 v          v
                              +--+---+  +---+-------+
                              | Save |  | HITL:     |
                              | Case |  | Human     |
                              |(WF-10)| | Review    |
                              +--+---+  +-----------+
                                 |
                                 v
                              +--+-----------+
                              | Explanation  |
                              | Agent(WF-011)|
                              +--+-----------+
                                 |
                                 v
                              +--+-------------+
                              | Final Status   |
                              | Assignment     |
                              |  (WF-012/013)  |
                              +--+----------+--+
                                 |          |
                                 v          v
                          +------+---+ +----+----------+
                          |Caseworker| |Supervisor/     |
                          |Dashboard | |Human Review    |
                          +----------+ |Queue           |
                                       +---------------+
```

---

## 6. Agent Orchestration Architecture

The five AI agents are orchestrated through a **LangGraph StateGraph** — a directed acyclic graph where each node represents an agent or decision gate, and edges represent conditional transitions.

```
+------------------------------------------------------------------+
|                     LangGraph StateGraph                         |
|                                                                  |
|  +-------------+    +----------+    +----------+    +----------+ |
|  |   Intake    |--->| Duplicate|--->|   Risk   |--->|   Data   | |
|  |Understanding|    | Detection|    |Assessment|    |  Quality | |
|  |  (AR-001)   |    |          |    |  (AR-002)|    |  (AR-003)| |
|  +-------------+    +----------+    +----------+    +----------+ |
|         |                                                  |     |
|         |           +----------+    +----------+           |     |
|         +---------->|   Bias   |--->|Explanation|<----------+     |
|                     |Monitoring|    |  (AR-005) |                |
|                     | (AR-004) |    +----------+                 |
|                     +----------+                                 |
+------------------------------------------------------------------+
         |                                       |
         v                                       v
+------------------+                   +------------------+
|   MCP Servers    |                   |   DynamoDB       |
| (Tool Interface) |                   |   (via MCP)      |
+------------------+                   +------------------+
```

**Critical architectural constraint:** All agents access backend services exclusively through MCP (Model Context Protocol) servers — never directly. This creates a clean separation between agent logic and data access, enabling auditability and tool-level access control.

### MCP Server Tool Interface

| MCP Server | ID | Tools Provided |
|-----------|-----|---------------|
| Intake Server | MCP-001 | Create/read/update intake cases, save messages |
| Risk Server | MCP-002 | Calculate risk scores, save risk assessments |
| Case History Server | MCP-003 | Search existing cases, find prior referrals, duplicate lookup |
| Audit Server | MCP-004 | Log agent decisions, escalation events, state transitions |
| Knowledge Server | MCP-005 | Retrieve policy guidelines, required field lists, risk policies |
| Notification Server | MCP-006 | Notify caseworkers, route to human review, alert supervisors |

---

## 7. Audit Trail and Transparency

Every action in the system is recorded as an immutable audit event:

| Event Type | What Is Logged |
|-----------|---------------|
| Agent Decision | Agent name, input summary, output JSON, confidence score, escalation flag, timestamp |
| State Transition | Previous state, next state, transition condition, triggering agent |
| Human Action | Reviewer ID, action taken (accept/override/note), before/after values, timestamp |
| Escalation | Escalating agent, reason, severity, target queue |
| Data Modification | Field changed, old value, new value, source (agent/human/merge) |

This ensures:
- **Explainability**: Every risk score can be traced back to the factors and agent logic that produced it.
- **Accountability**: Human overrides and AI recommendations are both permanently recorded.
- **Compliance**: The full decision chain is available for regulatory review.
- **Continuous improvement**: Patterns in escalations, overrides, and bias flags can be analyzed to improve the system.

---

## 8. Data Persistence Model

| Table | Purpose | Key Fields |
|-------|---------|-----------|
| **IntakeCases** | Primary case record | caseId, status, riskLevel, structuredFields, dataQualityScore, biasStatus, humanReviewRequired |
| **IntakeMessages** | Conversation history | messageId, caseId, senderType (user/agent), messageType, content, timestamp |
| **IntakeDocuments** | Uploaded file metadata | documentId, caseId, fileType, s3Key, extractionStatus, extractedText |
| **AgentOutputs** | Individual agent results | outputId, caseId, agentName, outputJson, confidenceScore, escalated |
| **AuditEvents** | Immutable event log | eventId, caseId, actor, eventType, beforeState, afterState, reason, timestamp |

---

## 9. Key Business Rules Summary

1. **No silent failures**: If information is missing, the system must ask — never proceed silently with gaps.
2. **Critical = always human**: Critical risk cases always route to supervisor review, regardless of AI confidence.
3. **High risk + poor data = human**: High risk assessments on low-quality data require human verification.
4. **Bias flags = mandatory review**: Any flagged bias concern triggers human review before the case can proceed.
5. **Audit everything**: Every agent decision, state change, and human action is immutably logged.
6. **Agents use tools, not backends**: All data access goes through MCP servers — agents never touch databases directly.
7. **Model swappable**: The LLM provider and model are configurable via environment variables — zero code changes required.
8. **Follow-up limits**: Maximum follow-up rounds prevent infinite loops; unresolvable gaps escalate to humans.
9. **Duplicate detection before analysis**: Duplicate checking occurs early to prevent redundant processing and merge related reports.
10. **Confidence-gated progression**: Each pipeline stage has a confidence threshold gate — low confidence routes to human review rather than producing unreliable outputs.

---

## 10. Sample Workflow Trace

**Scenario:** A teacher reports suspected neglect of a 7-year-old student.

| Step | Stage | Action | Outcome |
|------|-------|--------|---------|
| 1 | Session Init | Teacher opens chatbot, starts intake | Case CW-2026-0042 created |
| 2 | Narrative | Teacher describes: visible bruises, child afraid of father | 8 fields extracted, 3 missing |
| 3 | Duplicate Check | System compares against existing cases | No match found (0% confidence) |
| 4 | Follow-Up Round 1 | System asks for DOB, address, contact info | Teacher provides school address, declines contact |
| 5 | Follow-Up Round 2 | System asks for DOB, reporter contact | Teacher provides approximate DOB |
| 6 | Risk Assessment | Agent evaluates all structured data | High risk (0.87 confidence), Within 24 hours |
| 7 | Risk Gate | Confidence 0.87 > 0.6, not Critical | Pass — proceed to data quality |
| 8 | Data Quality | Agent checks completeness and consistency | 82% complete, no inconsistencies, ready for review |
| 9 | Quality Gate | Score 0.82 > 0.5, ready for review | Pass — proceed to bias monitoring |
| 10 | Bias Monitoring | Agent reviews risk factors for fairness | Passed — no inappropriate factor reliance |
| 11 | Bias Gate | No flags detected | Pass — proceed to save |
| 12 | Save Record | Complete intake record persisted to database | All fields, scores, and audit trail saved |
| 13 | Explanation | Agent generates caseworker summary | Plain-language summary with recommendation |
| 14 | Final Routing | Status: READY_FOR_CASEWORKER_REVIEW | Case appears on caseworker dashboard |
