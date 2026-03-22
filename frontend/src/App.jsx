import { useState } from 'react';
import DashboardPage from './pages/DashboardPage';
import UploadPage from './pages/UploadPage';
import AiChat from './components/AiChat';
import './styles/globals.css';

const NAV = [
  { id: 'dashboard', label: 'Dashboard' },
  { id: 'upload',    label: 'Upload Data' },
  { id: 'chat',      label: 'AI Analyst' },
];

export default function App() {
  const [page, setPage]         = useState('dashboard');
  const [sessionId, setSession] = useState('demo');

  return (
    <div style={{ display: 'flex', minHeight: '100vh', background: 'var(--bg-base)' }}>
      <aside style={{ width: 220, flexShrink: 0, background: 'var(--bg-surface)', borderRight: '1px solid var(--border)', display: 'flex', flexDirection: 'column', padding: '1.5rem 1rem' }}>
        <div style={{ marginBottom: '2rem' }}>
          <div style={{ fontFamily: 'var(--font-display)', fontSize: 18, fontWeight: 700, color: 'var(--accent-amber)', letterSpacing: '-0.02em' }}>ChainSense</div>
          <div style={{ fontFamily: 'var(--font-mono)', fontSize: 10, color: 'var(--text-muted)', letterSpacing: '0.1em', textTransform: 'uppercase', marginTop: 2 }}>AI Platform</div>
        </div>
        <div style={{ marginBottom: 24, padding: '8px 10px', background: 'var(--bg-elevated)', borderRadius: 'var(--radius-sm)', fontSize: 11, fontFamily: 'var(--font-mono)' }}>
          <div style={{ color: 'var(--text-muted)', marginBottom: 2 }}>session</div>
          <div style={{ color: sessionId === 'demo' ? '#f0a500' : '#00c9a7' }}>{sessionId}</div>
        </div>
        <nav style={{ display: 'flex', flexDirection: 'column', gap: 4, flex: 1 }}>
          {NAV.map(n => (
            <button key={n.id} onClick={() => setPage(n.id)} style={{ padding: '9px 12px', borderRadius: 'var(--radius-sm)', textAlign: 'left', background: page === n.id ? 'var(--bg-hover)' : 'transparent', color: page === n.id ? 'var(--accent-amber)' : 'var(--text-secondary)', borderLeft: `2px solid ${page === n.id ? 'var(--accent-amber)' : 'transparent'}`, transition: 'all 0.15s', fontSize: 13, fontWeight: page === n.id ? 500 : 400 }}
              onMouseEnter={e => { if (page !== n.id) e.currentTarget.style.color = 'var(--text-primary)'; }}
              onMouseLeave={e => { if (page !== n.id) e.currentTarget.style.color = 'var(--text-secondary)'; }}>
              {n.label}
            </button>
          ))}
        </nav>
        <div style={{ fontSize: 10, color: 'var(--text-muted)', fontFamily: 'var(--font-mono)', lineHeight: 1.8 }}>
          v1.0.0<br/>Grege Waren<br/>ChainSense AI
        </div>
      </aside>
      <main style={{ flex: 1, padding: '2rem', overflowY: 'auto' }}>
        <div style={{ maxWidth: 1100, margin: '0 auto' }}>
          <header style={{ marginBottom: '1.75rem', paddingBottom: '1rem', borderBottom: '1px solid var(--border)', display: 'flex', justifyContent: 'space-between', alignItems: 'flex-end' }}>
            <div>
              <h1 style={{ fontFamily: 'var(--font-display)', fontSize: 26, fontWeight: 700, letterSpacing: '-0.02em', lineHeight: 1 }}>{NAV.find(n => n.id === page)?.label}</h1>
              <p style={{ color: 'var(--text-muted)', fontSize: 12, fontFamily: 'var(--font-mono)', marginTop: 6 }}>{new Date().toLocaleDateString('en-KE', { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' })}</p>
            </div>
            {sessionId !== 'demo' && (
              <button onClick={() => setSession('demo')} style={{ fontSize: 12, padding: '6px 14px', border: '1px solid var(--border)', borderRadius: 'var(--radius-sm)', color: 'var(--text-secondary)' }}>Back to demo</button>
            )}
          </header>
          {page === 'dashboard' && <DashboardPage sessionId={sessionId} />}
          {page === 'upload'    && <UploadPage onSessionChange={sid => { setSession(sid); setPage('dashboard'); }} />}
          {page === 'chat'      && <AiChat sessionId={sessionId} />}
        </div>
      </main>
    </div>
  );
}
