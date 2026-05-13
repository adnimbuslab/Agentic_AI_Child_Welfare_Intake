# Agent Input/Output Contracts

## AR-001: Intake Understanding Agent

**Input:**
```json
{
  "sessionMessages": [{ "role": "user|assistant", "content": "string" }],
  "extractedDocumentTexts": ["string"],
  "currentStructuredFields": {}
}
```

**Output:**
```json
{
  "structuredFields": {
    "childName": { "value": "string|null", "confidence": 0.0 },
    "childDob": { "value": "string|null", "confidence": 0.0 },
    "childAge": { "value": "number|null", "confidence": 0.0 },
    "guardianInfo": { "value": "string|null", "confidence": 0.0 },
    "reporterInfo": { "value": "string|null", "confidence": 0.0 },
    "reporterRelationship": { "value": "string|null", "confidence": 0.0 },
    "contactDetails": { "value": "string|null", "confidence": 0.0 },
    "address": { "value": "string|null", "confidence": 0.0 },
    "concernType": { "value": "string|null", "confidence": 0.0 },
    "incidentDescription": { "value": "string|null", "confidence": 0.0 },
    "urgencyIndicators": { "value": ["string"], "confidence": 0.0 },
    "priorConcerns": { "value": "string|null", "confidence": 0.0 }
  },
  "missingRequiredFields": ["string"],
  "followUpQuestions": ["string"],
  "overallConfidenceScore": 0.0,
  "escalate": false,
  "escalationReason": "string|null"
}
```

**Escalation Triggers:** overallConfidence < 0.3, doc extraction < 0.4, unreadable docs, conflicting critical info, urgent danger + missing identity/location.

---

## AR-002: Risk Assessment Agent

**Input:**
```json
{
  "structuredFields": {},
  "dataQualityScore": 0.0,
  "documentSummaries": ["string"]
}
```

**Output:**
```json
{
  "riskLevel": "Low|Medium|High|Critical",
  "confidenceScore": 0.0,
  "urgency": "string",
  "riskFactors": ["string"],
  "escalate": false,
  "escalationReason": "string|null"
}
```

**Escalation Triggers:** confidence < 0.6, Critical risk (always), High risk + quality < 0.5, immediate safety + poor data.

---

## AR-003: Data Quality Agent

**Input:**
```json
{
  "structuredFields": {},
  "intakeMessages": [],
  "documentExtractionResults": []
}
```

**Output:**
```json
{
  "dataQualityScore": 0.0,
  "missingCriticalFields": ["string"],
  "inconsistencies": [{ "field": "string", "detail": "string" }],
  "readyForReview": true,
  "escalate": false,
  "escalationReason": "string|null"
}
```

**Escalation Triggers:** critical field missing after follow-up, quality < 0.5 after follow-up, doc/user contradiction, identity unverifiable.

---

## AR-004: Bias Monitoring Agent

**Input:**
```json
{
  "riskAssessmentOutput": {},
  "structuredFields": {},
  "biasPolicy": "string"
}
```

**Output:**
```json
{
  "biasStatus": "Passed|Flagged",
  "biasConfidence": 0.0,
  "flags": [{ "type": "string", "detail": "string" }],
  "humanReviewRequired": false,
  "escalationReason": "string|null"
}
```

**Escalation Triggers:** biasStatus == "Flagged" (always), biasConfidence < 0.7, sensitive attribute in primary risk factors.

---

## AR-005: Explanation Agent

**Input:**
```json
{
  "intakeUnderstandingOutput": {},
  "riskAssessmentOutput": {},
  "dataQualityOutput": {},
  "biasMonitoringOutput": {},
  "caseId": "string"
}
```

**Output:**
```json
{
  "caseworkerSummary": "string",
  "riskExplanation": ["string"],
  "recommendation": "string",
  "limitations": ["string"],
  "nextAction": "string",
  "humanReviewRequired": false,
  "humanReviewReason": "string|null",
  "finalCaseStatus": "READY_FOR_CASEWORKER_REVIEW|NEEDS_MORE_INFORMATION|ESCALATED_TO_SUPERVISOR|CRITICAL_IMMEDIATE_REVIEW|BIAS_REVIEW_REQUIRED|LOW_CONFIDENCE_REVIEW_REQUIRED"
}
```
