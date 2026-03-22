const STYLE = {
  high:   { bg: 'rgba(255,77,106,0.1)',  border: '#ff4d6a', dot: '#ff4d6a' },
  medium: { bg: 'rgba(240,165,0,0.1)',   border: '#f0a500', dot: '#f0a500' },
  low:    { bg: 'rgba(0,201,167,0.1)',   border: '#00c9a7', dot: '#00c9a7' },
};

export default function RiskBanner({ risks = [] }) {
  if (!risks.length) return null;
  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 8, marginBottom: '1.5rem' }}>
      {risks.map((r, i) => {
        const s = STYLE[r.level] || STYLE.low;
        return (
          <div key={i} style={{ background: s.bg, border: `1px solid ${s.border}`, borderRadius: 'var(--radius-sm)', padding: '10px 14px', display: 'flex', alignItems: 'center', gap: 10 }}>
            <span style={{ width: 7, height: 7, borderRadius: '50%', background: s.dot, flexShrink: 0 }} />
            <span style={{ fontSize: 13 }}>{r.message}</span>
            <span style={{ marginLeft: 'auto', fontSize: 11, fontFamily: 'var(--font-mono)', color: s.dot, textTransform: 'uppercase', letterSpacing: '0.06em' }}>{r.level}</span>
          </div>
        );
      })}
    </div>
  );
}
