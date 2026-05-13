High-Level Design: Agentic AI Child Welfare Intake POC
1. Purpose

The goal of this POC is to build a chatbot-based child welfare intake system where users can submit free-text narratives and supporting documents. The system will convert unstructured information into structured intake data, identify missing information, ask human-friendly follow-up questions, assess child vulnerability/risk, monitor data quality and bias, and finally produce a human-readable intake summary for a caseworker dashboard.

The paper already defines the multi-agent structure with agents for intake understanding, risk scoring, data quality, bias monitoring, and explanation. It also emphasizes confidence thresholds, abstention, human escalation, and traceable orchestration.

Part A — Business / Functional Workflow
2. Primary Users
2.1 Reporter / Intake Submitter

This may be a caseworker, mandated reporter, school staff member, healthcare staff member, or any authorized intake user submitting concern details.

They can provide information through a chatbot-style interface.

2.2 Caseworker

The caseworker reviews the structured intake output, risk recommendation, data completeness, AI-generated explanation, missing information, and escalation flags.

2.3 Human Reviewer / Supervisor

This user reviews cases where the AI system is uncertain, detects potential bias, receives incomplete critical data, or identifies high-risk situations needing manual intervention.

3. Intake Submission Workflow

The system begins with a simple React-based chatbot interface.

The user can submit:

Free-text concern narrative
Images
Scanned documents
PDFs
Forms
Identification documents, such as birth certificate or driving license
Videos
Any supporting files related to the intake case

The chatbot does not require the user to enter everything in a rigid form at the beginning. Instead, the system accepts messy, real-world information and gradually converts it into structured data.

This is important because the paper correctly identifies child welfare intake as a messy stage where information often comes in incomplete, inconsistent, or unstructured form.

4. Unstructured-to-Structured Conversion

Once the user submits the information, the Intake Understanding Agent processes the input.

Its responsibility is to extract structured fields such as:

Child name
Child date of birth
Child age
Guardian / parent information
Reporter information
Reporter relationship to child
Contact details
Address / location
Type of concern
Description of incident
Urgency indicators
Prior known concerns
Uploaded document metadata
Extracted document facts
Confidence score for each extracted field

Example:

User writes:

“I am a teacher. One of my students came to school with visible injury and seemed scared to go home.”

The system may extract:

Reporter Type: Teacher
Concern Type: Possible physical harm
Child Status: Student
Urgency Signal: Fear of returning home
Risk Indicator: Visible injury
Missing Data: Child DOB, guardian details, incident date, address
5. Missing Data and Follow-Up Question Workflow

If required information is missing, the system should not silently proceed.

The Intake Understanding Agent should generate human-friendly follow-up questions.

Example:

If date of birth is missing:

“May I know the child’s date of birth, if you don’t mind?”

If address is missing:

“Could you please share the child’s current address or the location where the concern happened?”

If the reporter relationship is missing:

“Can you please tell us how you know the child?”

This is one of the strongest parts of the system because it makes the AI intake flow interactive rather than one-way.

The system should keep asking only necessary questions. It should not overwhelm the user.

6. Risk Assessment Workflow

After enough structured intake data is available, the Risk Assessment Agent evaluates how critical or vulnerable the child may be.

The paper defines this agent as responsible for assigning risk levels such as Low, Medium, High, or Critical, along with confidence scores and contributing factors.

The Risk Assessment Agent should consider:

Type of concern
Age of child
Severity of alleged harm
Urgency indicators
Prior history
Reporter credibility/context
Household instability indicators
Missing critical information
Immediate safety concerns

Output example:

{
  "riskLevel": "High",
  "confidence": 0.87,
  "urgency": "Within 24 hours",
  "contributingFactors": [
    "Physical harm indicator",
    "Child under 5 years old",
    "Prior referral history",
    "Household instability"
  ]
}
7. Data Quality Agent Workflow

The Data Quality Agent checks whether the structured intake data is complete, consistent, and usable.

It should check:

Are required fields present?
Are there conflicting values?
Is the child’s age consistent with date of birth?
Are uploaded documents readable?
Are extracted values reliable?
Are any critical fields still missing?
Is the case ready for risk scoring and caseworker review?

The paper already describes the Data Quality Agent as responsible for missing or ambiguous data detection and follow-up question generation.

In our POC, we may split this slightly:

Intake Understanding Agent asks immediate missing-field questions during intake.
Data Quality Agent performs final completeness and consistency validation before the case is saved.

That separation will make the architecture cleaner.

8. Bias Monitoring Agent Workflow

The Bias Monitoring Agent checks whether the risk output or recommendation may be influenced by sensitive or inappropriate factors.

It should look for:

Demographic over-reliance
Location-based bias
Reporter bias
Language bias
Socioeconomic proxy bias
Unfair risk amplification
Inconsistent treatment for similar cases

The paper positions the Bias Monitoring Agent as a fairness checkpoint before the final caseworker-facing output.

For the POC, this can be rule-based + LLM-reviewed instead of a full SageMaker Clarify implementation.

Example bias flag:

{
  "biasCheckStatus": "Flagged",
  "reason": "Risk explanation appears to rely heavily on neighborhood-level socioeconomic indicators.",
  "action": "Escalate to human reviewer"
}
9. Save Intake Data

Once the intake data passes the required checks, the system saves the structured intake record into DynamoDB.

The system should save:

Raw intake text
Uploaded file references
Extracted structured fields
Missing field history
Follow-up questions and answers
Agent outputs
Risk score
Confidence scores
Bias check result
Data quality score
Final explanation
Human review status
Audit metadata

Important: even if the case is escalated to a human, the system should still save the case state and audit trail.

10. Explanation Agent Workflow

After the intake record is saved, the Explanation Agent converts technical outputs into human-readable information for the caseworker.

The paper already gives a good example of the caseworker-facing output: risk level, confidence, urgency, data quality, reasons for risk, recommendation, and bias check.

The final caseworker dashboard should show:

Case ID: CW-2026-0001
Risk Level: High
Confidence: 87%
Urgency: Within 24 hours
Data Quality: 82% Complete
Bias Check: Passed

Why this case is high risk:
1. Physical harm indicators described by reporter
2. Child is under 5 years old
3. Prior referrals found
4. Household instability indicators present

Recommendation:
Route to investigation unit.

Human Review:
Not required / Required with reason
Part B — Human-in-the-Loop Placement

Human-in-the-loop should be placed at multiple points, not only at the end.

11. Recommended Human Review Points
11.1 After Intake Understanding

Trigger human review if:

The system cannot understand the submitted narrative
Document extraction confidence is low
Uploaded documents are unreadable
The user gives conflicting information
The case contains urgent danger signals but key information is missing

Example:

Escalation Reason:
The intake narrative indicates possible immediate harm, but child identity and location are missing.
11.2 After Risk Assessment

Trigger human review if:

Risk confidence is below threshold
Risk level is High or Critical
The model detects immediate safety concern
Risk factors are severe but data completeness is poor
Risk recommendation conflicts with data quality score

My suggestion: Critical cases should always be human-reviewed, even if confidence is high.

The AI should help prioritize, not independently finalize.

11.3 After Data Quality Check

Trigger human review if:

Critical fields are missing
Data completeness is below required threshold
User cannot provide missing information
Documents are inconsistent with user-provided information
Identity or relationship cannot be verified
11.4 After Bias Monitoring

Trigger human review if:

Bias Monitoring Agent flags the case
Sensitive demographic factors appear in the risk explanation
Similar cases receive inconsistent risk treatment
The system cannot confidently confirm fairness

The paper already emphasizes that bias monitoring should have a strict confidence threshold and should route to escalation if fairness concerns appear.

11.5 Before Final Caseworker Routing

A final review checkpoint should exist before the intake is marked as ready for caseworker action.

Possible final statuses:

READY_FOR_CASEWORKER_REVIEW
NEEDS_MORE_INFORMATION
ESCALATED_TO_SUPERVISOR
CRITICAL_IMMEDIATE_REVIEW
BIAS_REVIEW_REQUIRED
LOW_CONFIDENCE_REVIEW_REQUIRED

