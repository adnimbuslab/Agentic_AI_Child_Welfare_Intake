"""Check case status and test follow-up submission."""
import traceback
from backend.mcp_servers import intake_server
from backend.workflow.intake_workflow import compile_workflow

case_id = "CW-2026-7545"
case = intake_server.get_intake_case(case_id)
print(f"Status: {case['status']}")
print(f"Follow-up round: {case.get('followUpRound', 0)}")

# Simulate the follow-up message submission
intake_server.save_intake_message(
    case_id=case_id,
    message_text="I believe this is physical abuse. The bruises look like grip marks and she is afraid of going home.",
    sender_type="user",
    message_type="follow-up-answer",
)

messages = intake_server.get_intake_messages(case_id)
session_messages = [
    {"role": "user" if m["senderType"] == "user" else "assistant", "content": m["messageText"]}
    for m in messages
]
print(f"Total messages: {len(session_messages)}")

workflow = compile_workflow()
try:
    result = workflow.invoke({
        "case_id": case_id,
        "session_messages": session_messages,
        "extracted_document_texts": None,
        "follow_up_round": case.get("followUpRound", 0),
    })
    print(f"Workflow completed! Final status: {result.get('final_status')}")
    print(f"Escalated: {result.get('escalated')}")
    if result.get("risk_output"):
        print(f"Risk level: {result['risk_output'].get('riskLevel')}")
except Exception as e:
    print(f"ERROR: {e}")
    traceback.print_exc()
