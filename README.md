# Agentic AI Child Welfare Intake

Proof-of-concept chatbot and caseworker dashboard for child welfare intake using multi-agent AI orchestration, FastAPI, React, LocalStack, DynamoDB, S3-compatible storage, and Ollama.

## Demo Video

- Ameddin E: [demo_10_min_walkthrough.mp4](https://github.com/adnimbuslab/Agentic_AI_Child_Welfare_Intake/blob/main/demo_10_min_walkthrough.mp4)

## Run Locally

```bash
docker-compose up -d
source .venv/bin/activate
python run.py
```

In another terminal:

```bash
cd frontend
npm run dev
```

Open the app at `http://localhost:3000`.

## Demo Script

Run the automated demo:

```bash
source .venv/bin/activate
python demo_script.py --auto
```

The script covers:

1. High-risk neglect report with four document uploads.
2. Emergency immediate-danger report.
3. Lower-risk behavioral concern.
4. Duplicate detection scenario.
5. Human supervisor review workflow.

## Key Screens

- New intake chatbot
- Document upload
- Caseworker dashboard
- Case detail with fields, documents, messages, agents, and audit trail
- Human review queue
