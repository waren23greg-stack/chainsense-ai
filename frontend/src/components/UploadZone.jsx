import { useState, useRef } from 'react';
import { api } from '../api/client';

export default function UploadZone({ onSuccess }) {
  const [dragging, setDragging] = useState(false);
  const [status, setStatus]     = useState(null);
  const [loading, setLoading]   = useState(false);
  const inputRef = useRef();

  const upload = async (file) => {
    if (!file) return;
    if (!file.name.endsWith('.csv')) { setStatus({ type: 'error', msg: 'Only CSV files accepted.' }); return; }
    setLoading(true); setStatus(null);
    const form = new FormData();
    form.append('file', file);
    try {
      const res = await api.upload(form);
      if (res.success) { setStatus({ type: 'success', msg: `Loaded ${res.data.rows.toLocaleString()} rows · ${res.data.columns} columns` }); onSuccess?.(res.data); }
      else setStatus({ type: 'error', msg: res.error || 'Upload failed.' });
    } catch (e) { setStatus({ type: 'error', msg: e.message }); }
    finally { setLoading(false); }
  };

  return (
    <div>
      <div onClick={() => inputRef.current?.click()}
        onDragOver={e => { e.preventDefault(); setDragging(true); }}
        onDragLeave={() => setDragging(false)}
        onDrop={e => { e.preventDefault(); setDragging(false); upload(e.dataTransfer.files[0]); }}
        style={{ border: `2px dashed ${dragging ? 'var(--accent-amber)' : 'var(--border-bright)'}`, borderRadius: 'var(--radius-md)', padding: '3rem 2rem', textAlign: 'center', cursor: 'pointer', background: dragging ? 'rgba(240,165,0,0.04)' : 'transparent', transition: 'all 0.2s' }}>
        <div style={{ fontSize: 32, marginBottom: 12 }}>⬆</div>
        <p style={{ fontWeight: 500, marginBottom: 6 }}>{loading ? 'Processing...' : 'Drop your CSV here or click to browse'}</p>
        <p style={{ color: 'var(--text-muted)', fontSize: 12 }}>Max 10MB · CSV files only</p>
        <input ref={inputRef} type="file" accept=".csv" style={{ display: 'none' }} onChange={e => upload(e.target.files[0])} />
      </div>
      {status && (
        <div style={{ marginTop: 12, padding: '10px 14px', borderRadius: 'var(--radius-sm)', fontSize: 13, background: status.type === 'success' ? 'rgba(0,201,167,0.1)' : 'rgba(255,77,106,0.1)', border: `1px solid ${status.type === 'success' ? '#00c9a7' : '#ff4d6a'}`, color: status.type === 'success' ? '#00c9a7' : '#ff4d6a' }}>
          {status.msg}
        </div>
      )}
    </div>
  );
}
