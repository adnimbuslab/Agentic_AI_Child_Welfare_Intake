"""Create a 2-minute demo walkthrough video from the running local app.

Prereqs:
  - LocalStack, backend, frontend, and Ollama are running
  - `python3 -m playwright` / Playwright browsers are installed
  - ffmpeg is available
"""

from pathlib import Path
import subprocess
import textwrap

from playwright.sync_api import sync_playwright


ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "demo_recording_assets"
FRAME_DIR = OUT_DIR / "frames"
VIDEO_PATH = ROOT / "demo_10_min_walkthrough.mp4"
FRONTEND = "http://127.0.0.1:3000"
API = "http://127.0.0.1:8000"
VIEWPORT = {"width": 1920, "height": 1080}


SLIDES = [
    ("01_intake_start.png", 7),
    ("02_session_started.png", 7),
    ("03_documents_uploaded.png", 9),
    ("04_narrative_ready.png", 8),
    ("05_dashboard_all_cases.png", 10),
    ("06_dashboard_escalated.png", 8),
    ("07_case_summary.png", 11),
    ("08_case_fields.png", 9),
    ("09_case_documents.png", 8),
    ("11_case_agents.png", 11),
    ("12_case_audit.png", 8),
    ("13_human_review_queue.png", 8),
    ("14_human_review_modal.png", 8),
    ("15_terminal_summary.png", 10),
    ("16_conclusion.png", 8),
]


def add_caption(page, title, subtitle):
    page.evaluate(
        """({ title, subtitle }) => {
            document.querySelector('[data-demo-caption]')?.remove();
            const box = document.createElement('div');
            box.dataset.demoCaption = 'true';
            box.style.cssText = [
              'position:fixed',
              'left:40px',
              'right:40px',
              'bottom:34px',
              'z-index:999999',
              'background:rgba(20,28,38,0.92)',
              'color:white',
              'padding:20px 26px',
              'border-radius:8px',
              'box-shadow:0 12px 40px rgba(0,0,0,0.28)',
              'font-family:Inter,Arial,sans-serif'
            ].join(';');
            const h = document.createElement('div');
            h.textContent = title;
            h.style.cssText = 'font-size:28px;font-weight:700;margin-bottom:6px';
            const p = document.createElement('div');
            p.textContent = subtitle;
            p.style.cssText = 'font-size:18px;line-height:1.35;color:#dbeafe';
            box.append(h, p);
            document.body.appendChild(box);
        }""",
        {"title": title, "subtitle": subtitle},
    )


def snap(page, name, title, subtitle):
    add_caption(page, title, subtitle)
    page.wait_for_timeout(500)
    page.screenshot(path=FRAME_DIR / name, full_page=False)


def build_terminal_slide(page, name):
    html = """
    <html>
    <head>
      <style>
        body { margin:0; background:#101820; color:#f5f7fb; font-family:Arial,sans-serif; }
        .wrap { padding:54px 70px; }
        h1 { font-size:42px; margin:0 0 10px; }
        .sub { color:#9fb3c8; font-size:20px; margin-bottom:30px; }
        pre {
          background:#05080d; color:#d7fbe8; padding:28px; border-radius:8px;
          font: 22px/1.45 Menlo, Monaco, Consolas, monospace;
          box-shadow:0 20px 60px rgba(0,0,0,.35);
          white-space:pre-wrap;
        }
      </style>
    </head>
    <body>
      <div class="wrap">
        <h1>Automated demo script results</h1>
        <div class="sub">All five API workflow scenarios completed and populated the dashboard.</div>
        <pre>python demo_script.py --auto

--- Demo Results Summary ---
Total cases: 5
CW-2026-1249: ESCALATED_TO_SUPERVISOR | Risk: High   | Review: True
CW-2026-8186: ESCALATED_TO_SUPERVISOR | Risk: Medium | Review: True
CW-2026-4456: ESCALATED_TO_SUPERVISOR | Risk: Medium | Review: True
CW-2026-6605: READY_FOR_CASEWORKER_REVIEW | Risk: Medium | Review: False
CW-2026-2492: ESCALATED_TO_SUPERVISOR | Risk: High   | Review: True

Services used:
LocalStack DynamoDB/S3, FastAPI, React, Ollama llama3.2:3b, LangGraph agents.</pre>
      </div>
    </body>
    </html>
    """
    page.set_content(html)
    page.screenshot(path=FRAME_DIR / name, full_page=False)


def build_conclusion_slide(page, name):
    html = """
    <html>
    <head>
      <style>
        body { margin:0; font-family:Arial,sans-serif; color:#17202a; background:#eef4f8; }
        .wrap { padding:86px 90px; }
        h1 { font-size:54px; margin:0 0 20px; }
        .grid { display:grid; grid-template-columns:1fr 1fr; gap:22px; max-width:1400px; }
        .card { background:white; border-radius:8px; padding:28px; box-shadow:0 10px 30px rgba(0,0,0,.10); }
        .card h2 { margin:0 0 12px; font-size:28px; color:#0b65a3; }
        .card p { margin:0; font-size:22px; line-height:1.45; color:#34495e; }
      </style>
    </head>
    <body>
      <div class="wrap">
        <h1>Agentic AI Child Welfare Intake System</h1>
        <div class="grid">
          <div class="card"><h2>Multi-agent workflow</h2><p>Intake understanding, risk assessment, data quality, bias monitoring, and explanation generation run as an auditable chain.</p></div>
          <div class="card"><h2>Human oversight</h2><p>High-risk, low-confidence, or flagged cases are routed to supervisor review before final caseworker handoff.</p></div>
          <div class="card"><h2>Document support</h2><p>Reporter ID, child identity, incident reports, and medical notes are stored and surfaced alongside the case.</p></div>
          <div class="card"><h2>Auditability</h2><p>Every major system and reviewer action is preserved for transparency and accountability.</p></div>
        </div>
      </div>
    </body>
    </html>
    """
    page.set_content(html)
    page.screenshot(path=FRAME_DIR / name, full_page=False)


def capture_frames():
    FRAME_DIR.mkdir(parents=True, exist_ok=True)
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page(viewport=VIEWPORT)

        page.goto(FRONTEND, wait_until="networkidle")
        snap(
            page,
            "01_intake_start.png",
            "Start a new intake",
            "The reporter begins a child welfare intake in the React interface.",
        )

        page.get_by_text("Start Intake Session").click()
        page.wait_for_selector("text=Case:")
        snap(
            page,
            "02_session_started.png",
            "Session and case ID created",
            "The backend creates a case record and returns a CW-YYYY-NNNN identifier.",
        )

        uploads = [
            ("reporter_identification", "teacher_drivers_license.txt"),
            ("child_identification", "child_birth_certificate.txt"),
            ("incident_report", "school_incident_report.txt"),
            ("medical_records", "medical_records_note.txt"),
        ]
        for category, filename in uploads:
            page.locator("select").select_option(category)
            page.locator("input[type=file]").set_input_files(ROOT / "demo_documents" / filename)
            page.wait_for_timeout(900)
        snap(
            page,
            "03_documents_uploaded.png",
            "Supporting documents attached",
            "Document metadata and extracted text are stored for the agent workflow and later review.",
        )

        narrative = (
            "I am Sarah Thompson, a 3rd grade teacher at Lincoln Elementary School. "
            "I am filing this report as a mandatory reporter regarding my student Emma Martinez, age 6. "
            "Over the past several weeks, Emma comes to school in dirty clothes, appears hungry and tired, "
            "and the nurse noted weight loss."
        )
        page.locator("textarea").fill(narrative)
        snap(
            page,
            "04_narrative_ready.png",
            "Narrative intake ready for agents",
            "The full demo script submits this narrative to the LangGraph agent workflow.",
        )

        page.goto(f"{FRONTEND}/dashboard", wait_until="networkidle")
        snap(
            page,
            "05_dashboard_all_cases.png",
            "Caseworker dashboard",
            "Completed demo cases are listed with status, risk level, urgency, quality, and review indicators.",
        )

        page.locator("select").first.select_option("ESCALATED_TO_SUPERVISOR")
        page.wait_for_timeout(900)
        snap(
            page,
            "06_dashboard_escalated.png",
            "Escalation filtering",
            "The dashboard can focus on supervisor escalations for rapid triage.",
        )

        page.goto(f"{FRONTEND}/dashboard", wait_until="networkidle")
        page.get_by_role("link", name="CW-2026-1249").click()
        page.wait_for_selector("text=Back to Dashboard")
        snap(page, "07_case_summary.png", "Case detail: summary", "The case summary gives caseworkers a concise AI-generated explanation and recommendation.")
        for tab, name, title, subtitle in [
            ("Fields", "08_case_fields.png", "Structured field extraction", "Key entities and facts are normalized with confidence scores."),
            ("Documents", "09_case_documents.png", "Document evidence", "Uploaded files remain linked to the case record for review."),
            ("Messages", "10_case_messages.png", "Reporter conversation", "The full intake conversation is preserved for context."),
            ("Agents", "11_case_agents.png", "Agent outputs", "Each agent decision is visible with JSON output, status, and confidence."),
            ("Audit", "12_case_audit.png", "Immutable audit trail", "System and reviewer actions are captured for transparency."),
        ]:
            page.get_by_text(tab, exact=True).click()
            page.wait_for_timeout(700)
            snap(page, name, title, subtitle)

        page.goto(f"{FRONTEND}/review", wait_until="networkidle")
        snap(
            page,
            "13_human_review_queue.png",
            "Human review queue",
            "Cases requiring oversight are routed to supervisors with escalation reasons.",
        )
        if page.get_by_text("Review", exact=True).count():
            page.get_by_text("Review", exact=True).first.click()
            page.wait_for_timeout(500)
            page.locator("textarea").fill("Supervisor reviewed AI recommendation and supporting documents.")
        snap(
            page,
            "14_human_review_modal.png",
            "Supervisor review action",
            "The reviewer can approve, override risk, or request more information with notes.",
        )

        build_terminal_slide(page, "15_terminal_summary.png")
        build_conclusion_slide(page, "16_conclusion.png")
        browser.close()


def build_video():
    concat = OUT_DIR / "concat.txt"
    with concat.open("w", encoding="utf-8") as fh:
        for filename, duration in SLIDES:
            fh.write(f"file 'frames/{filename}'\n")
            fh.write(f"duration {duration}\n")
        fh.write(f"file 'frames/{SLIDES[-1][0]}'\n")

    cmd = [
        "ffmpeg",
        "-y",
        "-f",
        "concat",
        "-safe",
        "0",
        "-i",
        str(concat),
        "-f",
        "lavfi",
        "-i",
        "anullsrc=channel_layout=stereo:sample_rate=48000",
        "-shortest",
        "-t",
        "120",
        "-r",
        "30",
        "-pix_fmt",
        "yuv420p",
        "-c:v",
        "libx264",
        "-c:a",
        "aac",
        "-movflags",
        "+faststart",
        str(VIDEO_PATH),
    ]
    subprocess.run(cmd, check=True)


def main():
    print(f"Capturing live app frames from {FRONTEND} and {API}")
    capture_frames()
    print("Building 2-minute MP4")
    build_video()
    print(f"Created {VIDEO_PATH}")


if __name__ == "__main__":
    main()
