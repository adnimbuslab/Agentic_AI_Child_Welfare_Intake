"""
Comprehensive Demo Script for Agentic AI Child Welfare Intake System
====================================================================
This script exercises the full end-to-end workflow for demonstration purposes.
Run while screen recording to create a demo video for the research paper.

Test Cases Covered:
1. Case 1 (High Risk - Neglect): Teacher reports child neglect with documents
2. Case 2 (Critical Risk): Emergency report of immediate danger
3. Case 3 (Low Risk): Community member reports minor concern
4. Case 4 (Duplicate Detection): Same child reported again
5. Case 5 (Human Review): Supervisor reviews escalated case
6. Dashboard & Case Detail walkthrough via API

Usage:
    source .venv/bin/activate
    python demo_script.py
"""

import requests
import json
import time
import sys
import os

BASE_URL = "http://localhost:8000"
DEMO_DOCS_DIR = os.path.join(os.path.dirname(__file__), "demo_documents")

BOLD = "\033[1m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
RED = "\033[91m"
CYAN = "\033[96m"
MAGENTA = "\033[95m"
RESET = "\033[0m"
SEPARATOR = "=" * 80


def print_header(text):
    print(f"\n{SEPARATOR}")
    print(f"{BOLD}{CYAN}{text}{RESET}")
    print(SEPARATOR)


def print_step(step_num, text):
    print(f"\n{BOLD}{GREEN}[Step {step_num}]{RESET} {text}")


def print_result(label, value, color=RESET):
    print(f"  {YELLOW}{label}:{RESET} {color}{value}{RESET}")


def print_json(data, indent=4):
    print(f"  {json.dumps(data, indent=indent, default=str)}")


AUTO_MODE = "--auto" in sys.argv

def wait_for_user(message="Press Enter to continue to next step..."):
    if AUTO_MODE:
        print(f"\n{MAGENTA}>>> (auto mode: continuing...){RESET}")
        time.sleep(2)
    else:
        input(f"\n{MAGENTA}>>> {message}{RESET}")


def check_health():
    try:
        resp = requests.get(f"{BASE_URL}/health", timeout=5)
        return resp.json().get("status") == "ok"
    except Exception:
        return False


def create_session(reporter_type):
    resp = requests.post(f"{BASE_URL}/intake/session", json={"reporterType": reporter_type})
    resp.raise_for_status()
    return resp.json()


def submit_message(case_id, message_text):
    resp = requests.post(f"{BASE_URL}/intake/message", json={
        "caseId": case_id,
        "messageText": message_text,
    })
    resp.raise_for_status()
    return resp.json()


def upload_document(case_id, file_path, category="other"):
    with open(file_path, "rb") as f:
        resp = requests.post(
            f"{BASE_URL}/intake/upload",
            data={"caseId": case_id, "documentCategory": category},
            files={"file": (os.path.basename(file_path), f, "text/plain")},
        )
    resp.raise_for_status()
    return resp.json()


def list_cases(status=None, risk_level=None):
    params = {"pageSize": 50}
    if status:
        params["status"] = status
    if risk_level:
        params["riskLevel"] = risk_level
    resp = requests.get(f"{BASE_URL}/cases", params=params)
    resp.raise_for_status()
    return resp.json()


def get_case_detail(case_id):
    resp = requests.get(f"{BASE_URL}/cases/{case_id}")
    resp.raise_for_status()
    return resp.json()


def submit_human_review(case_id, action, notes, override_risk=None):
    data = {
        "reviewerId": "supervisor-001",
        "action": action,
        "notes": notes,
    }
    if override_risk:
        data["overrideRiskLevel"] = override_risk
    resp = requests.post(f"{BASE_URL}/cases/{case_id}/human-review", json=data)
    resp.raise_for_status()
    return resp.json()


# ============================================================================
# DEMO CASE 1: Teacher Mandatory Reporter - Child Neglect (High/Critical Risk)
# ============================================================================
def demo_case_1():
    print_header("CASE 1: Teacher Mandatory Reporter - Child Neglect")
    print(f"{BOLD}Scenario:{RESET} A 3rd grade teacher (Sarah Thompson) reports")
    print("suspected neglect of 6-year-old Emma Martinez. The teacher uploads")
    print("her driver's license, the child's birth certificate, a school")
    print("incident report, and medical records as supporting documents.")
    print()
    wait_for_user("Press Enter to start Case 1...")

    # Step 1: Create session
    print_step(1, "Creating intake session (Mandatory Reporter: Teacher)")
    session = create_session("mandatory_reporter_teacher")
    case_id = session["caseId"]
    print_result("Case ID", case_id, GREEN)
    print_result("Session Token", session["sessionToken"])
    print_result("Created At", session["createdAt"])
    time.sleep(1)

    # Step 2: Upload teacher's DL
    print_step(2, "Uploading Teacher's Driver's License")
    dl_path = os.path.join(DEMO_DOCS_DIR, "teacher_drivers_license.txt")
    dl_result = upload_document(case_id, dl_path, "reporter_identification")
    print_result("Document ID", dl_result["documentId"])
    print_result("File Name", dl_result["fileName"])
    print_result("Extraction Status", dl_result["extractionStatus"], GREEN)
    time.sleep(1)

    # Step 3: Upload birth certificate
    print_step(3, "Uploading Child's Birth Certificate")
    bc_path = os.path.join(DEMO_DOCS_DIR, "child_birth_certificate.txt")
    bc_result = upload_document(case_id, bc_path, "child_identification")
    print_result("Document ID", bc_result["documentId"])
    print_result("File Name", bc_result["fileName"])
    print_result("Extraction Status", bc_result["extractionStatus"], GREEN)
    time.sleep(1)

    # Step 4: Upload school incident report
    print_step(4, "Uploading School Incident Report")
    ir_path = os.path.join(DEMO_DOCS_DIR, "school_incident_report.txt")
    ir_result = upload_document(case_id, ir_path, "incident_report")
    print_result("Document ID", ir_result["documentId"])
    print_result("File Name", ir_result["fileName"])
    print_result("Extraction Status", ir_result["extractionStatus"], GREEN)
    time.sleep(1)

    # Step 5: Upload medical records
    print_step(5, "Uploading Medical Records")
    mr_path = os.path.join(DEMO_DOCS_DIR, "medical_records_note.txt")
    mr_result = upload_document(case_id, mr_path, "medical_records")
    print_result("Document ID", mr_result["documentId"])
    print_result("File Name", mr_result["fileName"])
    print_result("Extraction Status", mr_result["extractionStatus"], GREEN)
    time.sleep(1)

    # Step 6: Submit the narrative
    print_step(6, "Submitting Intake Narrative (running all 5 agents)")
    print("  Processing through LangGraph workflow...")
    print("  Agents: Intake Understanding -> Risk Assessment -> Data Quality -> Bias Monitoring -> Explanation")
    print()

    narrative = (
        "I am Sarah Thompson, a 3rd grade teacher at Lincoln Elementary School in "
        "Springfield, Illinois. I am filing this report as a mandatory reporter "
        "regarding one of my students, Emma Martinez, who is 6 years old.\n\n"
        "Over the past several weeks, I have noticed increasing signs of neglect. "
        "Emma has been coming to school in dirty, unchanged clothes for multiple "
        "days in a row. She appears hungry and tired, often falling asleep in class. "
        "She told me that her mother has been 'sleeping a lot' and her father "
        "'hasn't been home.' She mentioned a neighbor sometimes brings her food.\n\n"
        "The school nurse examined Emma and noted a 3-pound weight loss since January. "
        "Emma's hygiene has declined - her hair is matted and she appears unbathed. "
        "No visible bruises or marks, but the pattern of neglect is concerning.\n\n"
        "I have tried contacting both parents multiple times without success. "
        "The mother's phone goes unanswered and the father's goes to voicemail. "
        "Neither parent attended the scheduled parent-teacher conference.\n\n"
        "The child lives at 1847 Oak Street, Springfield, IL 62702 with her mother "
        "Maria Martinez (DOB: 11/22/1990) and father Carlos Martinez (DOB: 05/03/1988). "
        "Emma's date of birth is June 14, 2019.\n\n"
        "I have attached my driver's license, Emma's birth certificate, a school "
        "incident report documenting the pattern, and medical records from a recent "
        "pediatric visit showing weight loss and developmental concerns."
    )

    start_time = time.time()
    result = submit_message(case_id, narrative)
    elapsed = time.time() - start_time

    print_result("Processing Time", f"{elapsed:.1f} seconds")
    print_result("Agent Response", result["agentResponse"][:200] + "...")
    print_result("Intake Complete", result["intakeComplete"], GREEN if result["intakeComplete"] else YELLOW)
    print_result("Follow-Up Questions", len(result.get("followUpQuestions", [])))

    if result.get("followUpQuestions"):
        print(f"\n  {YELLOW}Follow-up questions from agent:{RESET}")
        for q in result["followUpQuestions"]:
            print(f"    - {q}")

    # Step 7: Answer follow-up questions if any
    if result.get("followUpQuestions") and not result.get("intakeComplete"):
        time.sleep(2)
        print_step(7, "Answering Follow-Up Questions")

        follow_up_answer = (
            "To answer the follow-up questions:\n"
            "- The most recent incident was today, May 20, 2026\n"
            "- Emma is currently safe at school, we have given her clean clothes and food\n"
            "- The type of concern is neglect - lack of adequate food, hygiene, and supervision\n"
            "- I have not been able to reach either parent by phone\n"
            "- There is no known history of prior CPS involvement that I am aware of\n"
            "- Emma does not have any known disabilities or special needs\n"
            "- The father's absence appears to be recent based on what Emma has said\n"
            "- The mother's behavior change (excessive sleeping) started about a month ago\n"
            "- No other children in the household that I know of\n"
            "- Emma appears afraid to go home and has asked to stay at school"
        )

        result2 = submit_message(case_id, follow_up_answer)
        print_result("Agent Response", result2["agentResponse"][:200] + "...")
        print_result("Intake Complete", result2.get("intakeComplete", False), GREEN if result2.get("intakeComplete", False) else YELLOW)
    time.sleep(1)

    # Step 8: View case detail
    print_step(8, "Retrieving Full Case Detail")
    detail = get_case_detail(case_id)
    case_data = detail.get("case", {})
    print_result("Status", case_data.get("status"), RED if "ESCALATED" in str(case_data.get("status", "")) else GREEN)
    print_result("Risk Level", case_data.get("riskLevel"), RED if case_data.get("riskLevel") in ("High", "Critical") else GREEN)
    print_result("Urgency", case_data.get("urgency"))
    print_result("Data Quality", case_data.get("dataQualityScore"))
    print_result("Bias Status", case_data.get("biasStatus"))
    print_result("Human Review Required", case_data.get("humanReviewRequired"))

    agents = detail.get("agentOutputs", [])
    if agents:
        print(f"\n  {BOLD}Agent Decisions:{RESET}")
        for agent in agents:
            name = agent.get("agentName", "unknown")
            conf = agent.get("confidenceScore", "N/A")
            esc = agent.get("escalationReason", "")
            print(f"    {CYAN}{name}{RESET}: confidence={conf}" + (f" | ESCALATED: {esc}" if esc else ""))

    docs = detail.get("documents", [])
    if docs:
        print(f"\n  {BOLD}Uploaded Documents ({len(docs)}):{RESET}")
        for doc in docs:
            print(f"    - {doc.get('fileName')} [{doc.get('documentCategory', 'other')}] - {doc.get('extractionStatus')}")

    audit = detail.get("auditEvents", [])
    if audit:
        print(f"\n  {BOLD}Audit Trail ({len(audit)} events):{RESET}")
        for event in audit[:5]:
            print(f"    [{event.get('createdAt', '')[:19]}] {event.get('eventType')} by {event.get('actor')}")

    return case_id


# ============================================================================
# DEMO CASE 2: Emergency - Immediate Danger (Critical Risk)
# ============================================================================
def demo_case_2():
    print_header("CASE 2: Emergency Report - Immediate Danger (Critical Risk)")
    print(f"{BOLD}Scenario:{RESET} A neighbor calls to report a child locked outside")
    print("in freezing weather while a domestic violence incident occurs inside.")
    print("This should trigger CRITICAL risk and immediate supervisor escalation.")
    print()
    wait_for_user("Press Enter to start Case 2...")

    print_step(1, "Creating emergency intake session")
    session = create_session("community_member")
    case_id = session["caseId"]
    print_result("Case ID", case_id, GREEN)

    print_step(2, "Submitting emergency narrative")
    narrative = (
        "I am calling because there is a 4-year-old child locked outside the house "
        "next door at 892 Pine Street, Springfield, IL. It is currently 28 degrees "
        "outside and the child is wearing only a thin t-shirt and shorts. The child "
        "is crying and banging on the door.\n\n"
        "I can hear violent screaming and sounds of things breaking inside the house. "
        "It sounds like a man and woman fighting. I believe the parents are David "
        "and Jennifer Wilson. The child's name is Tyler. I have seen bruises on "
        "Tyler before.\n\n"
        "I called 911 already and police are on the way. But the child has been "
        "outside for at least 20 minutes and is shivering. I brought a blanket "
        "out to him but he is very scared and won't stop crying. He said 'daddy "
        "is hurting mommy again.'\n\n"
        "This is not the first time. I have heard fighting from that house at "
        "least once a week for the past two months. Last month I saw Jennifer "
        "with a black eye. The child Tyler seems to be getting more withdrawn.\n\n"
        "My name is Patricia Chen, I live at 894 Pine Street. My phone is "
        "(217) 555-0891. Please send someone immediately, this child is in danger."
    )

    start_time = time.time()
    result = submit_message(case_id, narrative)
    elapsed = time.time() - start_time

    print_result("Processing Time", f"{elapsed:.1f} seconds")
    print_result("Agent Response", result["agentResponse"][:200] + "...")
    print_result("Intake Complete", result.get("intakeComplete"))

    if result.get("followUpQuestions") and not result.get("intakeComplete"):
        time.sleep(2)
        print_step(3, "Answering follow-up questions")
        follow_up = (
            "Tyler Wilson appears to be about 4 years old. I don't know his exact "
            "birthday. He is a white male child with brown hair. The father David "
            "Wilson is a large man, maybe 6 feet tall, and I've seen him drink heavily. "
            "The mother Jennifer is petite and often looks tired and scared. "
            "I don't know if there are other children. Tyler goes to a daycare "
            "nearby but I don't know which one. The situation is happening right now "
            "and police should be arriving any minute. Please hurry."
        )
        result2 = submit_message(case_id, follow_up)
        print_result("Agent Response", result2["agentResponse"][:200] + "...")

    print_step(4, "Checking case status")
    detail = get_case_detail(case_id)
    case_data = detail.get("case", {})
    print_result("Status", case_data.get("status"), RED)
    print_result("Risk Level", case_data.get("riskLevel"), RED)
    print_result("Urgency", case_data.get("urgency"), RED)
    print_result("Human Review Required", case_data.get("humanReviewRequired"))
    print_result("Human Review Reason", case_data.get("humanReviewReason"))

    return case_id


# ============================================================================
# DEMO CASE 3: Low Risk - Minor Concern
# ============================================================================
def demo_case_3():
    print_header("CASE 3: Community Report - Minor Concern (Low Risk)")
    print(f"{BOLD}Scenario:{RESET} A school counselor reports mild behavioral changes")
    print("in a well-cared-for student. Expected: Low risk, minimal escalation.")
    print()
    wait_for_user("Press Enter to start Case 3...")

    print_step(1, "Creating intake session")
    session = create_session("mandatory_reporter_counselor")
    case_id = session["caseId"]
    print_result("Case ID", case_id, GREEN)

    print_step(2, "Submitting narrative")
    narrative = (
        "I am a school counselor at Washington Middle School, Springfield, IL. "
        "I want to report some mild behavioral changes I've noticed in one of "
        "our students, Jake Roberts, age 11 (DOB: 08/22/2014).\n\n"
        "Jake has been a good student with generally happy demeanor. Over the past "
        "two weeks, he has seemed a bit more quiet than usual and mentioned that "
        "his parents are 'arguing more.' He said he sometimes goes to his room "
        "to avoid the noise.\n\n"
        "Jake appears well-fed, well-dressed, and physically healthy. He continues "
        "to attend school regularly and his grades remain good. His parents recently "
        "attended a parent-teacher conference and both appeared caring and engaged.\n\n"
        "I believe the parents may be going through marital difficulties. Jake "
        "seems emotionally affected but not in any danger. He lives at 456 Elm "
        "Street, Springfield, IL with both parents, Robert and Lisa Roberts.\n\n"
        "I wanted to file this report for documentation purposes. I am continuing "
        "to monitor Jake and have offered him regular check-ins at school.\n\n"
        "Contact: Sarah Williams, School Counselor, (217) 555-0234"
    )

    start_time = time.time()
    result = submit_message(case_id, narrative)
    elapsed = time.time() - start_time

    print_result("Processing Time", f"{elapsed:.1f} seconds")
    print_result("Agent Response", result["agentResponse"][:200] + "...")
    print_result("Intake Complete", result.get("intakeComplete"))

    if result.get("followUpQuestions") and not result.get("intakeComplete"):
        time.sleep(2)
        print_step(3, "Answering follow-up questions")
        follow_up = (
            "Jake's parents are Robert Roberts (DOB: 03/11/1980) and Lisa Roberts "
            "(DOB: 07/25/1982). They live at 456 Elm Street, Springfield, IL 62704. "
            "There are no other children in the home. Jake has no known disabilities. "
            "There is no history of violence - just verbal arguments. Jake is not "
            "afraid of either parent and says they are both nice to him. I have no "
            "reason to believe Jake is being abused or neglected."
        )
        result2 = submit_message(case_id, follow_up)
        print_result("Agent Response", result2["agentResponse"][:200] + "...")

    print_step(4, "Checking case status")
    detail = get_case_detail(case_id)
    case_data = detail.get("case", {})
    print_result("Status", case_data.get("status"), GREEN)
    print_result("Risk Level", case_data.get("riskLevel"), GREEN)
    print_result("Urgency", case_data.get("urgency"))
    print_result("Data Quality", case_data.get("dataQualityScore"))
    print_result("Bias Status", case_data.get("biasStatus"))

    return case_id


# ============================================================================
# DEMO CASE 4: Duplicate Detection
# ============================================================================
def demo_case_4():
    print_header("CASE 4: Duplicate Detection Test")
    print(f"{BOLD}Scenario:{RESET} A second reporter calls about the same child")
    print("(Emma Martinez) from Case 1. The system should detect the duplicate")
    print("and ask for confirmation before merging.")
    print()
    wait_for_user("Press Enter to start Case 4...")

    print_step(1, "Creating new intake session (different reporter)")
    session = create_session("community_member")
    case_id = session["caseId"]
    print_result("Case ID", case_id, GREEN)

    print_step(2, "Submitting narrative about same child")
    narrative = (
        "I want to report a concern about a child in my neighborhood. Her name "
        "is Emma Martinez. She lives at 1847 Oak Street in Springfield. She is "
        "about 6 years old.\n\n"
        "I am a neighbor and I have noticed that Emma has been outside alone "
        "several evenings recently. She looks hungry and I have been giving her "
        "snacks. Her mother Maria does not seem to be taking care of her properly. "
        "I haven't seen the father Carlos in weeks.\n\n"
        "My name is Dorothy Chen, I live at 1849 Oak Street. Phone: (217) 555-0567."
    )

    start_time = time.time()
    result = submit_message(case_id, narrative)
    elapsed = time.time() - start_time

    print_result("Processing Time", f"{elapsed:.1f} seconds")
    print_result("Agent Response", result["agentResponse"][:300])

    if result.get("duplicateMatch"):
        match = result["duplicateMatch"]
        print(f"\n  {RED}{BOLD}DUPLICATE DETECTED!{RESET}")
        print_result("Matched Case ID", match["matchedCaseId"], RED)
        print_result("Confidence", f"{match['confidence']:.0%}", RED)
        print_result("Reasoning", match.get("reasoning", "N/A"))
        print_result("Confirmation Required", match.get("confirmationRequired"))
    else:
        print(f"\n  {YELLOW}No duplicate detected (first report may not have been saved yet){RESET}")

    return case_id


# ============================================================================
# DEMO CASE 5: Human Review Workflow
# ============================================================================
def demo_case_5(escalated_case_id):
    print_header("CASE 5: Human Review / Supervisor Workflow")
    print(f"{BOLD}Scenario:{RESET} A supervisor reviews an escalated case,")
    print("examines agent decisions, and either approves or overrides.")
    print()
    wait_for_user("Press Enter to start Human Review demo...")

    # List escalated cases
    print_step(1, "Listing all cases requiring human review")
    all_cases = list_cases()
    escalated = [c for c in all_cases.get("cases", []) if c.get("humanReviewRequired")]
    print_result("Total Cases", all_cases.get("totalCount", 0))
    print_result("Cases Needing Review", len(escalated), RED if escalated else GREEN)

    for c in escalated:
        print(f"    {CYAN}{c['caseId']}{RESET}: {c.get('status')} | Risk: {c.get('riskLevel', 'N/A')} | {c.get('humanReviewReason', 'N/A')[:60]}")

    if not escalated:
        print(f"  {YELLOW}No escalated cases found. Using provided case ID: {escalated_case_id}{RESET}")
        target_case = escalated_case_id
    else:
        target_case = escalated[0]["caseId"]

    # View the case detail
    print_step(2, f"Supervisor reviewing case: {target_case}")
    try:
        detail = get_case_detail(target_case)
        case_data = detail.get("case", {})
        print_result("Current Status", case_data.get("status"))
        print_result("Risk Level", case_data.get("riskLevel"))
        print_result("Review Reason", case_data.get("humanReviewReason"))

        agents = detail.get("agentOutputs", [])
        if agents:
            print(f"\n  {BOLD}Agent Decision Chain:{RESET}")
            for agent in agents:
                name = agent.get("agentName", "unknown")
                conf = agent.get("confidenceScore", "N/A")
                esc = "YES" if agent.get("escalationReason") else "NO"
                print(f"    {CYAN}{name}{RESET}: confidence={conf}, escalated={esc}")
    except Exception as e:
        print(f"  {RED}Could not retrieve case detail: {e}{RESET}")

    # Submit human review
    print_step(3, "Supervisor approving case with notes")
    try:
        review_result = submit_human_review(
            target_case,
            action="approve",
            notes="Reviewed all agent outputs and uploaded documents. "
                  "Risk assessment aligns with evidence. Approving for investigation assignment."
        )
        print_result("Review Status", "Submitted", GREEN)
        print_result("Response", str(review_result)[:200])
    except Exception as e:
        print(f"  {YELLOW}Human review submission: {e}{RESET}")
        print(f"  {YELLOW}(This is expected if case status doesn't allow review){RESET}")

    return target_case


# ============================================================================
# DEMO: Dashboard Overview
# ============================================================================
def demo_dashboard():
    print_header("DASHBOARD OVERVIEW: All Cases Summary")
    wait_for_user("Press Enter to view dashboard summary...")

    print_step(1, "Fetching all cases")
    all_cases = list_cases()
    cases = all_cases.get("cases", [])
    print_result("Total Cases", all_cases.get("totalCount", 0))

    if cases:
        print(f"\n  {'Case ID':<20} {'Status':<35} {'Risk':<10} {'Urgency':<10} {'Quality':<10} {'Bias':<10} {'Review':<8}")
        print(f"  {'-'*18:<20} {'-'*33:<35} {'-'*8:<10} {'-'*8:<10} {'-'*8:<10} {'-'*8:<10} {'-'*6:<8}")
        for c in cases:
            risk = c.get("riskLevel", "N/A")
            risk_color = RED if risk in ("High", "Critical") else (YELLOW if risk == "Medium" else GREEN)
            quality = c.get("dataQualityScore", "N/A")
            if quality != "N/A":
                try:
                    quality = f"{float(quality)*100:.0f}%"
                except (ValueError, TypeError):
                    pass
            print(f"  {c['caseId']:<20} {str(c.get('status', 'N/A'))[:33]:<35} {risk_color}{risk:<10}{RESET} {str(c.get('urgency', 'N/A')):<10} {str(quality):<10} {str(c.get('biasStatus', 'N/A')):<10} {str(c.get('humanReviewRequired', False)):<8}")

    # Show by risk level
    print_step(2, "Cases by Risk Level")
    for level in ["Critical", "High", "Medium", "Low"]:
        filtered = list_cases(risk_level=level)
        count = filtered.get("totalCount", 0)
        color = RED if level in ("Critical", "High") else (YELLOW if level == "Medium" else GREEN)
        print(f"  {color}{level}: {count} case(s){RESET}")


# ============================================================================
# MAIN DEMO ORCHESTRATION
# ============================================================================
def main():
    print(f"\n{BOLD}{CYAN}")
    print("  ╔══════════════════════════════════════════════════════════════╗")
    print("  ║                                                            ║")
    print("  ║   AGENTIC AI CHILD WELFARE INTAKE SYSTEM                   ║")
    print("  ║   End-to-End Demo for Research Paper                       ║")
    print("  ║                                                            ║")
    print("  ║   Multi-Agent Orchestration with LangGraph                 ║")
    print("  ║   5 AI Agents | 7 MCP Servers | LocalStack AWS             ║")
    print("  ║                                                            ║")
    print("  ╚══════════════════════════════════════════════════════════════╝")
    print(f"{RESET}")

    print(f"  {BOLD}System Components:{RESET}")
    print("  - LLM: Ollama (llama3.2:3b) for local demo")
    print("  - Backend: FastAPI + LangGraph workflow")
    print("  - Frontend: React (http://localhost:3000)")
    print("  - Infrastructure: LocalStack (DynamoDB, S3)")
    print()
    print(f"  {BOLD}Demo Test Cases:{RESET}")
    print("  1. High/Critical Risk: Teacher reports child neglect with 4 documents")
    print("  2. Critical Risk: Emergency - child in immediate danger")
    print("  3. Low Risk: Minor behavioral concern (baseline comparison)")
    print("  4. Duplicate Detection: Same child reported by different reporter")
    print("  5. Human Review: Supervisor reviews and approves escalated case")
    print("  6. Dashboard: Overview of all cases and filtering")
    print()

    # Pre-flight checks
    print_step(0, "Pre-flight System Check")
    if not check_health():
        print(f"  {RED}Backend is not running! Start with: source .venv/bin/activate && python run.py{RESET}")
        sys.exit(1)
    print_result("Backend", "OK", GREEN)
    print_result("Frontend", "http://localhost:3000", GREEN)
    print_result("LocalStack", "http://localhost:4566", GREEN)

    try:
        ollama_resp = requests.get("http://localhost:11434/api/tags", timeout=3)
        models = [m["name"] for m in ollama_resp.json().get("models", [])]
        print_result("Ollama Models", ", ".join(models), GREEN)
    except Exception:
        print_result("Ollama", "Not available (will use fallback)", YELLOW)

    wait_for_user("All systems ready. Press Enter to begin demo...")

    # Run all demo cases
    case1_id = demo_case_1()

    time.sleep(2)
    case2_id = demo_case_2()

    time.sleep(2)
    case3_id = demo_case_3()

    time.sleep(2)
    case4_id = demo_case_4()

    time.sleep(2)
    demo_case_5(case2_id)

    time.sleep(2)
    demo_dashboard()

    # Final summary
    print_header("DEMO COMPLETE")
    print(f"""
  {BOLD}Summary of Demo Cases:{RESET}
  - Case 1 ({case1_id}): Teacher neglect report with 4 documents
  - Case 2 ({case2_id}): Emergency critical risk report
  - Case 3 ({case3_id}): Low risk behavioral concern
  - Case 4 ({case4_id}): Duplicate detection test
  - Human review workflow demonstrated on escalated case

  {BOLD}Key Capabilities Demonstrated:{RESET}
  1. Multi-agent orchestration (5 AI agents via LangGraph)
  2. Document upload and text extraction
  3. Risk assessment with confidence scoring
  4. Data quality validation
  5. Bias monitoring and fairness review
  6. Duplicate case detection (weighted fuzzy matching)
  7. Human-in-the-loop escalation workflow
  8. Immutable audit trail
  9. Caseworker dashboard with filtering
  10. Full case detail with agent decision transparency

  {BOLD}Architecture Highlights:{RESET}
  - All agent-to-backend communication via MCP servers (no direct DB calls)
  - Single-point LLM configuration (swap model via env vars)
  - LocalStack for AWS simulation (DynamoDB, S3)
  - Configurable confidence thresholds
  - Real-time workflow state management

  {CYAN}Frontend is running at: http://localhost:3000{RESET}
  {CYAN}Open in browser to see the UI with all created cases.{RESET}
    """)


if __name__ == "__main__":
    main()
