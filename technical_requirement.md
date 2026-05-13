Part C — Technical HLD
12. Technical Architecture Overview

The POC architecture should follow this flow:

React Chat UI
   ↓
API Gateway on LocalStack
   ↓
Lambda Intake API
   ↓
DynamoDB
   ↓
LangGraph Agent Workflow
   ↓
MCP Servers
   ↓
Backend Tools / Agent Tools
   ↓
Agent Outputs
   ↓
DynamoDB + Audit Logs
   ↓
React Caseworker Dashboard
13. Frontend
Technology

Use React.

Main UI Modules
Chatbot Intake Interface
Text input
File upload
Conversation history
Follow-up questions
Intake progress indicator
Caseworker Dashboard
Case list
Risk level
Status
Urgency
Data completeness
Bias flag
Human review flag
Case Detail View
Structured intake summary
Uploaded documents
Extracted fields
Follow-up Q&A
Risk explanation
Agent confidence scores
Audit timeline
Human Review Queue
Escalated cases
Escalation reason
Reviewer action
Override notes
14. Backend / API Layer
LocalStack

LocalStack will simulate AWS services locally.

API Gateway

API Gateway exposes backend endpoints such as:

POST /intake/session
POST /intake/message
POST /intake/upload
GET  /intake/{caseId}
GET  /cases
GET  /cases/{caseId}/summary
POST /cases/{caseId}/human-review
Lambda

Lambda functions handle API requests.

Suggested Lambda functions:

CreateIntakeSessionLambda
SubmitIntakeMessageLambda
UploadIntakeDocumentLambda
GetCaseSummaryLambda
ListCasesLambda
HumanReviewActionLambda
15. Database: DynamoDB

Suggested tables:

15.1 IntakeCases

Stores main case record.

Key:

PK: caseId

Attributes:

caseId
status
riskLevel
riskConfidence
urgency
dataQualityScore
biasStatus
humanReviewRequired
createdAt
updatedAt
15.2 IntakeMessages

Stores chat conversation.

Key:

PK: caseId
SK: messageTimestamp

Attributes:

senderType
messageText
messageType
attachments
agentGenerated
createdAt
15.3 IntakeDocuments

Stores uploaded document metadata.

Key:

PK: caseId
SK: documentId

Attributes:

fileName
fileType
storagePath
extractedText
extractionConfidence
documentCategory
createdAt
15.4 AgentOutputs

Stores each agent output.

Key:

PK: caseId
SK: agentName#timestamp

Attributes:

agentName
inputSummary
outputJson
confidenceScore
status
escalationReason
createdAt
15.5 AuditEvents

Stores complete audit trail.

Key:

PK: caseId
SK: eventTimestamp

Attributes:

eventType
actor
agentName
action
reason
beforeState
afterState
createdAt
16. LangGraph Agent Layer

The agent workflow should be implemented using LangGraph.

Suggested graph flow:

Start
 ↓
Intake Understanding Agent
 ↓
Missing Data Check
 ├── Missing Critical Data → Generate Follow-Up Question → Wait for User Response
 └── Sufficient Data → Continue
 ↓
Risk Assessment Agent
 ↓
Risk Confidence Gate
 ├── Low Confidence / Critical Risk → Human Review Queue
 └── Continue
 ↓
Data Quality Agent
 ↓
Quality Gate
 ├── Poor Quality → Follow-Up / Human Review
 └── Continue
 ↓
Bias Monitoring Agent
 ↓
Bias Gate
 ├── Bias Flagged → Human Review Queue
 └── Continue
 ↓
Save Final Intake Record
 ↓
Explanation Agent
 ↓
Caseworker Dashboard
 ↓
End
17. MCP Server Design

The LLM/agent layer should not directly manipulate backend resources. It should use MCP servers as controlled tool boundaries.

Recommended MCP servers:

17.1 Intake MCP Server

Tools:

create_intake_case
get_intake_case
update_intake_case
save_structured_intake
save_intake_message
17.2 Contacts MCP Server

Tools:

lookup_child_contact
lookup_guardian_contact
lookup_reporter_contact
validate_contact_information
17.3 Case History MCP Server

Tools:

get_prior_referrals
get_case_history
get_household_history
17.4 Risk Assessment MCP Server

Tools:

calculate_risk_score
get_risk_thresholds
save_risk_assessment
17.5 Audit & Governance MCP Server

Tools:

save_agent_decision
save_confidence_score
save_escalation_reason
save_human_override
get_audit_timeline
17.6 Notification / Escalation MCP Server

Tools:

route_to_human_review
notify_caseworker
notify_supervisor
create_review_task
17.7 Knowledge / Policy MCP Server

Tools:

get_intake_required_fields
get_mandatory_reporting_rules
get_risk_policy_guidelines
get_bias_monitoring_policy
get_human_review_policy

This server is especially important because it keeps the LLM grounded in approved policy/checklist content.

18. Agent Responsibilities
18.1 Intake Understanding Agent

Responsibilities:

Read chat text
Read extracted document text
Interpret uploaded materials
Convert unstructured input into structured intake fields
Detect missing required fields
Generate human-friendly follow-up questions
Assign field-level confidence scores

Output:

{
  "structuredFields": {},
  "missingFields": [],
  "followUpQuestions": [],
  "confidenceScore": 0.82
}
18.2 Risk Assessment Agent

Responsibilities:

Evaluate child vulnerability
Determine risk level
Assign confidence score
Identify contributing risk factors
Recommend urgency level

Output:

{
  "riskLevel": "High",
  "confidenceScore": 0.87,
  "urgency": "Within 24 hours",
  "riskFactors": []
}
18.3 Data Quality Agent

Responsibilities:

Validate completeness
Detect contradictions
Check document quality
Check consistency across fields
Decide whether case is ready for review

Output:

{
  "dataQualityScore": 0.82,
  "missingCriticalFields": [],
  "inconsistencies": [],
  "readyForReview": true
}
18.4 Bias Monitoring Agent

Responsibilities:

Review risk reasoning
Identify possible sensitive attribute influence
Check fairness concerns
Flag unsafe or biased reasoning

Output:

{
  "biasStatus": "Passed",
  "biasConfidence": 0.96,
  "flags": [],
  "humanReviewRequired": false
}
18.5 Explanation Agent

Responsibilities:

Convert technical agent outputs into simple caseworker-facing explanation
Show confidence and limitations
Explain why a risk level was selected
Explain whether human review is needed
Avoid diagnostic or overly certain language

Output:

{
  "caseworkerSummary": "",
  "riskExplanation": [],
  "recommendation": "",
  "limitations": [],
  "nextAction": ""
}
Part D — Recommendation for Claude LLD
19. What We Should Give Claude Next

We should give Claude one combined prompt with:

Architecture baseline
Business workflow
Agent responsibilities
DynamoDB tables
MCP server list
API endpoints
LangGraph flow
Human-in-the-loop rules
React frontend screens
Request to generate LLD module by module

But before that, I suggest we finalize these two HLD documents:

Document 1: Business Workflow HLD

Sections:

1. Objective
2. User Personas
3. Intake Submission Journey
4. Missing Data Follow-Up Flow
5. Risk Assessment Flow
6. Data Quality Flow
7. Bias Monitoring Flow
8. Human-in-the-Loop Flow
9. Caseworker Dashboard Flow
10. Final Case Statuses
Document 2: Technical Architecture HLD

Sections:

1. Architecture Overview
2. Technology Stack
3. React Frontend
4. LocalStack AWS Simulation
5. API Gateway and Lambda
6. DynamoDB Data Model
7. LangGraph Agent Workflow
8. MCP Server Design
9. Agent Input/Output Contracts
10. Human Review Queue
11. Audit and Governance
12. Deployment Path: Local POC to AWS AgentCore

Important - Let's use Opus 4.7 for all agents. Write the code in such a way that all the LLMs can be replacable later on.

Prepare all test cases, save those test cases in readme file of the code, and deploy and test iteratively in local stack. I have already installed local stack in my machine. I'll also personally test once you're done.