import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { listCases, submitHumanReview } from '../api/client';

export default function HumanReviewPage() {
  const [cases, setCases] = useState([]);
  const [loading, setLoading] = useState(true);
  const [reviewModal, setReviewModal] = useState(null);
  const [reviewAction, setReviewAction] = useState('approve');
  const [overrideRisk, setOverrideRisk] = useState('');
  const [notes, setNotes] = useState('');
  const [submitting, setSubmitting] = useState(false);

  useEffect(() => { fetchEscalated(); }, []);

  async function fetchEscalated() {
    setLoading(true);
    try {
      const res = await listCases({ pageSize: 100 });
      const escalated = (res.data.cases || []).filter(c => c.humanReviewRequired);
      setCases(escalated);
    } catch {
      setCases([]);
    }
    setLoading(false);
  }

  async function handleSubmitReview() {
    if (!reviewModal) return;
    setSubmitting(true);
    try {
      await submitHumanReview(reviewModal.caseId, {
        reviewerId: 'supervisor-001',
        action: reviewAction,
        overrideRiskLevel: reviewAction === 'override' ? overrideRisk : null,
        notes: notes || null,
      });
      setReviewModal(null);
      setNotes('');
      setReviewAction('approve');
      setOverrideRisk('');
      fetchEscalated();
    } catch (err) {
      alert('Review submission failed: ' + (err.response?.data?.detail || 'Unknown error'));
    }
    setSubmitting(false);
  }

  return (
    <div>
      <h2 style={{ marginBottom: '16px' }}>Human Review Queue</h2>

      {loading ? <p>Loading...</p> : cases.length === 0 ? (
        <div style={emptyState}>
          <p>No cases pending human review.</p>
        </div>
      ) : (
        <table style={tableStyle}>
          <thead>
            <tr>
              <th style={th}>Case ID</th>
              <th style={th}>Status</th>
              <th style={th}>Risk</th>
              <th style={th}>Escalation Reason</th>
              <th style={th}>Created</th>
              <th style={th}>Action</th>
            </tr>
          </thead>
          <tbody>
            {cases.map(c => (
              <tr key={c.caseId}>
                <td style={td}><Link to={`/cases/${c.caseId}`}>{c.caseId}</Link></td>
                <td style={td}>{c.status?.replace(/_/g, ' ')}</td>
                <td style={td}>{c.riskLevel || '—'}</td>
                <td style={td}>{c.humanReviewReason || '—'}</td>
                <td style={td}>{c.createdAt?.slice(0, 16)}</td>
                <td style={td}>
                  <button onClick={() => setReviewModal(c)} style={actionBtn}>Review</button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      )}

      {reviewModal && (
        <div style={overlay}>
          <div style={modal}>
            <h3>Review Case: {reviewModal.caseId}</h3>
            <div style={{ marginTop: '12px' }}>
              <label style={labelStyle}>Action:</label>
              <select value={reviewAction} onChange={e => setReviewAction(e.target.value)} style={selectStyle}>
                <option value="approve">Approve</option>
                <option value="override">Override Risk Level</option>
                <option value="request_more_info">Request More Info</option>
              </select>
            </div>

            {reviewAction === 'override' && (
              <div style={{ marginTop: '10px' }}>
                <label style={labelStyle}>New Risk Level:</label>
                <select value={overrideRisk} onChange={e => setOverrideRisk(e.target.value)} style={selectStyle}>
                  <option value="">Select...</option>
                  <option value="Low">Low</option>
                  <option value="Medium">Medium</option>
                  <option value="High">High</option>
                  <option value="Critical">Critical</option>
                </select>
              </div>
            )}

            <div style={{ marginTop: '10px' }}>
              <label style={labelStyle}>Notes:</label>
              <textarea value={notes} onChange={e => setNotes(e.target.value)} style={textArea} rows={3} placeholder="Review notes..." />
            </div>

            <div style={modalActions}>
              <button onClick={() => setReviewModal(null)} style={cancelBtn}>Cancel</button>
              <button onClick={handleSubmitReview} disabled={submitting} style={submitBtn}>
                {submitting ? 'Submitting...' : 'Submit Review'}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

const emptyState = { textAlign: 'center', padding: '40px', background: '#fff', borderRadius: '8px' };
const tableStyle = { width: '100%', borderCollapse: 'collapse', background: '#fff', borderRadius: '8px', overflow: 'hidden', boxShadow: '0 1px 3px rgba(0,0,0,0.1)' };
const th = { padding: '10px 12px', textAlign: 'left', background: '#dfe6e9', fontSize: '12px', fontWeight: 700, textTransform: 'uppercase' };
const td = { padding: '10px 12px', borderBottom: '1px solid #f0f0f0', fontSize: '13px' };
const actionBtn = { padding: '5px 14px', borderRadius: '6px', border: '1px solid #0984e3', background: '#fff', color: '#0984e3', cursor: 'pointer', fontSize: '13px', fontWeight: 600 };
const overlay = { position: 'fixed', top: 0, left: 0, right: 0, bottom: 0, background: 'rgba(0,0,0,0.4)', display: 'flex', alignItems: 'center', justifyContent: 'center', zIndex: 1000 };
const modal = { background: '#fff', padding: '24px', borderRadius: '12px', width: '440px', boxShadow: '0 4px 20px rgba(0,0,0,0.2)' };
const labelStyle = { display: 'block', fontSize: '13px', fontWeight: 600, marginBottom: '4px' };
const selectStyle = { width: '100%', padding: '8px', borderRadius: '6px', border: '1px solid #dfe6e9', fontSize: '14px' };
const textArea = { width: '100%', padding: '8px', borderRadius: '6px', border: '1px solid #dfe6e9', fontSize: '14px', fontFamily: 'inherit' };
const modalActions = { display: 'flex', justifyContent: 'flex-end', gap: '10px', marginTop: '16px' };
const cancelBtn = { padding: '8px 16px', borderRadius: '6px', border: '1px solid #dfe6e9', background: '#fff', cursor: 'pointer' };
const submitBtn = { padding: '8px 16px', borderRadius: '6px', border: 'none', background: '#0984e3', color: '#fff', fontWeight: 600, cursor: 'pointer' };
