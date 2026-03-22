import { Line } from 'react-chartjs-2';
import { Chart, CategoryScale, LinearScale, PointElement, LineElement, Tooltip, Filler } from 'chart.js';
Chart.register(CategoryScale, LinearScale, PointElement, LineElement, Tooltip, Filler);

export default function RevenueChart({ trend = [], forecast = [] }) {
  const labels   = [...trend, ...forecast].map(d => d.month);
  const actuals  = trend.map(d => d.revenue);
  const fcast    = [
    ...Array(trend.length - 1).fill(null),
    trend.length ? trend[trend.length - 1].revenue : null,
    ...forecast.map(d => d.revenue),
  ];
  const data = {
    labels,
    datasets: [
      { label: 'Revenue', data: actuals, borderColor: '#00c9a7', backgroundColor: 'rgba(0,201,167,0.08)', borderWidth: 2, pointRadius: 3, pointBackgroundColor: '#00c9a7', tension: 0.4, fill: true },
      { label: 'Forecast', data: fcast, borderColor: '#f0a500', backgroundColor: 'rgba(240,165,0,0.05)', borderWidth: 2, borderDash: [5, 4], pointRadius: 3, pointBackgroundColor: '#f0a500', tension: 0.4, fill: false },
    ],
  };
  const options = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: { display: false },
      tooltip: { backgroundColor: '#1a1f29', borderColor: 'rgba(255,255,255,0.1)', borderWidth: 1, titleColor: '#8892a4', bodyColor: '#e8eaf0', callbacks: { label: ctx => ` $${ctx.parsed.y.toLocaleString()}` } },
    },
    scales: {
      x: { grid: { color: 'rgba(255,255,255,0.04)' }, ticks: { color: '#4a5265', font: { family: 'IBM Plex Mono', size: 11 }, maxRotation: 45 } },
      y: { grid: { color: 'rgba(255,255,255,0.04)' }, ticks: { color: '#4a5265', font: { family: 'IBM Plex Mono', size: 11 }, callback: v => `$${(v / 1000).toFixed(0)}k` } },
    },
  };
  return <div style={{ height: 260 }}><Line data={data} options={options} /></div>;
}
