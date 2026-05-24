import React from 'react';
import { Routes, Route, Link } from 'react-router-dom';
import IntakePage from './pages/IntakePage';
import DashboardPage from './pages/DashboardPage';
import CaseDetailPage from './pages/CaseDetailPage';
import HumanReviewPage from './pages/HumanReviewPage';

export default function App() {
  return (
    <div>
      <nav style={navStyle}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
          <div style={navBrand}>Child Welfare Intake System</div>
          <span style={tagStyle}>Agentic AI POC</span>
        </div>
        <div style={navLinks}>
          <Link to="/" style={linkStyle}>New Intake</Link>
          <Link to="/dashboard" style={linkStyle}>Dashboard</Link>
          <Link to="/review" style={linkStyle}>Human Review</Link>
        </div>
      </nav>
      <div style={techBar}>
        LangGraph Multi-Agent Orchestration | Claude / Ollama LLM | MCP Servers | LocalStack AWS
      </div>
      <main style={mainStyle}>
        <Routes>
          <Route path="/" element={<IntakePage />} />
          <Route path="/dashboard" element={<DashboardPage />} />
          <Route path="/cases/:caseId" element={<CaseDetailPage />} />
          <Route path="/review" element={<HumanReviewPage />} />
        </Routes>
      </main>
    </div>
  );
}

const navStyle = { display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '14px 24px', background: 'linear-gradient(135deg, #2d3436, #0984e3)', color: '#fff' };
const navBrand = { fontWeight: 700, fontSize: '18px' };
const tagStyle = { fontSize: '10px', padding: '2px 8px', borderRadius: '4px', background: 'rgba(255,255,255,0.2)', fontWeight: 600, letterSpacing: '0.5px' };
const navLinks = { display: 'flex', gap: '20px' };
const linkStyle = { color: '#dfe6e9', fontSize: '14px' };
const techBar = { background: '#f0f0f0', textAlign: 'center', padding: '6px 0', fontSize: '11px', color: '#636e72', letterSpacing: '0.5px', fontWeight: 500, borderBottom: '1px solid #dfe6e9' };
const mainStyle = { maxWidth: '1200px', margin: '0 auto', padding: '24px' };
