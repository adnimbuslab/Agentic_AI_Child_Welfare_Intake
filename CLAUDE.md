# Child Welfare Intake System — Project Instructions

## Overview
Agentic AI Child Welfare Intake POC: a chatbot-based intake platform using multi-agent orchestration (LangGraph), Claude Opus 4.7, MCP servers, and LocalStack AWS simulation.

## Key Documents
- `Business_requirement.md` — Business workflow, user personas, intake/risk/quality/bias flows, HITL rules
- `technical_requirement.md` — Technical HLD: architecture, API endpoints, DynamoDB schema, MCP servers, LangGraph flow, agent contracts
- `SPEC.md` — Full detailed specification with requirement traceability (BR/FR/AR/HITL/API/MCP/DB/FE/NFR/WF/DEP/TEST)
- `arc/` — Architecture diagrams and design documents

## Tech Stack
- **Frontend:** React (chatbot + caseworker dashboard)
- **Backend:** Python Lambda functions on LocalStack + Docker (no real AWS)
- **Agent Orchestration:** LangGraph with 5 agents (Intake Understanding, Risk Assessment, Data Quality, Bias Monitoring, Explanation)
- **LLM:** Claude Opus 4.7 — single-point config via `LLM_MODEL_ID` + `LLM_PROVIDER` env vars; ALL agents share this one config
- **Tool Access:** All agents use MCP servers only — no direct backend calls
- **Infrastructure:** LocalStack (Docker) for DynamoDB, S3, Lambda, API Gateway — no real AWS accounts needed

## Architecture Rules
1. Agents must NEVER call DynamoDB, S3, Lambda, or any backend service directly — use MCP server tools only
2. Every agent decision, state transition, and human action must be logged as an immutable AuditEvent
3. Critical and High risk cases must always route through human review before finalization
4. All confidence thresholds are configurable via environment variables
5. LLM provider/model must be swappable via env vars without code changes

## LLM Configuration (Single Point)
All 5 agents read from the same two env vars — change once, applies everywhere:
- `LLM_MODEL_ID=claude-opus-4-7` — the model all agents use
- `LLM_PROVIDER=anthropic` — the provider all agents use
- `ANTHROPIC_API_KEY` — API key (set in `.claude/settings.local.json`, not committed)

Agents obtain their LLM client via a shared factory function. Swapping to a different model requires only changing these env vars — zero code changes.

## Development Workflow
1. Start LocalStack + Docker: `docker-compose up -d`
2. All services (DynamoDB, S3, Lambda, API Gateway) run locally via LocalStack — no AWS account needed
3. Test iteratively on LocalStack before any handoff
4. Test cases are documented in the project README
5. Follow requirement traceability IDs (BR-xxx, FR-xxx, AR-xxx, etc.) from SPEC.md

## Naming Conventions
- Case IDs: `CW-YYYY-NNNN` format
- Agent names: `intake-understanding`, `risk-assessment`, `data-quality`, `bias-monitoring`, `explanation`
- DynamoDB tables: `IntakeCases`, `IntakeMessages`, `IntakeDocuments`, `AgentOutputs`, `AuditEvents`