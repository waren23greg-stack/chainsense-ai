const BASE = '/api';

async function request(path, options = {}) {
  const res = await fetch(`${BASE}${path}`, {
    headers: { 'Content-Type': 'application/json', ...options.headers },
    ...options,
  });
  const data = await res.json();
  if (!res.ok) throw new Error(data.error || `HTTP ${res.status}`);
  return data;
}

export const api = {
  health:        ()                    => request('/health'),
  demo:          ()                    => request('/demo'),
  upload:        (formData)            => fetch(`${BASE}/upload`, { method: 'POST', body: formData }).then(r => r.json()),
  fullAnalytics: (sid = 'demo')        => request(`/analytics/full?session_id=${sid}`),
  forecast:      (sid = 'demo', p = 6) => request(`/analytics/forecast?session_id=${sid}&periods=${p}`),
  risks:         (sid = 'demo')        => request(`/analytics/risks?session_id=${sid}`),
  suppliers:     (sid = 'demo')        => request(`/analytics/suppliers?session_id=${sid}`),
  chat:          (message, session_id, history) =>
    request('/ai/chat', { method: 'POST', body: JSON.stringify({ message, session_id, history }) }),
};
