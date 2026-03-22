export default function KpiCard({ label, value, sub, accent = '#f0a500' }) {
  return (
    <div style={{ background: 'var(--bg-surface)', border: '1px solid var(--border)', borderRadius: 'var(--radius-md)', padding: '1.25rem', display: 'flex', flexDirection: 'column', gap: '0.5rem', transition: 'border-color 0.2s' }}
      onMouseEnter={e => e.currentTarget.style.borderColor = 'var(--border-bright)'}
      onMouseLeave={e => e.currentTarget.style.borderColor = 'var(--border)'}>
      <span style={{ fontSize: '11px', letterSpacing: '0.08em', textTransform: 'uppercase', color: 'var(--text-muted)', fontFamily: 'var(--font-mono)' }}>{label}</span>
      <span style={{ fontSize: '28px', fontWeight: 700, fontFamily: 'var(--font-mono)', color: accent, lineHeight: 1 }}>{value}</span>
      {sub && <span style={{ fontSize: '12px', color: 'var(--text-secondary)' }}>{sub}</span>}
    </div>
  );
}
