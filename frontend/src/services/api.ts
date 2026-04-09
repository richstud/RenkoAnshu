const BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

async function request(path: string, opts: RequestInit = {}) {
  try {
    const res = await fetch(`${BASE_URL}${path}`, {
      headers: { 'Content-Type': 'application/json' },
      ...opts,
    });
    if (!res.ok) {
      const text = await res.text();
      console.error(`API Error ${res.status}:`, text);
      return null;
    }
    return res.json();
  } catch (error) {
    console.error(`Request failed:`, error);
    return null;
  }
}

// Accounts - return mock data if backend is unavailable
export const getAccounts = async () => {
  const result = await request('/api/accounts');
  const data = result?.data || result || [];
  return Array.isArray(data) ? data : [
    { id: 1, login: 101510620, server: 'XMGlobal-MT5 10', status: 'active' }
  ];
};

// Trades - return empty if backend is unavailable
export const getTrades = async () => {
  const result = await request('/api/trades');
  const data = result?.data || result || [];
  return Array.isArray(data) ? data : [];
};

export const startBot = () => request('/api/start-bot', { method: 'POST' });
export const stopBot = () => request('/api/stop-bot', { method: 'POST' });
export const updateSettings = (brick_size: number) => request('/api/update-settings', { method: 'POST', body: JSON.stringify({ brick_size }) });

export const executeTrade = (trade: {
  account_id: number;
  symbol: string;
  trade_type: 'buy' | 'sell';
  lot_size: number;
  stop_loss?: number;
  take_profit?: number;
}) => request('/api/execute-trade', { 
  method: 'POST', 
  body: JSON.stringify(trade) 
});
