const BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

async function request(path: string, opts: RequestInit = {}) {
  const res = await fetch(`${BASE_URL}${path}`, {
    headers: { 'Content-Type': 'application/json' },
    ...opts,
  });
  if (!res.ok) {
    const text = await res.text();
    throw new Error(`${res.status}: ${text}`);
  }
  return res.json();
}

export const getAccounts = () => request('/accounts');
export const getTrades = () => request('/trades');
export const startBot = () => request('/start-bot', { method: 'POST' });
export const stopBot = () => request('/stop-bot', { method: 'POST' });
export const updateSettings = (brick_size: number) => request('/update-settings', { method: 'POST', body: JSON.stringify({ brick_size }) });
