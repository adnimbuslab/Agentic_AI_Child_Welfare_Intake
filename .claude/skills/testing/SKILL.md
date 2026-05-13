# Testing Skill — Child Welfare Intake System

## When to Use
Invoke this skill when writing, running, or validating tests for the Child Welfare Intake project.

## Test Categories (from SPEC.md §14)

### Category A — Session & API Layer
- TEST-001: Session creation happy path (CW-YYYY-NNNN format, IN_PROGRESS status)
- TEST-016: Missing reporterType returns HTTP 400
- TEST-017: Malformed JSON returns HTTP 400
- TEST-018: Case ID uniqueness across sessions
- TEST-019: Message to non-existent case returns HTTP 404
- TEST-020: Message to completed case returns HTTP 409

### Category B — Intake Message Submission
- TEST-002: Structured field extraction from narrative
- TEST-003: Follow-up question generation for missing fields
- TEST-021: Empty message text returns HTTP 400
- TEST-022: Extremely long message (>10K chars) processes without crash
- TEST-023: XSS payload stored as literal text, not executable
- TEST-024: Non-English narrative does not crash system
- TEST-025: Whitespace-only message returns HTTP 400

### Category C — Document Upload
- TEST-004: File upload happy path (S3 + IntakeDocuments record)
- TEST-026: Upload to non-existent case returns HTTP 404
- TEST-027: Unsupported file type (.exe) returns HTTP 400
- TEST-028: Zero-byte file returns HTTP 400 or extraction failed
- TEST-029: Corrupted PDF returns extractionStatus=failed gracefully
- TEST-030: Image with no text returns low/zero extractionConfidence
- TEST-031: Upload after final status returns HTTP 409

### Category D — Intake Understanding Agent
- TEST-032: Conflicting info triggers escalation
- TEST-033: All fields present skips follow-up loop
- TEST-034: Anonymous reporter does not block progress
- TEST-035: Multiple children mentioned handled gracefully
- TEST-036: "I don't know" answer does not cause infinite loop
- TEST-037: Max follow-up rounds exceeded triggers escalation

## Test Execution
```bash
# Run all tests against LocalStack
python -m pytest tests/ -v --tb=short

# Run by category
python -m pytest tests/ -k "category_a" -v
python -m pytest tests/ -k "category_b" -v
python -m pytest tests/ -k "category_c" -v
python -m pytest tests/ -k "category_d" -v
```

## Test Writing Rules
1. Each test must reference its TEST-xxx ID and traced requirement IDs in the docstring
2. Tests must run against LocalStack (use `AWS_ENDPOINT_URL` env var)
3. Assert specific HTTP status codes, DynamoDB record states, and agent output shapes
4. Never mock DynamoDB — use LocalStack for integration tests
5. Clean up test data after each test run (use fixtures with teardown)
