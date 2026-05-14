"""End-to-end test of the intake workflow with Ollama."""
import json
import traceback

# Reset DB singletons to ensure fresh connections
import backend.db as db_mod
db_mod._dynamodb_resource = None
db_mod._dynamodb_client = None

print("=" * 60)
print("E2E TEST: Child Welfare Intake with Ollama (llama3.1:8b)")
print("=" * 60)

# Step 1: Create a session
print("\n--- Step 1: Creating intake session ---")
from backend.mcp_servers import intake_server, audit_server
case = intake_server.create_intake_case("mandated-reporter")
case_id = case["caseId"]
print(f"Case created: {case_id}")

audit_server.save_agent_decision(
    case_id=case_id,
    agent_name="system",
    output_json={"action": "session_created", "reporterType": "mandated-reporter"},
)

# Step 2: Save the reporter message
print("\n--- Step 2: Saving reporter narrative ---")
narrative = (
    "I am a teacher at Lincoln Elementary School. I need to report a concern about "
    "one of my students, Emma Johnson, age 7, date of birth March 15 2019. "
    "She is in my 2nd grade class. Over the past two weeks I have noticed Emma "
    "coming to school with bruises on her arms and she seems very withdrawn and scared. "
    "She flinches when adults raise their voice. Yesterday she told me she is afraid "
    "to go home because daddy gets angry. Her mother is Sarah Johnson and her father "
    "is David Johnson. They live at 142 Oak Street, Springfield, IL 62701. "
    "My name is Patricia Williams and I can be reached at 555-0147. "
    "I have been her teacher since September and this behavior is new."
)

intake_server.save_intake_message(
    case_id=case_id,
    message_text=narrative,
    sender_type="user",
    message_type="narrative",
)
print("Message saved.")

# Step 3: Run the workflow
print("\n--- Step 3: Running LangGraph workflow (5 agents via Ollama) ---")
print("This may take several minutes on CPU...")
from backend.workflow.intake_workflow import compile_workflow

session_messages = [{"role": "user", "content": narrative}]

workflow = compile_workflow()
try:
    result = workflow.invoke({
        "case_id": case_id,
        "session_messages": session_messages,
        "extracted_document_texts": None,
        "follow_up_round": 0,
    })
    print("\nWorkflow completed!")
    print(f"Final status: {result.get('final_status', 'N/A')}")
    print(f"Needs follow-up: {result.get('needs_followup', False)}")
    print(f"Escalated: {result.get('escalated', False)}")

    if result.get("intake_output"):
        io = result["intake_output"]
        print(f"\n{'='*60}")
        print("AGENT 1: Intake Understanding")
        print(f"{'='*60}")
        print(f"Overall confidence: {io.get('overallConfidenceScore', 'N/A')}")
        print(f"Escalate: {io.get('escalate', False)}")
        if io.get('escalationReason'):
            print(f"Escalation reason: {io['escalationReason']}")
        print(f"Missing fields: {io.get('missingRequiredFields', [])}")
        print(f"Follow-up questions: {io.get('followUpQuestions', [])}")
        sf = io.get("structuredFields", {})
        print("Extracted fields:")
        for field_name, field_data in sf.items():
            if isinstance(field_data, dict):
                val = field_data.get("value", "N/A")
                conf = field_data.get("confidence", "N/A")
            else:
                val = field_data
                conf = "N/A"
            print(f"  {field_name}: {val} (confidence: {conf})")

    if result.get("risk_output"):
        ro = result["risk_output"]
        print(f"\n{'='*60}")
        print("AGENT 2: Risk Assessment")
        print(f"{'='*60}")
        print(f"Risk level: {ro.get('riskLevel', 'N/A')}")
        print(f"Confidence: {ro.get('confidenceScore', 'N/A')}")
        print(f"Urgency: {ro.get('urgency', 'N/A')}")
        print(f"Risk factors: {ro.get('riskFactors', [])}")
        print(f"Escalate: {ro.get('escalate', False)}")
        if ro.get('escalationReason'):
            print(f"Escalation reason: {ro['escalationReason']}")

    if result.get("quality_output"):
        qo = result["quality_output"]
        print(f"\n{'='*60}")
        print("AGENT 3: Data Quality")
        print(f"{'='*60}")
        print(f"Quality score: {qo.get('dataQualityScore', 'N/A')}")
        print(f"Ready for review: {qo.get('readyForReview', 'N/A')}")
        print(f"Missing critical fields: {qo.get('missingCriticalFields', [])}")
        print(f"Inconsistencies: {qo.get('inconsistencies', [])}")
        print(f"Escalate: {qo.get('escalate', False)}")

    if result.get("bias_output"):
        bo = result["bias_output"]
        print(f"\n{'='*60}")
        print("AGENT 4: Bias Monitoring")
        print(f"{'='*60}")
        print(f"Bias status: {bo.get('biasStatus', 'N/A')}")
        print(f"Bias confidence: {bo.get('biasConfidence', 'N/A')}")
        print(f"Flags: {bo.get('flags', [])}")
        print(f"Human review required: {bo.get('humanReviewRequired', False)}")

    if result.get("explanation_output"):
        eo = result["explanation_output"]
        print(f"\n{'='*60}")
        print("AGENT 5: Explanation")
        print(f"{'='*60}")
        print(f"Final case status: {eo.get('finalCaseStatus', 'N/A')}")
        print(f"Caseworker summary: {eo.get('caseworkerSummary', 'N/A')}")
        print(f"Risk explanation: {eo.get('riskExplanation', [])}")
        print(f"Recommendation: {eo.get('recommendation', 'N/A')}")
        print(f"Next action: {eo.get('nextAction', 'N/A')}")
        print(f"Limitations: {eo.get('limitations', [])}")
        print(f"Human review required: {eo.get('humanReviewRequired', False)}")
        if eo.get('humanReviewReason'):
            print(f"Human review reason: {eo['humanReviewReason']}")

    if result.get("escalated"):
        print(f"\n{'='*60}")
        print("ESCALATION DETAILS")
        print(f"{'='*60}")
        print(f"Reason: {result.get('escalation_reason', 'N/A')}")
        print(f"Stage: {result.get('escalation_stage', 'N/A')}")

except Exception as e:
    print(f"\nERROR: {e}")
    traceback.print_exc()

# Step 4: Check audit trail
print(f"\n{'='*60}")
print("AUDIT TRAIL")
print(f"{'='*60}")
try:
    timeline = audit_server.get_audit_timeline(case_id)
    for event in timeline:
        print(f"  [{event.get('eventType', '?')}] {event.get('actor', '?')}: {event.get('action', '?')}")
    print(f"  Total events: {len(timeline)}")
except Exception as e:
    print(f"Error fetching audit trail: {e}")

# Step 5: Retrieve final case
print(f"\n{'='*60}")
print("FINAL CASE STATE")
print(f"{'='*60}")
final_case = intake_server.get_intake_case(case_id)
if final_case:
    print(f"  Case ID: {final_case.get('caseId')}")
    print(f"  Status: {final_case.get('status')}")
    print(f"  Risk Level: {final_case.get('riskLevel', 'N/A')}")
    print(f"  Risk Confidence: {final_case.get('riskConfidence', 'N/A')}")
    print(f"  Data Quality: {final_case.get('dataQualityScore', 'N/A')}")
    print(f"  Bias Status: {final_case.get('biasStatus', 'N/A')}")
    print(f"  Human Review: {final_case.get('humanReviewRequired', 'N/A')}")
    print(f"  Human Review Reason: {final_case.get('humanReviewReason', 'N/A')}")

print(f"\n{'='*60}")
print("E2E TEST COMPLETE")
print(f"{'='*60}")
