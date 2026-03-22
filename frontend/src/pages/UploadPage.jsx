import { useState } from 'react';
import UploadZone from '../components/UploadZone';

export default function UploadPage({ onSessionChange }) {
  const [uploaded, setUploaded] = useState(null);
  return (
    <div style={{ maxWidth: 600, margin: '0 auto', display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
      <div>
        <h2 style={{ fontFamily: 'var(--font-display)', fontSize: 22, marginBottom: 6 }}>Upload your data</h2>
        <p style={{ color: 'var(--text-secondary)', fontSize: 13 }}>Upload a CSV to analyse your own supply chain. Session expires in 1 hour.</p>
      </div>
      <UploadZone onSuccess={data => { setUploaded(data); onSessionChange?.(data.session_id); }} />
      {uploaded && (
        <div style={{ background: 'var(--bg-surface)', border: '1px solid var(--border)', borderRadius: 'var(--radius-md)', padding: '1.25rem', fontSize: 13 }}>
          <p style={{ fontWeight: 500, marginBottom: 12, color: '#00c9a7' }}>File loaded successfully</p>
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '10px 20px' }}>
            {[['Filename', uploaded.filename], ['Rows', uploaded.rows?.toLocaleString()], ['Columns', uploaded.columns], ['Session', uploaded.session_id]].map(([k, v]) => (
              <div key={k}>
                <div style={{ fontSize: 11, color: 'var(--text-muted)', fontFamily: 'var(--font-mono)', textTransform: 'uppercase', letterSpacing: '0.06em', marginBottom: 2 }}>{k}</div>
                <div style={{ fontFamily: 'var(--font-mono)' }}>{v}</div>
              </div>
            ))}
          </div>
          {uploaded.detected_roles && (
            <div style={{ marginTop: 16 }}>
              <div style={{ fontSize: 11, color: 'var(--text-muted)', fontFamily: 'var(--font-mono)', textTransform: 'uppercase', letterSpacing: '0.06em', marginBottom: 8 }}>Detected columns</div>
              <div style={{ display: 'flex', flexWrap: 'wrap', gap: 6 }}>
                {Object.entries(uploaded.detected_roles).map(([role, col]) => (
                  <span key={role} style={{ fontSize: 11, padding: '3px 8px', background: 'rgba(0,201,167,0.1)', border: '1px solid rgba(0,201,167,0.25)', borderRadius: 20, color: '#00c9a7', fontFamily: 'var(--font-mono)' }}>{role}: {col}</span>
                ))}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
