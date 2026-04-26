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
    { id: 1, login: 316923999, server: 'XMGlobal-MT5 7', status: 'active' }
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

export const executeTrade = async (trade: {
  account_id: number;
  symbol: string;
  trade_type: 'buy' | 'sell';
  lot_size: number;
  stop_loss?: number;
  take_profit?: number;
}) => {
  console.log('📤 [API] Executing trade:', trade);
  try {
    const res = await fetch(`${BASE_URL}/api/execute-trade`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(trade)
    });
    
    if (!res.ok) {
      const errorText = await res.text();
      console.error('❌ [API] Trade execution failed:', res.status, errorText);
      throw new Error(`Trade failed: ${errorText}`);
    }
    
    const result = await res.json();
    console.log('✅ [API] Trade executed successfully:', result);
    return result;
  } catch (error) {
    const errorMsg = error instanceof Error ? error.message : String(error);
    console.error('❌ [API] Trade execution error:', errorMsg);
    throw error;
  }
};
