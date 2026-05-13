# DynamoDB Schema — LocalStack

## DB-001: IntakeCases
**Key:** PK = `caseId` (String)

| Attribute | Type | Required |
|-----------|------|----------|
| caseId | String | Yes |
| status | String | Yes |
| riskLevel | String | No |
| riskConfidence | Number | No |
| urgency | String | No |
| dataQualityScore | Number | No |
| biasStatus | String | No |
| humanReviewRequired | Boolean | No |
| humanReviewReason | String | No |
| structuredFields | Map | No |
| missingFieldHistory | List | No |
| reporterType | String | No |
| createdAt | String (ISO 8601) | Yes |
| updatedAt | String (ISO 8601) | Yes |

## DB-002: IntakeMessages
**Key:** PK = `caseId` (String), SK = `messageTimestamp` (String, ISO 8601)

| Attribute | Type | Required |
|-----------|------|----------|
| caseId | String | Yes |
| messageTimestamp | String | Yes |
| senderType | String | Yes |
| messageText | String | Yes |
| messageType | String | Yes |
| attachments | List | No |
| agentGenerated | Boolean | Yes |
| createdAt | String (ISO 8601) | Yes |

## DB-003: IntakeDocuments
**Key:** PK = `caseId` (String), SK = `documentId` (String)

| Attribute | Type | Required |
|-----------|------|----------|
| caseId | String | Yes |
| documentId | String (UUID) | Yes |
| fileName | String | Yes |
| fileType | String (MIME) | Yes |
| storagePath | String (S3 key) | Yes |
| extractedText | String | No |
| extractionConfidence | Number | No |
| documentCategory | String | No |
| createdAt | String (ISO 8601) | Yes |

## DB-004: AgentOutputs
**Key:** PK = `caseId` (String), SK = `agentName#timestamp` (String)

| Attribute | Type | Required |
|-----------|------|----------|
| caseId | String | Yes |
| agentName | String | Yes |
| inputSummary | String | No |
| outputJson | Map | Yes |
| confidenceScore | Number | No |
| status | String | Yes |
| escalationReason | String | No |
| createdAt | String (ISO 8601) | Yes |

## DB-005: AuditEvents
**Key:** PK = `caseId` (String), SK = `eventTimestamp` (String, ISO 8601 + UUID suffix)

| Attribute | Type | Required |
|-----------|------|----------|
| caseId | String | Yes |
| eventTimestamp | String | Yes |
| eventType | String | Yes |
| actor | String | Yes |
| agentName | String | No |
| action | String | Yes |
| reason | String | No |
| beforeState | Map | No |
| afterState | Map | No |
| createdAt | String (ISO 8601) | Yes |

**Immutability Rule (NFR-003):** AuditEvents records must never be updated or deleted. Corrections are new events referencing the original.
