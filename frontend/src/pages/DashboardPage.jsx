import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { listCases } from '../api/client';

const riskColors = { Low: '#00b894', Medium: '#fdcb6e', High: '#e17055', Critical: '#d63031' };

export default function DashboardPage() {
  const [cases, setCases] = useState([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [statusFilter, setStatusFilter] = useState('');
  const [riskFilter, setRiskFilter] = useState('');
  const [loading, setLoading] = useState(false);

  useEffect(() => { fetchCases(); }, [page, statusFilter, riskFilter]);

  async function fetchCases() {
    setLoading(true);
    try {
      const params = { page, pageSize: 20 };
      if (statusFilter) params.status = statusFilter;
      if (riskFilter) params.riskLevel = riskFilter;
      const res = await listCases(params);
      setCases(res.data.cases);
      setTotal(res.data.totalCount);
    } catch {
      setCases([]);
    }
    setLoading(false);
  }

  return (
    <div>
      <h2 style={{ marginBottom: '16px' }}>Caseworker Dashboard</h2>

      <div style={filterBar}>
        <select value={statusFilter} onChange={e => { setStatusFilter(e.target.value); setPage(1); }} style={selectStyle}>
          <option value="">All Statuses</option>
          <option value="IN_PROGRESS">In Progress</option>
          <option value="READY_FOR_CASEWORKER_REVIEW">Ready for Review</option>
          <option value="ESCALATED_TO_SUPERVISOR">Escalated</option>
          <option value="CRITICAL_IMMEDIATE_REVIEW">Critical</option>
          <option value="NEEDS_MORE_INFORMATION">Needs Info</option>
          <option value="BIAS_REVIEW_REQUIRED">Bias Review</option>
        </select>
        <select value={riskFilter} onChange={e => { setRiskFilter(e.target.value); setPage(1); }} style={selectStyle}>
          <option value="">All Risk Levels</option>
          <option value="Low">Low</option>
          <option value="Medium">Medium</option>
          <option value="High">High</option>
          <option value="Critical">Critical</option>
        </select>
        <span style={{ color: '#636e72', fontSize: '14px' }}>{total} case(s)</span>
      </div>

      {loading ? <p>Loading...</p> : (
        <table style={tableStyle}>
          <thead>
            <tr>
              <th style={th}>Case ID</th>
              <th style={th}>Status</th>
              <th style={th}>Risk Level</th>
              <th style={th}>Urgency</th>
              <th style={th}>Data Quality</th>
              <th style={th}>Bias</th>
              <th style={th}>Review</th>
              <th style={th}>Created</th>
            </tr>
          </thead>
          <tbody>
            {cases.map(c => (
              <tr key={c.caseId}>
                <td style={td}><Link to={`/cases/${c.caseId}`}>{c.caseId}</Link></td>
                <td style={td}><span style={statusPill}>{c.status?.replace(/_/g, ' ')}</span></td>
                <td style={td}><span style={{ ...riskBadge, background: riskColors[c.riskLevel] || '#b2bec3' }}>{c.riskLevel || '—'}</span></td>
                <td style={td}>{c.urgency || '—'}</td>
                <td style={td}>{c.dataQualityScore ? `${Math.round(parseFloat(c.dataQualityScore) * 100)}%` : '—'}</td>
                <td style={td}>{c.biasStatus || '—'}</td>
                <td style={td}>{c.humanReviewRequired ? 'Yes' : 'No'}</td>
                <td style={td}>{c.createdAt?.slice(0, 16)}</td>
              </tr>
            ))}
            {cases.length === 0 && <tr><td colSpan={8} style={{ ...td, textAlign: 'center' }}>No cases found</td></tr>}
          </tbody>
        </table>
      )}

      <div style={paginationBar}>
        <button disabled={page <= 1} onClick={() => setPage(p => p - 1)} style={pageBtn}>Previous</button>
        <span>Page {page}</span>
        <button disabled={cases.length < 20} onClick={() => setPage(p => p + 1)} style={pageBtn}>Next</button>
      </div>
    </div>
  );
}

const filterBar = { display: 'flex', gap: '12px', alignItems: 'center', marginBottom: '16px' };
const selectStyle = { padding: '8px 12px', borderRadius: '6px', border: '1px solid #dfe6e9', fontSize: '14px' };
const tableStyle = { width: '100%', borderCollapse: 'collapse', background: '#fff', borderRadius: '8px', overflow: 'hidden', boxShadow: '0 1px 3px rgba(0,0,0,0.1)' };
const th = { padding: '10px 12px', textAlign: 'left', background: '#dfe6e9', fontSize: '12px', fontWeight: 700, textTransform: 'uppercase' };
const td = { padding: '10px 12px', borderBottom: '1px solid #f0f0f0', fontSize: '13px' };
const statusPill = { fontSize: '11px', padding: '3px 8px', borderRadius: '8px', background: '#f0f0f0' };
const riskBadge = { color: '#fff', padding: '3px 10px', borderRadius: '10px', fontSize: '12px', fontWeight: 600 };
const paginationBar = { display: 'flex', justifyContent: 'center', alignItems: 'center', gap: '16px', marginTop: '16px' };
const pageBtn = { padding: '6px 16px', borderRadius: '6px', border: '1px solid #dfe6e9', background: '#fff', cursor: 'pointer' };
