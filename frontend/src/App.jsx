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
        <div style={navBrand}>Child Welfare Intake</div>
        <div style={navLinks}>
          <Link to="/" style={linkStyle}>New Intake</Link>
          <Link to="/dashboard" style={linkStyle}>Dashboard</Link>
          <Link to="/review" style={linkStyle}>Human Review</Link>
        </div>
      </nav>
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

const navStyle = { display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '12px 24px', background: '#2d3436', color: '#fff' };
const navBrand = { fontWeight: 700, fontSize: '18px' };
const navLinks = { display: 'flex', gap: '20px' };
const linkStyle = { color: '#dfe6e9', fontSize: '14px' };
const mainStyle = { maxWidth: '1200px', margin: '0 auto', padding: '24px' };
