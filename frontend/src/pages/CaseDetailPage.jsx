import React, { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import { getCaseSummary } from '../api/client';

const riskColors = { Low: '#00b894', Medium: '#fdcb6e', High: '#e17055', Critical: '#d63031' };

export default function CaseDetailPage() {
  const { caseId } = useParams();
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState('summary');

  useEffect(() => {
    getCaseSummary(caseId)
      .then(res => setData(res.data))
      .catch(() => setData(null))
      .finally(() => setLoading(false));
  }, [caseId]);

  if (loading) return <p>Loading case...</p>;
  if (!data) return <p>Case not found. <Link to="/dashboard">Back to dashboard</Link></p>;

  const { case: caseData, agentOutputs, auditEvents, documents, messages } = data;
  const fields = caseData.structuredFields || {};
  const explanationAgent = agentOutputs?.find(a => a.agentName === 'explanation');
  const explanation = explanationAgent?.outputJson || {};

  return (
    <div>
      <Link to="/dashboard" style={{ fontSize: '13px' }}>Back to Dashboard</Link>
      <div style={headerCard}>
        <h2>{caseId}</h2>
        <div style={badgeRow}>
          <span style={statusPill}>{caseData.status?.replace(/_/g, ' ')}</span>
          <span style={{ ...riskPill, background: riskColors[caseData.riskLevel] || '#b2bec3' }}>{caseData.riskLevel || 'N/A'}</span>
          {caseData.urgency && <span style={infoPill}>{caseData.urgency}</span>}
          {caseData.dataQualityScore && <span style={infoPill}>Quality: {Math.round(parseFloat(caseData.dataQualityScore) * 100)}%</span>}
          {caseData.biasStatus && <span style={infoPill}>Bias: {caseData.biasStatus}</span>}
          {caseData.humanReviewRequired && <span style={{ ...infoPill, background: '#d63031', color: '#fff' }}>Human Review Required</span>}
        </div>
      </div>

      <div style={tabBar}>
        {['summary', 'fields', 'documents', 'messages', 'agents', 'audit'].map(tab => (
          <button key={tab} onClick={() => setActiveTab(tab)} style={activeTab === tab ? tabActive : tabBtn}>
            {tab.charAt(0).toUpperCase() + tab.slice(1)}
          </button>
        ))}
      </div>

      <div style={contentCard}>
        {activeTab === 'summary' && (
          <div>
            {explanation.caseworkerSummary && <p style={{ marginBottom: '12px' }}>{explanation.caseworkerSummary}</p>}
            {explanation.riskExplanation && (
              <div><strong>Risk Factors:</strong><ul>{explanation.riskExplanation.map((r, i) => <li key={i}>{r}</li>)}</ul></div>
            )}
            {explanation.recommendation && <p><strong>Recommendation:</strong> {explanation.recommendation}</p>}
            {explanation.limitations?.length > 0 && (
              <div style={{ marginTop: '8px' }}><strong>Limitations:</strong><ul>{explanation.limitations.map((l, i) => <li key={i}>{l}</li>)}</ul></div>
            )}
            {explanation.nextAction && <p style={{ marginTop: '8px' }}><strong>Next Action:</strong> {explanation.nextAction}</p>}
          </div>
        )}

        {activeTab === 'fields' && (
          <table style={tableStyle}>
            <thead><tr><th style={th}>Field</th><th style={th}>Value</th><th style={th}>Confidence</th></tr></thead>
            <tbody>
              {Object.entries(fields).map(([key, val]) => (
                <tr key={key}>
                  <td style={td}>{key}</td>
                  <td style={td}>{typeof val === 'object' ? (val?.value != null ? String(Array.isArray(val.value) ? val.value.join(', ') : val.value) : '—') : String(val)}</td>
                  <td style={td}>{typeof val === 'object' && val?.confidence != null ? `${Math.round(val.confidence * 100)}%` : '—'}</td>
                </tr>
              ))}
            </tbody>
          </table>
        )}

        {activeTab === 'documents' && (
          <table style={tableStyle}>
            <thead><tr><th style={th}>File</th><th style={th}>Type</th><th style={th}>Category</th><th style={th}>Extraction</th><th style={th}>Confidence</th></tr></thead>
            <tbody>
              {(documents || []).map((d, i) => (
                <tr key={i}>
                  <td style={td}>{d.fileName}</td>
                  <td style={td}>{d.fileType}</td>
                  <td style={td}>{d.documentCategory || '—'}</td>
                  <td style={td}>{d.extractionStatus || '—'}</td>
                  <td style={td}>{d.extractionConfidence ? `${Math.round(parseFloat(d.extractionConfidence) * 100)}%` : '—'}</td>
                </tr>
              ))}
              {(!documents || documents.length === 0) && <tr><td colSpan={5} style={td}>No documents</td></tr>}
            </tbody>
          </table>
        )}

        {activeTab === 'messages' && (
          <div>
            {(messages || []).map((m, i) => (
              <div key={i} style={{ ...msgRow, background: m.senderType === 'user' ? '#e8f4fd' : '#fff' }}>
                <strong style={{ fontSize: '11px' }}>{m.senderType} — {m.messageType}</strong>
                <p style={{ whiteSpace: 'pre-wrap', marginTop: '4px' }}>{m.messageText}</p>
              </div>
            ))}
          </div>
        )}

        {activeTab === 'agents' && (
          <div>
            {(agentOutputs || []).map((a, i) => (
              <div key={i} style={agentCard}>
                <strong>{a.agentName}</strong>
                <span style={{ fontSize: '12px', color: '#636e72', marginLeft: '8px' }}>
                  {a.status} {a.confidenceScore ? `(${Math.round(parseFloat(a.confidenceScore) * 100)}%)` : ''}
                </span>
                {a.escalationReason && <div style={{ color: '#d63031', fontSize: '13px', marginTop: '4px' }}>Escalation: {a.escalationReason}</div>}
                <pre style={preStyle}>{JSON.stringify(a.outputJson, null, 2)}</pre>
              </div>
            ))}
          </div>
        )}

        {activeTab === 'audit' && (
          <div>
            {(auditEvents || []).map((e, i) => (
              <div key={i} style={auditRow}>
                <div style={auditTime}>{e.createdAt?.slice(0, 19)}</div>
                <div>
                  <strong>{e.eventType}</strong> by <em>{e.actor}</em>
                  {e.action && <span> — {e.action}</span>}
                  {e.reason && <div style={{ fontSize: '12px', color: '#636e72' }}>{e.reason}</div>}
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

const headerCard = { background: '#fff', padding: '20px', borderRadius: '8px', marginTop: '12px', boxShadow: '0 1px 3px rgba(0,0,0,0.1)' };
const badgeRow = { display: 'flex', gap: '8px', marginTop: '10px', flexWrap: 'wrap' };
const statusPill = { fontSize: '12px', padding: '4px 10px', borderRadius: '10px', background: '#f0f0f0', fontWeight: 600 };
const riskPill = { fontSize: '12px', padding: '4px 10px', borderRadius: '10px', color: '#fff', fontWeight: 600 };
const infoPill = { fontSize: '12px', padding: '4px 10px', borderRadius: '10px', background: '#dfe6e9' };
const tabBar = { display: 'flex', gap: '4px', marginTop: '16px' };
const tabBtn = { padding: '8px 16px', border: '1px solid #dfe6e9', borderBottom: 'none', borderRadius: '6px 6px 0 0', background: '#f5f6fa', cursor: 'pointer', fontSize: '13px' };
const tabActive = { ...tabBtn, background: '#fff', fontWeight: 600, borderBottomColor: '#fff' };
const contentCard = { background: '#fff', padding: '20px', borderRadius: '0 0 8px 8px', boxShadow: '0 1px 3px rgba(0,0,0,0.1)', minHeight: '200px' };
const tableStyle = { width: '100%', borderCollapse: 'collapse' };
const th = { padding: '8px 10px', textAlign: 'left', background: '#f0f0f0', fontSize: '12px', fontWeight: 700 };
const td = { padding: '8px 10px', borderBottom: '1px solid #f0f0f0', fontSize: '13px' };
const msgRow = { padding: '10px', borderRadius: '6px', marginBottom: '8px', border: '1px solid #f0f0f0' };
const agentCard = { padding: '12px', marginBottom: '10px', border: '1px solid #f0f0f0', borderRadius: '6px' };
const preStyle = { background: '#f5f6fa', padding: '10px', borderRadius: '4px', fontSize: '12px', overflow: 'auto', maxHeight: '200px', marginTop: '8px' };
const auditRow = { display: 'flex', gap: '12px', padding: '8px 0', borderBottom: '1px solid #f0f0f0', fontSize: '13px' };
const auditTime = { minWidth: '140px', fontFamily: 'monospace', fontSize: '12px', color: '#636e72' };
