const BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';
async function request(path, opts = {}) {
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
    }
    catch (error) {
        console.error(`Request failed:`, error);
        return null;
    }
}
// Accounts - return empty array if backend is unavailable
export const getAccounts = async () => {
    const result = await request('/api/accounts');
    const data = result?.data || result || [];
    return Array.isArray(data) ? data : [];
};
// Trades - return empty if backend is unavailable
export const getTrades = async () => {
    const result = await request('/api/trades');
    const data = result?.data || result || [];
    return Array.isArray(data) ? data : [];
};
export const startBot = () => request('/api/start-bot', { method: 'POST' });
export const stopBot = () => request('/api/stop-bot', { method: 'POST' });
export const updateSettings = (brick_size) => request('/api/update-settings', { method: 'POST', body: JSON.stringify({ brick_size }) });
export const executeTrade = async (trade) => {
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
    }
    catch (error) {
        const errorMsg = error instanceof Error ? error.message : String(error);
        console.error('❌ [API] Trade execution error:', errorMsg);
        throw error;
    }
};
