import { useEffect, useState } from 'react';
import { api } from '../api/client';
import KpiCard from '../components/KpiCard';
import RiskBanner from '../components/RiskBanner';
import RevenueChart from '../components/RevenueChart';
import SupplierTable from '../components/SupplierTable';

export default function DashboardPage({ sessionId = 'demo' }) {
  const [data, setData]       = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError]     = useState(null);

  useEffect(() => {
    setLoading(true); setError(null);
    api.fullAnalytics(sessionId)
      .then(res => { setData(res.data); setLoading(false); })
      .catch(e  => { setError(e.message); setLoading(false); });
  }, [sessionId]);

  if (loading) return <div style={{ color: 'var(--text-muted)', padding: '3rem', textAlign: 'center', fontFamily: 'var(--font-mono)' }}>Loading analytics...</div>;
  if (error)   return <div style={{ color: '#ff4d6a', padding: '2rem' }}>Error: {error}</div>;
  if (!data)   return null;

  const k   = data.kpis || {};
  const fmt = n => n != null ? `$${Math.round(n).toLocaleString()}` : '—';

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
      <RiskBanner risks={data.risks || []} />
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(175px, 1fr))', gap: 12 }}>
        <KpiCard label="Total Revenue"     value={fmt(k.total_revenue)}       sub={`${k.row_count?.toLocaleString()} orders`} accent="#00c9a7" />
        <KpiCard label="Avg Order Value"   value={fmt(k.avg_order_value)}     sub="per order"       accent="#4d9fff" />
        <KpiCard label="Cancellation Rate" value={k.cancellation_rate != null ? `${k.cancellation_rate}%` : '—'} sub="of all orders" accent={k.cancellation_rate > 15 ? '#ff4d6a' : '#f0a500'} />
        <KpiCard label="Avg Delay"         value={k.avg_delay_days != null ? `${k.avg_delay_days}d` : '—'} sub={`max ${k.max_delay_days}d`} accent="#f0a500" />
        <KpiCard label="Active Suppliers"  value={k.unique_suppliers ?? '—'}  sub="in network"      accent="#00c9a7" />
      </div>
      <div style={{ background: 'var(--bg-surface)', border: '1px solid var(--border)', borderRadius: 'var(--radius-md)', padding: '1.25rem' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem' }}>
          <span style={{ fontFamily: 'var(--font-mono)', fontSize: 11, textTransform: 'uppercase', letterSpacing: '0.08em', color: 'var(--text-muted)' }}>Revenue trend</span>
          <div style={{ display: 'flex', gap: 16, fontSize: 11, fontFamily: 'var(--font-mono)' }}>
            <span style={{ color: '#00c9a7' }}>── Actual</span>
            <span style={{ color: '#f0a500' }}>- - Forecast</span>
          </div>
        </div>
        <RevenueChart trend={data.revenue_trend || []} forecast={data.forecast?.forecast || []} />
      </div>
      <div style={{ background: 'var(--bg-surface)', border: '1px solid var(--border)', borderRadius: 'var(--radius-md)', padding: '1.25rem' }}>
        <span style={{ fontFamily: 'var(--font-mono)', fontSize: 11, textTransform: 'uppercase', letterSpacing: '0.08em', color: 'var(--text-muted)', display: 'block', marginBottom: '1rem' }}>Supplier scorecard</span>
        <SupplierTable suppliers={data.suppliers || []} />
      </div>
    </div>
  );
}
