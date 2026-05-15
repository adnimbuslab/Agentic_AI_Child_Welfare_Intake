"""View all data in DynamoDB tables on LocalStack — summary view."""
import json
from decimal import Decimal
from backend.db import get_dynamodb_resource

def decimal_default(obj):
    if isinstance(obj, Decimal):
        if obj == int(obj):
            return int(obj)
        return float(obj)
    raise TypeError

def scan_table(table_name):
    table = get_dynamodb_resource().Table(table_name)
    items = []
    resp = table.scan()
    items.extend(resp.get("Items", []))
    while "LastEvaluatedKey" in resp:
        resp = table.scan(ExclusiveStartKey=resp["LastEvaluatedKey"])
        items.extend(resp.get("Items", []))
    return items

# ============================================================
# TABLE 1: IntakeCases
# ============================================================
print("=" * 90)
print("TABLE 1: IntakeCases")
print("=" * 90)
cases = scan_table("IntakeCases")
print(f"Total records: {len(cases)}\n")

for case in sorted(cases, key=lambda x: x.get("createdAt", "")):
    cid = case.get("caseId")
    status = case.get("status", "?")
    risk = case.get("riskLevel", "-")
    risk_conf = case.get("riskConfidence", "-")
    dq = case.get("dataQualityScore", "-")
    bias = case.get("biasStatus", "-")
    hr = case.get("humanReviewRequired", False)
    hr_reason = case.get("humanReviewReason", "-")
    reporter = case.get("reporterType", "?")
    created = case.get("createdAt", "?")[:19]

    sf = case.get("structuredFields", {})
    child_name = "-"
    if sf:
        cn = sf.get("childName", {})
        child_name = cn.get("value", "-") if isinstance(cn, dict) else str(cn or "-")

    print(f"  Case: {cid}  |  Created: {created}")
    print(f"    Status:         {status}")
    print(f"    Reporter:       {reporter}")
    print(f"    Child Name:     {child_name}")
    print(f"    Risk Level:     {risk}  (confidence: {risk_conf})")
    print(f"    Data Quality:   {dq}")
    print(f"    Bias Status:    {bias}")
    print(f"    Human Review:   {hr}  — {hr_reason}")
    print()

# ============================================================
# TABLE 2: IntakeMessages
# ============================================================
print("=" * 90)
print("TABLE 2: IntakeMessages")
print("=" * 90)
messages = scan_table("IntakeMessages")
print(f"Total records: {len(messages)}\n")

by_case = {}
for m in messages:
    cid = m.get("caseId")
    by_case.setdefault(cid, []).append(m)

for cid in sorted(by_case.keys()):
    msgs = sorted(by_case[cid], key=lambda x: x.get("messageTimestamp", ""))
    print(f"  Case: {cid}  ({len(msgs)} messages)")
    for m in msgs:
        sender = m.get("senderType", "?")
        mtype = m.get("messageType", "?")
        text = m.get("messageText", "")
        preview = text[:120] + "..." if len(text) > 120 else text
        print(f"    [{sender}/{mtype}] {preview}")
    print()

# ============================================================
# TABLE 3: IntakeDocuments
# ============================================================
print("=" * 90)
print("TABLE 3: IntakeDocuments")
print("=" * 90)
docs = scan_table("IntakeDocuments")
print(f"Total records: {len(docs)}\n")
if docs:
    for d in docs:
        print(f"  {d.get('caseId')} / {d.get('fileName')} — {d.get('extractionStatus')}")
else:
    print("  (no documents uploaded in test runs)")
print()

# ============================================================
# TABLE 4: AgentOutputs
# ============================================================
print("=" * 90)
print("TABLE 4: AgentOutputs")
print("=" * 90)
agent_outputs = scan_table("AgentOutputs")
print(f"Total records: {len(agent_outputs)}\n")

ao_by_case = {}
for ao in agent_outputs:
    cid = ao.get("caseId")
    ao_by_case.setdefault(cid, []).append(ao)

for cid in sorted(ao_by_case.keys()):
    outputs = sorted(ao_by_case[cid], key=lambda x: x.get("agentNameTimestamp", ""))
    print(f"  Case: {cid}  ({len(outputs)} agent outputs)")
    for ao in outputs:
        agent = ao.get("agentName", "?")
        status_val = ao.get("status", "?")
        conf = ao.get("confidenceScore", "-")
        esc = ao.get("escalationReason")
        print(f"    Agent: {agent:25s}  Status: {status_val:10s}  Confidence: {conf}")
        if esc:
            print(f"      Escalation: {esc}")

        out = ao.get("outputJson", {})
        if agent == "intake-understanding" and isinstance(out, dict):
            sf = out.get("structuredFields", {})
            if sf:
                fields_summary = []
                for k, v in sf.items():
                    val = v.get("value") if isinstance(v, dict) else v
                    if val is not None and val != [] and val != "":
                        fields_summary.append(k)
                print(f"      Fields extracted: {', '.join(fields_summary)}")
                print(f"      Overall confidence: {out.get('overallConfidenceScore', '?')}")
        elif agent == "risk-assessment" and isinstance(out, dict):
            print(f"      Risk: {out.get('riskLevel', '?')} | Urgency: {str(out.get('urgency', '?'))[:80]}")
            factors = out.get("riskFactors", [])
            if factors:
                print(f"      Factors: {'; '.join(str(f)[:60] for f in factors[:3])}")
        elif agent == "system" and isinstance(out, dict):
            print(f"      Action: {out.get('action', '?')}")
    print()

# ============================================================
# TABLE 5: AuditEvents
# ============================================================
print("=" * 90)
print("TABLE 5: AuditEvents")
print("=" * 90)
events = scan_table("AuditEvents")
print(f"Total records: {len(events)}\n")

ev_by_case = {}
for ev in events:
    cid = ev.get("caseId")
    ev_by_case.setdefault(cid, []).append(ev)

for cid in sorted(ev_by_case.keys()):
    evts = sorted(ev_by_case[cid], key=lambda x: x.get("eventTimestamp", ""))
    print(f"  Case: {cid}  ({len(evts)} audit events)")
    for ev in evts:
        etype = ev.get("eventType", "?")
        actor = ev.get("actor", "?")
        action = ev.get("action", "?")
        reason = ev.get("reason")
        ts = ev.get("eventTimestamp", "")[:19]
        line = f"    [{ts}] {etype:20s} | {actor:25s} | {action}"
        print(line)
        if reason:
            print(f"      Reason: {reason[:100]}")
    print()
