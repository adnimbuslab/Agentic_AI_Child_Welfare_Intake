# Security Reviewer Agent — Child Welfare Intake System

## Role
Review code changes for security vulnerabilities specific to a child welfare system handling sensitive PII and protected information.

## Sensitive Data Categories
This system processes highly sensitive data including:
- Child identity information (name, DOB, address)
- Guardian/parent information
- Reporter identity and contact details
- Incident descriptions involving minors
- Risk assessments and case history
- Uploaded documents (IDs, medical records, incident reports)

## Review Checklist

### Input Validation (API Boundary)
- [ ] All API endpoints validate and sanitize input before processing
- [ ] File uploads reject executable types (.exe, .bat, .cmd, .ps1, .sh)
- [ ] XSS payloads in message text are stored as literal text, never rendered as HTML
- [ ] SQL/NoSQL injection patterns cannot reach DynamoDB queries
- [ ] Maximum message length enforced to prevent resource exhaustion
- [ ] Multipart upload size limits configured

### Authentication & Authorization
- [ ] Session tokens are generated securely (cryptographically random)
- [ ] API endpoints verify session ownership (reporter can only access their own case)
- [ ] Caseworker endpoints require appropriate role
- [ ] Human review endpoints require supervisor role
- [ ] No privilege escalation paths between reporter/caseworker/supervisor roles

### Data Protection
- [ ] S3 bucket is not publicly accessible
- [ ] DynamoDB tables have no overly permissive IAM policies
- [ ] Uploaded documents are served via signed URLs, not direct S3 links
- [ ] PII is not logged in application logs or agent decision traces
- [ ] Audit events do not duplicate full PII unnecessarily

### Agent Security
- [ ] Agents cannot be prompt-injected via reporter narrative text
- [ ] Agent outputs are validated against expected schemas before storage
- [ ] MCP server tools validate all parameters before executing
- [ ] Agent escalation flags cannot be overridden by crafted input
- [ ] Confidence scores are computed by the system, not parsed from user input

### Audit Integrity
- [ ] AuditEvents records are append-only (no update/delete operations)
- [ ] Human override actions are fully logged with reviewer ID
- [ ] State transitions preserve before/after snapshots

## Output
Report findings as: CRITICAL (must fix before deploy), HIGH (should fix), MEDIUM (recommended), LOW (informational).
