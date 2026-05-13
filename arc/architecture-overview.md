# Architecture Overview — Child Welfare Intake System

## System Architecture

```
Reporter (Browser)
       │
       ▼
┌──────────────────┐
│  React Chat UI   │  FE-001, FE-002, FE-003
│  React Dashboard │  FE-004, FE-005, FE-006, FE-007
└────────┬─────────┘
         │ HTTP
         ▼
┌──────────────────┐
│  API Gateway     │  LocalStack
│  (LocalStack)    │
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│  Lambda Functions│  API-001 through API-007
│  (LocalStack)    │
└────────┬─────────┘
         │
    ┌────┴─────┐
    ▼          ▼
┌────────┐ ┌──────────────────────────┐
│DynamoDB│ │  LangGraph Workflow      │
│  (5    │ │  ┌────────────────────┐  │
│tables) │ │  │Intake Understanding│  │
│        │ │  │Risk Assessment     │  │
│        │ │  │Data Quality        │  │
│        │ │  │Bias Monitoring     │  │
│        │ │  │Explanation         │  │
│        │ │  └────────┬───────────┘  │
│        │ │           │              │
│        │ │    MCP Servers (7)       │
│        │ │    ┌──────┴───────┐      │
│        │ │    │Intake  │Audit│      │
│        │ │    │Contact │Notif│      │
│        │ │    │History │Know.│      │
│        │ │    │Risk    │     │      │
│        │ │    └──────────────┘      │
│        │ └──────────────────────────┘
└────────┘
    │
    ▼
┌────────┐
│   S3   │  Document storage (LocalStack)
└────────┘
```

## Data Flow

1. Reporter submits narrative/documents via React chatbot
2. API Gateway routes to Lambda handler
3. Lambda triggers LangGraph workflow
4. Agents process sequentially: Intake → Risk → Quality → Bias → Explanation
5. Each agent accesses backend resources ONLY through MCP server tools
6. HITL gates check escalation conditions after each agent
7. Final output routed to caseworker dashboard or human review queue
8. All decisions logged as immutable AuditEvents

## LLM Configuration (Single Point for All Agents)

All 5 agents share one LLM configuration — no per-agent model settings:

```
LLM_MODEL_ID=claude-opus-4-7    # One model for all agents
LLM_PROVIDER=anthropic           # One provider for all agents
ANTHROPIC_API_KEY=<your-key>     # One API key
```

Agents obtain their client via a shared `create_llm_client()` factory that reads these env vars. To swap models, change the env vars — zero code changes required.

## Infrastructure: LocalStack + Docker (No Real AWS)

All AWS-equivalent services run locally via LocalStack in Docker:
- **DynamoDB** → `http://localhost:4566`
- **S3** → `http://localhost:4566`
- **Lambda** → `http://localhost:4566`
- **API Gateway** → `http://localhost:4566`

No AWS account, credentials, or cloud resources are needed. Start everything with `docker-compose up -d`.

## Key Architecture Decisions

| Decision | Rationale | Requirement |
|----------|-----------|-------------|
| MCP-only agent access | Controlled tool boundaries prevent agents from bypassing validation | NFR-007 |
| Single-point LLM config | All 5 agents read `LLM_MODEL_ID` + `LLM_PROVIDER` from env — one change applies everywhere | AR-006, NFR-002 |
| LocalStack + Docker only | Full local dev/test, no AWS account needed | NFR-005, DEP-001 |
| Immutable audit log | Regulatory compliance, full decision traceability | NFR-003, BR-012 |
| Multi-point HITL gates | AI must not independently finalize high-stakes cases | HITL-007 |
