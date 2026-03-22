import { useState, useRef, useEffect } from 'react';
import { api } from '../api/client';

const SUGGESTIONS = ['Which suppliers are underperforming?', 'What are the top risk alerts?', 'Summarise revenue trends'];

export default function AiChat({ sessionId = 'demo' }) {
  const [messages, setMessages] = useState([{ role: 'assistant', content: 'ChainSense AI ready. Ask me anything about your supply chain data.' }]);
  const [input, setInput]       = useState('');
  const [loading, setLoading]   = useState(false);
  const bottomRef = useRef(null);

  useEffect(() => { bottomRef.current?.scrollIntoView({ behavior: 'smooth' }); }, [messages]);

  const send = async () => {
    const msg = input.trim();
    if (!msg || loading) return;
    const history = messages.slice(-10).map(m => ({ role: m.role, content: m.content }));
    setMessages(prev => [...prev, { role: 'user', content: msg }]);
    setInput('');
    setLoading(true);
    try {
      const res = await api.chat(msg, sessionId, history);
      setMessages(prev => [...prev, { role: 'assistant', content: res.reply, chart: res.chart_suggestion }]);
    } catch (e) {
      setMessages(prev => [...prev, { role: 'assistant', content: `Error: ${e.message}` }]);
    } finally { setLoading(false); }
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', height: '100%', minHeight: 500 }}>
      <div style={{ flex: 1, overflowY: 'auto', display: 'flex', flexDirection: 'column', gap: 12, paddingBottom: 16 }}>
        {messages.map((m, i) => (
          <div key={i} style={{ display: 'flex', justifyContent: m.role === 'user' ? 'flex-end' : 'flex-start' }}>
            <div style={{ maxWidth: '82%', background: m.role === 'user' ? 'rgba(240,165,0,0.12)' : 'var(--bg-elevated)', border: `1px solid ${m.role === 'user' ? 'rgba(240,165,0,0.25)' : 'var(--border)'}`, borderRadius: 'var(--radius-md)', padding: '10px 14px', fontSize: 13, lineHeight: 1.7, whiteSpace: 'pre-wrap' }}>
              {m.content}
              {m.chart && <div style={{ marginTop: 8, padding: '6px 10px', background: 'rgba(0,201,167,0.08)', borderRadius: 6, fontSize: 11, fontFamily: 'var(--font-mono)', color: '#00c9a7' }}>Chart: {m.chart.type} · x: {m.chart.x_field} · y: {m.chart.y_field}</div>}
            </div>
          </div>
        ))}
        {loading && (
          <div style={{ display: 'flex', gap: 6, padding: '10px 14px' }}>
            {[0,1,2].map(i => <span key={i} style={{ width: 6, height: 6, borderRadius: '50%', background: 'var(--accent-amber)', opacity: 0.6 }} />)}
          </div>
        )}
        <div ref={bottomRef} />
      </div>
      <div style={{ display: 'flex', gap: 6, flexWrap: 'wrap', marginBottom: 10 }}>
        {SUGGESTIONS.map(s => (
          <button key={s} onClick={() => setInput(s)} style={{ fontSize: 11, padding: '4px 10px', border: '1px solid var(--border)', borderRadius: 20, color: 'var(--text-secondary)', background: 'var(--bg-elevated)', transition: 'all 0.15s' }}
            onMouseEnter={e => { e.target.style.borderColor = 'var(--accent-amber)'; e.target.style.color = 'var(--accent-amber)'; }}
            onMouseLeave={e => { e.target.style.borderColor = 'var(--border)'; e.target.style.color = 'var(--text-secondary)'; }}>
            {s}
          </button>
        ))}
      </div>
      <div style={{ display: 'flex', gap: 8 }}>
        <input value={input} onChange={e => setInput(e.target.value)} onKeyDown={e => e.key === 'Enter' && !e.shiftKey && send()}
          placeholder="Ask about your supply chain data..."
          style={{ flex: 1, padding: '10px 14px', fontSize: 13 }} />
        <button onClick={send} disabled={loading} style={{ padding: '10px 18px', background: loading ? 'var(--bg-hover)' : 'var(--accent-amber)', color: loading ? 'var(--text-muted)' : '#000', borderRadius: 'var(--radius-sm)', fontWeight: 600, fontSize: 13, transition: 'all 0.15s' }}>
          {loading ? '...' : 'Send'}
        </button>
      </div>
    </div>
  );
}
