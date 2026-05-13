# Code Review Skill — Child Welfare Intake System

## When to Use
Invoke this skill when reviewing PRs or code changes in the Child Welfare Intake project.

## Review Checklist

### Architecture Compliance
- Agents must NOT call DynamoDB, S3, Lambda, or any backend service directly
- All agent resource access goes through MCP server tools only (NFR-007)
- LLM client obtained via shared factory reading `LLM_MODEL_ID` / `LLM_PROVIDER` env vars (AR-006)
- No hardcoded AWS endpoints — all must use `AWS_ENDPOINT_URL` (NFR-005)

### Agent Contract Validation
- Verify agent input/output matches the contracts defined in SPEC.md (AR-001 through AR-005)
- Every extracted field must carry a confidence score between 0 and 1
- Escalation triggers must match the spec (e.g., Critical risk always escalates)
- Confidence thresholds must be read from config, not hardcoded

### Human-in-the-Loop Gates
- Confirm HITL gates exist at: post-intake, post-risk, post-quality, post-bias, final-gate
- High/Critical risk cases must NEVER be auto-finalized without human review (HITL-007)
- Audit trail must be saved BEFORE escalation occurs (BR-012)

### Audit Trail
- Every agent decision, state transition, and human action logged as immutable AuditEvent (FR-011)
- Every LangGraph node transition logged (NFR-006)
- AuditEvents records must never be updated or deleted (NFR-003)

### Data Safety
- Input validation at API boundaries (no XSS, injection)
- Case IDs follow `CW-YYYY-NNNN` format
- File uploads reject unsupported types (.exe, etc.)
- Empty/whitespace-only messages rejected with HTTP 400

### DynamoDB Schema
- Table names and key structures match DB-001 through DB-005
- Sort keys use ISO 8601 format where specified
- All required attributes are populated

## Output Format
Produce findings grouped by: Critical (blocks merge), Warning (should fix), Info (suggestion).
