import { useState, useEffect } from 'react';

interface Account {
  id: number;
  login: number;
  server: string;
  status: string;
  balance: number;
}

export default function AccountManager() {
  const [accounts, setAccounts] = useState<Account[]>([]);
  const [fetchingAccounts, setFetchingAccounts] = useState(false);
  const [connecting, setConnecting] = useState(false);
  const [disconnecting, setDisconnecting] = useState<number | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);

  const [formData, setFormData] = useState({
    login: '',
    password: '',
    server: 'XMGlobal-MT5 6'
  });

  const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

  useEffect(() => {
    fetchAccounts();
    const interval = setInterval(fetchAccounts, 15000); // refresh every 15s
    return () => clearInterval(interval);
  }, []);

  const fetchAccounts = async () => {
    try {
      setFetchingAccounts(true);
      const res = await fetch(`${API_URL}/api/accounts`);
      if (res.ok) {
        const data = await res.json();
        const list = Array.isArray(data) ? data : (data.accounts || []);
        setAccounts(Array.isArray(list) ? list : []);
      } else {
        setAccounts([]);
      }
    } catch (err) {
      setAccounts([]);
    } finally {
      setFetchingAccounts(false);
    }
  };

  const handleAddAccount = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!formData.login || !formData.password || !formData.server) {
      setError('Please fill all fields');
      return;
    }

    setConnecting(true);
    setError(null);
    setSuccess(null);

    // Timeout to show helpful message if MT5 is slow
    const slowTimer = setTimeout(() => {
      setError('⏳ MT5 is taking longer than usual. Ensure MetaTrader 5 is running on VPS...');
    }, 8000);

    try {
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), 25000);

      const res = await fetch(`${API_URL}/api/connect-account`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          login: parseInt(formData.login),
          password: formData.password,
          server: formData.server
        }),
        signal: controller.signal
      });

      clearTimeout(timeoutId);
      clearTimeout(slowTimer);

      if (res.ok) {
        const data = await res.json();
        setSuccess(`✅ Account ${formData.login} connected! Balance: $${data.balance?.toFixed(2) ?? '?'}`);
        setFormData({ login: '', password: '', server: formData.server });
        fetchAccounts();
        setTimeout(() => setSuccess(null), 5000);
      } else {
        const errData = await res.json().catch(() => ({ detail: res.statusText }));
        setError(`❌ ${errData.detail || 'Connection failed'}`);
      }
    } catch (err: any) {
      clearTimeout(slowTimer);
      if (err.name === 'AbortError') {
        setError('❌ Connection timed out (25s). Is MetaTrader 5 running on the VPS?');
      } else {
        setError(`❌ ${err.message || 'Connection failed'}`);
      }
    } finally {
      setConnecting(false);
    }
  };

  const handleDisconnect = async (login: number) => {
    if (!confirm(`Disconnect account ${login}? Auto-trading for this account will stop.`)) return;

    setDisconnecting(login);
    setError(null);

    try {
      const res = await fetch(`${API_URL}/api/disconnect-account`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ login })
      });

      if (res.ok) {
        setSuccess(`✅ Account ${login} disconnected`);
        setAccounts(prev => prev.filter(a => a.login !== login));
        setTimeout(() => setSuccess(null), 3000);
      } else {
        const errData = await res.json().catch(() => ({ detail: 'Unknown error' }));
        setError(`❌ Failed to disconnect: ${errData.detail}`);
      }
    } catch (err: any) {
      setError(`❌ ${err.message || 'Disconnect failed'}`);
    } finally {
      setDisconnecting(null);
    }
  };

  return (
    <div className="space-y-6">
      <div className="bg-slate-800 p-6 rounded-lg border border-slate-700">
        <h2 className="text-2xl font-bold mb-4 flex items-center gap-2">
          🔐 MT5 Account Manager
        </h2>

        {/* Add Account Form */}
        <form onSubmit={handleAddAccount} className="space-y-4 mb-6 p-4 bg-slate-700 rounded-lg">
          <h3 className="font-semibold text-lg">Link New MT5 Account</h3>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium mb-1">Account Login Number</label>
              <input
                type="number"
                value={formData.login}
                onChange={(e) => setFormData({ ...formData, login: e.target.value })}
                placeholder="e.g., 101510620"
                className="w-full px-3 py-2 bg-slate-600 rounded border border-slate-500 text-white focus:outline-none focus:border-emerald-500"
                disabled={connecting}
              />
            </div>

            <div>
              <label className="block text-sm font-medium mb-1">Password</label>
              <input
                type="password"
                value={formData.password}
                onChange={(e) => setFormData({ ...formData, password: e.target.value })}
                placeholder="MT5 password"
                className="w-full px-3 py-2 bg-slate-600 rounded border border-slate-500 text-white focus:outline-none focus:border-emerald-500"
                disabled={connecting}
              />
            </div>

            <div>
              <label className="block text-sm font-medium mb-1">Server</label>
              <input
                type="text"
                value={formData.server}
                onChange={(e) => setFormData({ ...formData, server: e.target.value })}
                placeholder="e.g., XMGlobal-MT5 6, ICMarkets-MT5"
                className="w-full px-3 py-2 bg-slate-600 rounded border border-slate-500 text-white focus:outline-none focus:border-emerald-500"
                disabled={connecting}
              />
            </div>

            <div className="flex items-end">
              <button
                type="submit"
                disabled={connecting}
                className="w-full px-4 py-2 bg-blue-600 hover:bg-blue-700 disabled:bg-slate-600 rounded font-medium transition flex items-center justify-center gap-2"
              >
                {connecting ? (
                  <>
                    <span className="animate-spin">⌛</span>
                    Connecting to MT5...
                  </>
                ) : (
                  '🔗 Link Account'
                )}
              </button>
            </div>
          </div>

          {error && (
            <div className="p-3 bg-red-900/40 border border-red-600 rounded text-red-200 text-sm">
              {error}
            </div>
          )}
          {success && (
            <div className="p-3 bg-green-900/40 border border-green-600 rounded text-green-200 text-sm">
              {success}
            </div>
          )}
        </form>

        {/* Connected Accounts List */}
        <div className="space-y-3">
          <div className="flex items-center justify-between">
            <h3 className="font-semibold text-lg">Connected Accounts</h3>
            <button
              onClick={fetchAccounts}
              disabled={fetchingAccounts}
              className="text-xs text-slate-400 hover:text-white px-2 py-1 rounded border border-slate-600 hover:border-slate-400 transition"
            >
              {fetchingAccounts ? '⌛' : '🔄 Refresh'}
            </button>
          </div>

          {accounts.length === 0 ? (
            <div className="text-slate-400 p-4 bg-slate-700 rounded">
              {fetchingAccounts ? 'Loading accounts...' : 'No accounts linked yet. Link an MT5 account above.'}
            </div>
          ) : (
            <div className="space-y-2">
              {accounts.map((account) => (
                <div
                  key={account.login}
                  className="bg-slate-700 p-4 rounded border border-slate-600 flex justify-between items-center hover:border-slate-500 transition"
                >
                  <div className="flex-1">
                    <div className="flex items-center gap-3 flex-wrap">
                      <span className="text-lg font-bold font-mono">{account.login}</span>
                      <span className={`px-2 py-0.5 rounded text-xs font-medium ${
                        account.status === 'active'
                          ? 'bg-green-900/60 text-green-300 border border-green-700'
                          : 'bg-red-900/40 text-red-300 border border-red-800'
                      }`}>
                        {account.status === 'active' ? '🟢 Active' : '🔴 Offline'}
                      </span>
                      {account.balance > 0 && (
                        <span className="text-emerald-400 text-sm font-mono font-bold">
                          ${account.balance.toFixed(2)}
                        </span>
                      )}
                    </div>
                    <div className="text-sm text-slate-400 mt-1">
                      🖥️ {account.server}
                    </div>
                  </div>

                  <button
                    onClick={() => handleDisconnect(account.login)}
                    disabled={disconnecting === account.login}
                    className="px-4 py-2 bg-red-700 hover:bg-red-600 disabled:bg-slate-600 rounded text-sm font-medium transition ml-4 whitespace-nowrap"
                  >
                    {disconnecting === account.login ? '⌛ ...' : '🔌 Disconnect'}
                  </button>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Info Box */}
        <div className="mt-6 p-4 bg-blue-900/30 border border-blue-700 rounded text-sm text-blue-200">
          <p className="font-semibold mb-2">ℹ️ How to use:</p>
          <ul className="space-y-1 list-disc list-inside">
            <li>Enter your MT5 account login, password and exact server name</li>
            <li>Click "Link Account" — MT5 terminal must be running on the VPS</li>
            <li>Once connected, go to <strong>Watchlist</strong> and add symbols with algo trading enabled</li>
            <li>Auto-trading starts automatically within 30 seconds of adding watchlist items</li>
            <li>Multiple accounts trade simultaneously with separate positions</li>
          </ul>
        </div>
      </div>
    </div>
  );
}

