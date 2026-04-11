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
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);

  // Form state for adding account
  const [formData, setFormData] = useState({
    login: '',
    password: '',
    server: 'ICMarkets'
  });

  const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

  // Fetch connected accounts
  useEffect(() => {
    fetchAccounts();
  }, []);

  const fetchAccounts = async () => {
    try {
      setLoading(true);
      const res = await fetch(`${API_URL}/api/accounts`);
      if (res.ok) {
        const data = await res.json();
        setAccounts(data || []);
      }
    } catch (err) {
      setError('Failed to fetch accounts');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleAddAccount = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!formData.login || !formData.password || !formData.server) {
      setError('Please fill all fields');
      return;
    }

    try {
      setLoading(true);
      setError(null);
      setSuccess(null);

      const res = await fetch(`${API_URL}/api/connect-account`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          login: parseInt(formData.login),
          password: formData.password,
          server: formData.server
        })
      });

      if (res.ok) {
        const data = await res.json();
        setSuccess(`✅ Account ${formData.login} connected successfully!`);
        setFormData({ login: '', password: '', server: 'ICMarkets' });
        fetchAccounts(); // Refresh list
        setTimeout(() => setSuccess(null), 3000);
      } else {
        const errorData = await res.json();
        setError(`❌ Failed: ${errorData.detail || 'Unknown error'}`);
      }
    } catch (err) {
      setError('Connection failed');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleRemoveAccount = async (login: number) => {
    if (!confirm(`Remove account ${login}?`)) return;

    try {
      setLoading(true);
      const res = await fetch(`${API_URL}/api/disconnect-account`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ login })
      });

      if (res.ok) {
        setSuccess(`✅ Account ${login} disconnected`);
        fetchAccounts();
        setTimeout(() => setSuccess(null), 3000);
      } else {
        setError('Failed to remove account');
      }
    } catch (err) {
      setError('Disconnection failed');
      console.error(err);
    } finally {
      setLoading(false);
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
                className="w-full px-3 py-2 bg-slate-600 rounded border border-slate-500 text-white"
                disabled={loading}
              />
            </div>

            <div>
              <label className="block text-sm font-medium mb-1">Password</label>
              <input
                type="password"
                value={formData.password}
                onChange={(e) => setFormData({ ...formData, password: e.target.value })}
                placeholder="MT5 password"
                className="w-full px-3 py-2 bg-slate-600 rounded border border-slate-500 text-white"
                disabled={loading}
              />
            </div>

            <div>
              <label className="block text-sm font-medium mb-1">Server</label>
              <select
                value={formData.server}
                onChange={(e) => setFormData({ ...formData, server: e.target.value })}
                className="w-full px-3 py-2 bg-slate-600 rounded border border-slate-500 text-white"
                disabled={loading}
              >
                <option value="ICMarkets">ICMarkets</option>
                <option value="ICMarkets-MT5">ICMarkets-MT5</option>
                <option value="XM.MT5">XM.MT5</option>
                <option value="FXPro.MT5">FXPro.MT5</option>
              </select>
            </div>

            <div className="flex items-end">
              <button
                type="submit"
                disabled={loading}
                className="w-full px-4 py-2 bg-blue-600 hover:bg-blue-700 disabled:bg-gray-600 rounded font-medium transition"
              >
                {loading ? 'Connecting...' : 'Link Account'}
              </button>
            </div>
          </div>

          {error && (
            <div className="p-3 bg-red-900/30 border border-red-700 rounded text-red-200 text-sm">
              {error}
            </div>
          )}

          {success && (
            <div className="p-3 bg-green-900/30 border border-green-700 rounded text-green-200 text-sm">
              {success}
            </div>
          )}
        </form>

        {/* Connected Accounts List */}
        <div className="space-y-3">
          <h3 className="font-semibold text-lg">Connected Accounts</h3>
          
          {loading && accounts.length === 0 ? (
            <div className="text-slate-400">Loading accounts...</div>
          ) : accounts.length === 0 ? (
            <div className="text-slate-400 p-4 bg-slate-700 rounded">
              No accounts connected yet. Link an MT5 account above.
            </div>
          ) : (
            <div className="space-y-2">
              {accounts.map((account) => (
                <div
                  key={account.login}
                  className="bg-slate-700 p-4 rounded border border-slate-600 flex justify-between items-center hover:border-slate-500 transition"
                >
                  <div className="flex-1">
                    <div className="flex items-center gap-2">
                      <span className="text-lg font-bold">{account.login}</span>
                      <span
                        className={`px-2 py-1 rounded text-xs font-medium ${
                          account.status === 'active'
                            ? 'bg-green-900/50 text-green-300'
                            : 'bg-red-900/50 text-red-300'
                        }`}
                      >
                        {account.status === 'active' ? '✅ Active' : '❌ Offline'}
                      </span>
                    </div>
                    <div className="text-sm text-slate-400 mt-1">
                      Server: {account.server}
                      {account.balance && (
                        <>
                          {' | '}💰 Balance: ${account.balance.toFixed(2)}
                        </>
                      )}
                    </div>
                  </div>

                  <button
                    onClick={() => handleRemoveAccount(account.login)}
                    disabled={loading}
                    className="px-4 py-2 bg-red-600 hover:bg-red-700 disabled:bg-gray-600 rounded text-sm font-medium transition ml-4"
                  >
                    Unlink
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
            <li>Enter your MT5 account login number and password</li>
            <li>Select the MT5 server</li>
            <li>Click "Link Account"</li>
            <li>Once connected, you can enable auto-trading for this account</li>
            <li>Multiple accounts can be linked to trade simultaneously</li>
          </ul>
        </div>
      </div>
    </div>
  );
}
