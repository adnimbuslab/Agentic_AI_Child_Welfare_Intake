import React, { useState, useRef, useEffect } from 'react';
import { createSession, submitMessage, uploadDocument } from '../api/client';

export default function IntakePage() {
  const [caseId, setCaseId] = useState(null);
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [intakeComplete, setIntakeComplete] = useState(false);
  const [progress, setProgress] = useState(0);
  const [docCategory, setDocCategory] = useState('other');
  const [uploadedDocs, setUploadedDocs] = useState([]);
  const fileRef = useRef();
  const chatEndRef = useRef();

  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  async function startSession() {
    setLoading(true);
    try {
      const res = await createSession('reporter');
      setCaseId(res.data.caseId);
      setMessages([{ role: 'assistant', content: `Session started. Case ID: ${res.data.caseId}\n\nPlease describe your concern about the child. You can also upload any supporting documents.` }]);
    } catch (err) {
      setMessages([{ role: 'assistant', content: 'Failed to start session. Please try again.' }]);
    }
    setLoading(false);
  }

  async function handleSend() {
    if (!input.trim() || !caseId || loading) return;
    const text = input.trim();
    setInput('');
    setMessages(prev => [...prev, { role: 'user', content: text }]);
    setLoading(true);
    try {
      const res = await submitMessage(caseId, text);
      setMessages(prev => [...prev, { role: 'assistant', content: res.data.agentResponse }]);
      setIntakeComplete(res.data.intakeComplete);
      const questions = res.data.followUpQuestions || [];
      const totalFields = 10;
      const answeredFields = totalFields - questions.length;
      setProgress(Math.round((answeredFields / totalFields) * 100));
    } catch (err) {
      const detail = err.response?.data?.detail || 'Error processing message';
      setMessages(prev => [...prev, { role: 'assistant', content: `Error: ${detail}` }]);
    }
    setLoading(false);
  }

  async function handleUpload(e) {
    const file = e.target.files?.[0];
    if (!file || !caseId) return;
    setLoading(true);
    setMessages(prev => [...prev, { role: 'user', content: `Uploading [${docCategory}]: ${file.name}` }]);
    try {
      const res = await uploadDocument(caseId, file, docCategory);
      setUploadedDocs(prev => [...prev, { name: res.data.fileName, category: docCategory, status: res.data.extractionStatus }]);
      setMessages(prev => [...prev, { role: 'assistant', content: `Document uploaded: ${res.data.fileName} [${docCategory}] (extraction: ${res.data.extractionStatus})` }]);
    } catch (err) {
      const detail = err.response?.data?.detail || 'Upload failed';
      setMessages(prev => [...prev, { role: 'assistant', content: `Upload error: ${detail}` }]);
    }
    setLoading(false);
    if (fileRef.current) fileRef.current.value = '';
  }

  function handleKeyDown(e) {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  }

  if (!caseId) {
    return (
      <div style={startContainer}>
        <h2>New Child Welfare Intake</h2>
        <p style={{ margin: '12px 0', color: '#636e72' }}>Start a new intake session to report a child welfare concern.</p>
        <p style={{ margin: '8px 0 20px', color: '#b2bec3', fontSize: '13px' }}>
          AI-assisted intake with 5 specialized agents: Intake Understanding, Risk Assessment,
          Data Quality, Bias Monitoring, and Explanation Generation.
        </p>
        <button onClick={startSession} disabled={loading} style={btnPrimary}>
          {loading ? 'Starting...' : 'Start Intake Session'}
        </button>
        <div style={{ marginTop: '24px', display: 'flex', gap: '12px', justifyContent: 'center', flexWrap: 'wrap' }}>
          {['Intake Understanding', 'Risk Assessment', 'Data Quality', 'Bias Monitoring', 'Explanation'].map(agent => (
            <span key={agent} style={{ fontSize: '11px', padding: '4px 10px', borderRadius: '12px', background: '#e8f4fd', color: '#0984e3', fontWeight: 500 }}>{agent}</span>
          ))}
        </div>
      </div>
    );
  }

  return (
    <div style={chatContainer}>
      <div style={headerBar}>
        <span>Case: <strong>{caseId}</strong></span>
        <span style={statusBadge(intakeComplete)}>{intakeComplete ? 'Complete' : 'In Progress'}</span>
        <span>Progress: {progress}%</span>
      </div>

      <div style={messageList}>
        {messages.map((m, i) => (
          <div key={i} style={messageBubble(m.role)}>
            <div style={messageLabel}>{m.role === 'user' ? 'You' : 'System'}</div>
            <div style={{ whiteSpace: 'pre-wrap' }}>{m.content}</div>
          </div>
        ))}
        {loading && <div style={messageBubble('assistant')}><em>Processing...</em></div>}
        <div ref={chatEndRef} />
      </div>

      {uploadedDocs.length > 0 && (
        <div style={docBar}>
          <strong style={{ fontSize: '11px' }}>Attached Documents:</strong>
          {uploadedDocs.map((d, i) => (
            <span key={i} style={docChip}>{d.name} [{d.category}]</span>
          ))}
        </div>
      )}

      {!intakeComplete && (
        <div style={inputArea}>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '4px' }}>
            <select value={docCategory} onChange={e => setDocCategory(e.target.value)} style={categorySelect}>
              <option value="reporter_identification">Reporter ID (DL)</option>
              <option value="child_identification">Child ID (Birth Cert)</option>
              <option value="incident_report">Incident Report</option>
              <option value="medical_records">Medical Records</option>
              <option value="court_documents">Court Documents</option>
              <option value="other">Other</option>
            </select>
            <button onClick={() => fileRef.current?.click()} style={uploadBtn} title="Upload document">
              Upload
            </button>
          </div>
          <input type="file" ref={fileRef} onChange={handleUpload} style={{ display: 'none' }} />
          <textarea
            value={input}
            onChange={e => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="Describe your concern about the child..."
            style={textInput}
            rows={2}
          />
          <button onClick={handleSend} disabled={loading || !input.trim()} style={btnPrimary}>
            Send
          </button>
        </div>
      )}
    </div>
  );
}

const startContainer = { textAlign: 'center', marginTop: '80px' };
const chatContainer = { display: 'flex', flexDirection: 'column', height: 'calc(100vh - 120px)' };
const headerBar = { display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '10px 16px', background: '#fff', borderRadius: '8px', marginBottom: '12px', boxShadow: '0 1px 3px rgba(0,0,0,0.1)' };
const statusBadge = (complete) => ({ padding: '4px 10px', borderRadius: '12px', fontSize: '12px', fontWeight: 600, background: complete ? '#00b894' : '#fdcb6e', color: complete ? '#fff' : '#2d3436' });
const messageList = { flex: 1, overflowY: 'auto', padding: '8px 0' };
const messageBubble = (role) => ({ maxWidth: '75%', marginLeft: role === 'user' ? 'auto' : '0', marginRight: role === 'user' ? '0' : 'auto', marginBottom: '10px', padding: '10px 14px', borderRadius: '12px', background: role === 'user' ? '#0984e3' : '#fff', color: role === 'user' ? '#fff' : '#2d3436', boxShadow: '0 1px 2px rgba(0,0,0,0.08)' });
const messageLabel = { fontSize: '11px', fontWeight: 600, marginBottom: '4px', opacity: 0.7 };
const inputArea = { display: 'flex', gap: '8px', alignItems: 'flex-end', padding: '12px 0' };
const textInput = { flex: 1, padding: '10px 14px', borderRadius: '8px', border: '1px solid #dfe6e9', fontSize: '14px', resize: 'none', fontFamily: 'inherit' };
const btnPrimary = { padding: '10px 20px', borderRadius: '8px', border: 'none', background: '#0984e3', color: '#fff', fontWeight: 600, cursor: 'pointer', fontSize: '14px' };
const uploadBtn = { padding: '6px 12px', borderRadius: '6px', border: '1px solid #dfe6e9', background: '#fff', cursor: 'pointer', fontSize: '12px', fontWeight: 600, color: '#0984e3' };
const categorySelect = { padding: '4px 8px', borderRadius: '4px', border: '1px solid #dfe6e9', fontSize: '11px', width: '130px' };
const docBar = { display: 'flex', gap: '6px', alignItems: 'center', padding: '6px 12px', background: '#e8f4fd', borderRadius: '6px', flexWrap: 'wrap', marginBottom: '4px' };
const docChip = { fontSize: '11px', padding: '2px 8px', borderRadius: '4px', background: '#fff', border: '1px solid #b2bec3' };
