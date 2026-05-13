import React, { useState, useRef, useEffect } from 'react';
import { createSession, submitMessage, uploadDocument } from '../api/client';

export default function IntakePage() {
  const [caseId, setCaseId] = useState(null);
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [intakeComplete, setIntakeComplete] = useState(false);
  const [progress, setProgress] = useState(0);
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
    setMessages(prev => [...prev, { role: 'user', content: `Uploading: ${file.name}` }]);
    try {
      const res = await uploadDocument(caseId, file, 'other');
      setMessages(prev => [...prev, { role: 'assistant', content: `Document uploaded: ${res.data.fileName} (extraction: ${res.data.extractionStatus})` }]);
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
        <button onClick={startSession} disabled={loading} style={btnPrimary}>
          {loading ? 'Starting...' : 'Start Intake Session'}
        </button>
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

      {!intakeComplete && (
        <div style={inputArea}>
          <button onClick={() => fileRef.current?.click()} style={uploadBtn} title="Upload document">
            +
          </button>
          <input type="file" ref={fileRef} onChange={handleUpload} style={{ display: 'none' }} />
          <textarea
            value={input}
            onChange={e => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="Describe your concern..."
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
const uploadBtn = { width: '40px', height: '40px', borderRadius: '50%', border: '1px solid #dfe6e9', background: '#fff', cursor: 'pointer', fontSize: '20px', display: 'flex', alignItems: 'center', justifyContent: 'center' };
