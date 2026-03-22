const fmt  = n => typeof n === 'number' ? `$${Math.round(n).toLocaleString()}` : '—';
const fmtD = n => typeof n === 'number' ? `${n.toFixed(1)}d` : '—';
const fmtR = n => typeof n === 'number' ? `${(n * 100).toFixed(0)}%` : '—';

export default function SupplierTable({ suppliers = [] }) {
  if (!suppliers.length) return <p style={{ color: 'var(--text-muted)', fontSize: 13 }}>No supplier data.</p>;
  return (
    <div style={{ overflowX: 'auto' }}>
      <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: 13 }}>
        <thead>
          <tr style={{ borderBottom: '1px solid var(--border)' }}>
            {['Supplier','Orders','Revenue','Avg Delay','On-Time'].map(h => (
              <th key={h} style={{ padding: '8px 12px', textAlign: 'left', color: 'var(--text-muted)', fontWeight: 500, fontFamily: 'var(--font-mono)', fontSize: 11, letterSpacing: '0.06em', textTransform: 'uppercase', whiteSpace: 'nowrap' }}>{h}</th>
            ))}
          </tr>
        </thead>
        <tbody>
          {suppliers.map((s, i) => (
            <tr key={i} style={{ borderBottom: '1px solid var(--border)', transition: 'background 0.15s' }}
              onMouseEnter={e => e.currentTarget.style.background = 'var(--bg-hover)'}
              onMouseLeave={e => e.currentTarget.style.background = 'transparent'}>
              <td style={{ padding: '10px 12px', fontWeight: 500 }}>{s.supplier_name || s.supplier || '—'}</td>
              <td style={{ padding: '10px 12px', fontFamily: 'var(--font-mono)', color: 'var(--text-secondary)' }}>{s.order_count}</td>
              <td style={{ padding: '10px 12px', fontFamily: 'var(--font-mono)', color: '#00c9a7' }}>{fmt(s.total_revenue)}</td>
              <td style={{ padding: '10px 12px', fontFamily: 'var(--font-mono)', color: s.avg_delay > 7 ? '#ff4d6a' : 'var(--text-secondary)' }}>{fmtD(s.avg_delay)}</td>
              <td style={{ padding: '10px 12px', fontFamily: 'var(--font-mono)', color: s.on_time_rate > 0.5 ? '#00c9a7' : '#f0a500' }}>{fmtR(s.on_time_rate)}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
