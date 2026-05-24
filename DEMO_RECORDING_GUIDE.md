# Demo Recording Guide - 10 Minute Video

## Recording Setup
- Use **QuickTime Player** (Mac) > File > New Screen Recording, or **OBS Studio**
- Resolution: 1920x1080 recommended
- Record both screen and audio narration

## Pre-Recording Checklist
1. Docker running with LocalStack: `docker-compose up -d`
2. Backend running: `source .venv/bin/activate && python run.py`
3. Frontend running: `cd frontend && npm run dev` (http://localhost:3000)
4. Ollama running: `ollama serve`
5. Open browser to http://localhost:3000
6. Open terminal for the demo script

---

## Video Script (10 Minutes)

### Segment 1: Introduction (0:00 - 1:00)
**Show:** Architecture diagram or title slide

**Narrate:**
> "This is a demonstration of the Agentic AI Child Welfare Intake System, a proof-of-concept that uses multi-agent AI orchestration to assist child welfare intake processes. The system uses 5 specialized AI agents coordinated through LangGraph, communicating via MCP servers, running on simulated AWS infrastructure via LocalStack."

**Show:** Terminal with `docker ps` and `curl localhost:8000/health`

### Segment 2: Start New Intake - UI (1:00 - 2:30)
**Show:** Browser at http://localhost:3000

1. Click "Start Intake Session" button
2. Show the case ID generated (CW-YYYY-NNNN format)
3. Upload documents one by one:
   - `demo_documents/teacher_drivers_license.txt` (Reporter ID)
   - `demo_documents/child_birth_certificate.txt` (Child ID)
   - `demo_documents/school_incident_report.txt` (Incident Report)
   - `demo_documents/medical_records_note.txt` (Medical Records)
4. Show upload confirmations

### Segment 3: Submit Narrative (2:30 - 4:30)
**Type in chat (or paste):**
> I am Sarah Thompson, a 3rd grade teacher at Lincoln Elementary School. I am filing this report as a mandatory reporter regarding my student Emma Martinez, age 6. Over the past several weeks, I have noticed signs of neglect. Emma comes to school in dirty, unchanged clothes. She appears hungry and tired. She told me her mother has been 'sleeping a lot' and her father 'hasn't been home.' The school nurse noted weight loss. The child lives at 1847 Oak Street, Springfield, IL 62702 with parents Maria and Carlos Martinez.

**Show:** The "Processing..." state while agents run
**Show:** The agent response with follow-up questions or completion

**Narrate:** Explain that the system is running through 5 agents:
1. Intake Understanding - extracts structured fields
2. Risk Assessment - evaluates danger level
3. Data Quality - validates completeness
4. Bias Monitoring - checks for fairness
5. Explanation - generates caseworker summary

### Segment 4: Answer Follow-ups (4:30 - 5:30)
**If follow-up questions appear, answer them**

**Show:** The progress bar updating
**Show:** The intake completion message

### Segment 5: Dashboard View (5:30 - 6:30)
**Navigate to:** http://localhost:3000/dashboard

**Show:**
- Case list with status, risk level, urgency
- Risk level color coding (Green/Yellow/Orange/Red)
- Filter by status (escalated cases)
- Filter by risk level

### Segment 6: Case Detail Deep Dive (6:30 - 8:00)
**Click on the case ID** to open detail view

**Show each tab:**
1. **Summary** - AI-generated caseworker summary
2. **Fields** - Structured data extracted with confidence scores
3. **Documents** - Uploaded documents and extraction status
4. **Messages** - Full conversation history
5. **Agents** - Each agent's output with confidence scores
6. **Audit** - Complete immutable audit trail

### Segment 7: Human Review (8:00 - 9:00)
**Navigate to:** http://localhost:3000/review

**Show:**
- Escalated cases queue
- Click "Review" on a case
- Show the review modal (Approve / Override Risk / Request More Info)
- Add reviewer notes
- Submit review

### Segment 8: Terminal Demo Script (9:00 - 9:45)
**Show:** Terminal running `python demo_script.py`

**Narrate:** Briefly show the automated test running multiple cases:
- Emergency critical risk case
- Low risk case for comparison
- Duplicate detection test

### Segment 9: Conclusion (9:45 - 10:00)
**Show:** Final dashboard with all test cases

**Narrate:**
> "This demonstrates how multi-agent AI orchestration can assist child welfare intake processes while maintaining human oversight for critical decisions. The system ensures transparency through immutable audit trails, fairness through bias monitoring, and safety through configurable human-in-the-loop escalation."

---

## Quick Commands Reference
```bash
# Start everything
docker-compose up -d
source .venv/bin/activate
python run.py &
cd frontend && npm run dev &

# Run automated demo
python demo_script.py

# View database contents
python view_dynamo.py
```
