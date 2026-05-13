# MCP Server Design

All agents access backend resources exclusively through MCP server tools. Seven MCP servers provide controlled tool boundaries.

## MCP-001: Intake MCP Server
| Tool | Description |
|------|-------------|
| `create_intake_case` | Create new case in IntakeCases |
| `get_intake_case` | Retrieve full case record by caseId |
| `update_intake_case` | Update case status, risk, or quality fields |
| `save_structured_intake` | Write extracted structured fields |
| `save_intake_message` | Append message to IntakeMessages |

## MCP-002: Contacts MCP Server
| Tool | Description |
|------|-------------|
| `lookup_child_contact` | Look up child by name/DOB |
| `lookup_guardian_contact` | Look up guardian by name/address |
| `lookup_reporter_contact` | Look up reporter by ID/name |
| `validate_contact_information` | Validate contact record completeness |

## MCP-003: Case History MCP Server
| Tool | Description |
|------|-------------|
| `get_prior_referrals` | Prior referral records for a child |
| `get_case_history` | Full prior case history |
| `get_household_history` | Household instability history |

## MCP-004: Risk Assessment MCP Server
| Tool | Description |
|------|-------------|
| `calculate_risk_score` | Invoke risk scoring with structured fields |
| `get_risk_thresholds` | Configured risk threshold values |
| `save_risk_assessment` | Persist risk output to AgentOutputs |

## MCP-005: Audit & Governance MCP Server
| Tool | Description |
|------|-------------|
| `save_agent_decision` | Write agent output to AgentOutputs |
| `save_confidence_score` | Record field-level confidence in AuditEvents |
| `save_escalation_reason` | Record escalation details in AuditEvents |
| `save_human_override` | Record human override in AuditEvents |
| `get_audit_timeline` | Retrieve ordered audit events for a case |

## MCP-006: Notification / Escalation MCP Server
| Tool | Description |
|------|-------------|
| `route_to_human_review` | Place case in human review queue |
| `notify_caseworker` | Notify assigned caseworker |
| `notify_supervisor` | Notify supervisor for critical/bias cases |
| `create_review_task` | Create task in review queue |

## MCP-007: Knowledge / Policy MCP Server
| Tool | Description |
|------|-------------|
| `get_intake_required_fields` | Mandatory intake field list |
| `get_mandatory_reporting_rules` | Reporting compliance rules |
| `get_risk_policy_guidelines` | Risk assessment policy thresholds |
| `get_bias_monitoring_policy` | Bias detection rules and sensitive attributes |
| `get_human_review_policy` | Conditions triggering human review |
