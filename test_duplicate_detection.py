"""End-to-end test of duplicate detection with weighted fuzzy matching."""
import json
import traceback

import backend.db as db_mod
db_mod._dynamodb_resource = None
db_mod._dynamodb_client = None

from backend.mcp_servers import intake_server, audit_server
from backend.mcp_servers import case_history_server
from backend.agents import duplicate_detector
from backend.workflow.intake_workflow import compile_workflow

print("=" * 70)
print("E2E TEST: Duplicate Detection with Weighted Fuzzy Matching")
print("=" * 70)

# ============================================================
# PHASE 1: Create the ORIGINAL case for Emma Johnson
# ============================================================
print("\n" + "=" * 70)
print("PHASE 1: Creating original case for Emma Johnson")
print("=" * 70)

case1 = intake_server.create_intake_case("mandated-reporter")
case1_id = case1["caseId"]
print(f"Original case created: {case1_id}")

narrative1 = (
    "I am a teacher at Lincoln Elementary School. I need to report a concern about "
    "one of my students, Emma Johnson, age 7, date of birth March 15 2019. "
    "She has bruises on her arms and seems very withdrawn. "
    "Her mother is Sarah Johnson and they live at 142 Oak Street, Springfield, IL 62701. "
    "My name is Patricia Williams and I can be reached at 555-0147."
)

intake_server.save_intake_message(
    case_id=case1_id,
    message_text=narrative1,
    sender_type="user",
    message_type="narrative",
)

print("Running workflow for original case (this takes a few minutes on CPU)...")
workflow = compile_workflow()
try:
    result1 = workflow.invoke({
        "case_id": case1_id,
        "session_messages": [{"role": "user", "content": narrative1}],
        "follow_up_round": 0,
    })
    print(f"Original case result — status: {result1.get('final_status', 'N/A')}")

    intake_output = result1.get("intake_output", {})
    sf = intake_output.get("structuredFields", {})
    print("Extracted fields from original case:")
    for k, v in sf.items():
        val = v.get("value") if isinstance(v, dict) else v
        if val is not None and val != "" and val != []:
            print(f"  {k}: {val}")

except Exception as e:
    print(f"ERROR in phase 1: {e}")
    traceback.print_exc()

# ============================================================
# PHASE 2: Create a DUPLICATE case — same child, different reporter
# ============================================================
print("\n" + "=" * 70)
print("PHASE 2: Creating duplicate case (same child, different reporter)")
print("=" * 70)

case2 = intake_server.create_intake_case("concerned-citizen")
case2_id = case2["caseId"]
print(f"Duplicate case created: {case2_id}")

narrative2 = (
    "I'm a neighbor and I want to report a concern about a little girl named Emma Johnson "
    "who lives at 142 Oak Street in Springfield. She is about 7 years old, born on March 15, 2019. "
    "Her mom is Sarah Johnson. I've seen the child outside crying late at night "
    "and she always looks very scared. I'm worried about her safety. "
    "My name is Robert Chen, phone 555-0298."
)

intake_server.save_intake_message(
    case_id=case2_id,
    message_text=narrative2,
    sender_type="user",
    message_type="narrative",
)

dup_matches = []
dup_pending = False

print("Running workflow for duplicate case...")
try:
    result2 = workflow.invoke({
        "case_id": case2_id,
        "session_messages": [{"role": "user", "content": narrative2}],
        "follow_up_round": 0,
    })

    print(f"\nDuplicate detection results:")
    dup_matches = result2.get("duplicate_matches", [])
    dup_pending = result2.get("duplicate_pending_confirmation", False)
    matched_id = result2.get("matched_case_id")

    if dup_matches:
        print(f"  Matches found: {len(dup_matches)}")
        for m in dup_matches:
            print(f"    Case: {m['caseId']}")
            print(f"    Confidence: {m['confidence']:.1%}")
            print(f"    Reasoning: {m.get('reasoning', 'N/A')}")
            print(f"    Field scores: {json.dumps(m.get('fieldScores', {}), indent=6)}")
            print(f"    Confirmation required: {m.get('confirmationRequired', False)}")
            print(f"    Auto-match: {m.get('autoMatch', False)}")
    else:
        print("  No duplicates detected.")

    print(f"\n  Pending confirmation: {dup_pending}")
    if matched_id:
        print(f"  Auto-matched to: {matched_id}")

    if dup_pending:
        print(f"\n  Workflow paused — waiting for reporter to confirm/deny match")
    else:
        print(f"\n  Workflow status: {result2.get('final_status', 'continued normally')}")

except Exception as e:
    print(f"ERROR in phase 2: {e}")
    traceback.print_exc()

# ============================================================
# PHASE 3: Test the standalone duplicate detector directly
# ============================================================
print("\n" + "=" * 70)
print("PHASE 3: Direct duplicate detector test (no workflow)")
print("=" * 70)

existing_cases = case_history_server.search_existing_cases()
print(f"Existing cases in DB: {len(existing_cases)}")

test_fields = {
    "childName": {"value": "Emma Johnson", "confidence": 0.95},
    "childDob": {"value": "March 15, 2019", "confidence": 0.9},
    "childAge": {"value": 7, "confidence": 0.9},
    "guardianInfo": {"value": "Sarah Johnson", "confidence": 0.8},
    "address": {"value": "142 Oak Street, Springfield", "confidence": 0.85},
}

print("\nTest 1: Same child (Emma Johnson, DOB match, address match)")
matches = duplicate_detector.find_duplicates(test_fields, existing_cases)
if matches:
    for m in matches:
        print(f"  -> {m['caseId']}: {m['confidence']:.1%} confidence "
              f"(confirm={m['confirmationRequired']}, auto={m['autoMatch']})")
else:
    print("  No matches found")

print("\nTest 2: Different child (no match expected)")
test_fields_diff = {
    "childName": {"value": "Michael Brown", "confidence": 0.95},
    "childDob": {"value": "January 5, 2020", "confidence": 0.9},
    "childAge": {"value": 6, "confidence": 0.9},
    "guardianInfo": {"value": "James Brown", "confidence": 0.8},
    "address": {"value": "500 Pine Ave, Chicago, IL", "confidence": 0.85},
}
matches_diff = duplicate_detector.find_duplicates(test_fields_diff, existing_cases)
if matches_diff:
    for m in matches_diff:
        print(f"  -> {m['caseId']}: {m['confidence']:.1%} confidence")
else:
    print("  No matches found (correct!)")

print("\nTest 3: Same name only (low confidence expected)")
test_fields_name_only = {
    "childName": {"value": "Emma Johnson", "confidence": 0.95},
    "childDob": {"value": "June 20, 2022", "confidence": 0.9},
    "guardianInfo": {"value": "Mark Johnson", "confidence": 0.8},
    "address": {"value": "999 Maple Rd, Denver, CO", "confidence": 0.85},
}
matches_name = duplicate_detector.find_duplicates(test_fields_name_only, existing_cases)
if matches_name:
    for m in matches_name:
        print(f"  -> {m['caseId']}: {m['confidence']:.1%} confidence "
              f"(confirm={m['confirmationRequired']}, auto={m['autoMatch']})")
else:
    print("  No matches found")

# ============================================================
# PHASE 4: Test confirm-match API flow
# ============================================================
print("\n" + "=" * 70)
print("PHASE 4: Testing confirm-match merge flow")
print("=" * 70)

if dup_matches and dup_pending:
    print(f"Confirming match: {case2_id} -> {dup_matches[0]['caseId']}")
    matched_case_id = dup_matches[0]["caseId"]

    intake_server.update_intake_case(case2_id, {
        "status": "MERGED",
        "humanReviewReason": f"Merged into {matched_case_id} by reporter confirmation",
    })
    audit_server.save_agent_decision(
        case_id=case2_id,
        agent_name="system",
        output_json={"action": "duplicate_confirmed", "mergedInto": matched_case_id},
    )

    final_original = intake_server.get_intake_case(matched_case_id)
    final_dup = intake_server.get_intake_case(case2_id)

    print(f"\n  Original case ({matched_case_id}):")
    print(f"    Status: {final_original.get('status')}")
    print(f"    Risk Level: {final_original.get('riskLevel', 'N/A')}")

    print(f"\n  Duplicate case ({case2_id}):")
    print(f"    Status: {final_dup.get('status')}")
    print(f"    Human Review Reason: {final_dup.get('humanReviewReason')}")
else:
    print("  Skipping — no duplicate pending confirmation")

print("\n" + "=" * 70)
print("DUPLICATE DETECTION E2E TEST COMPLETE")
print("=" * 70)
