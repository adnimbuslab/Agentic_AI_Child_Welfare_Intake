# LangGraph Workflow Design

## Workflow Nodes (WF-001 through WF-013)

```
WF-001: start (Session Init)
    │
    ▼
WF-002: intake_understanding (AR-001)
    │
    ▼
WF-003: follow_up_router ◄──────────────────────┐
    │                                             │
    ├── missing fields & !escalate ───────────────┘
    │   (send follow-up Qs, wait for response,    
    │    re-enter WF-002)                         
    │                                             
    ├── escalate=true ──────► WF-012: human_review_queue
    │
    └── no missing fields
         │
         ▼
WF-004: risk_assessment (AR-002)
         │
         ▼
WF-005: risk_gate
         │
         ├── escalate=true ──────► WF-012
         │
         └── continue
              │
              ▼
WF-006: data_quality (AR-003)
              │
              ▼
WF-007: quality_gate
              │
              ├── escalate=true ──────► WF-012
              ├── !readyForReview ────► WF-003 (more follow-up)
              │
              └── continue
                   │
                   ▼
WF-008: bias_monitoring (AR-004)
                   │
                   ▼
WF-009: bias_gate
                   │
                   ├── flagged/review ──► WF-012
                   │
                   └── continue
                        │
                        ▼
WF-010: save_intake (persist final record)
                        │
                        ▼
WF-011: explanation (AR-005, assign final status)
                        │
                        ├── needs review ──► WF-012
                        │
                        └── READY_FOR_CASEWORKER_REVIEW
                             │
                             ▼
WF-013: end
```

## Node Details

### WF-002: intake_understanding
- Calls: MCP-007-T1 (required fields), MCP-001-T2 (case state)
- Runs extraction via AR-001
- Saves: MCP-001-T4 (structured fields), MCP-005-T1 (agent decision)

### WF-004: risk_assessment
- Calls: MCP-007-T3 (policy thresholds), MCP-003-T1 (prior referrals)
- Runs scoring via AR-002
- Saves: MCP-004-T3 (risk output), MCP-005-T1 (agent decision)

### WF-006: data_quality
- Calls: MCP-007-T1 (required fields)
- Runs validation via AR-003
- Saves: MCP-005-T1 (agent decision)

### WF-008: bias_monitoring
- Calls: MCP-007-T4 (bias policy)
- Runs review via AR-004
- Saves: MCP-005-T1 (agent decision)

### WF-011: explanation
- Receives all prior agent outputs
- Assigns final case status (BR-011)
- Calls: MCP-006-T2 (notify caseworker) if READY_FOR_CASEWORKER_REVIEW

### WF-012: human_review_queue
- Calls: MCP-006-T1 (route to queue), MCP-006-T3 (notify supervisor if Critical)
- Calls: MCP-005-T3 (log escalation)
- Pauses workflow until human action via API-006
