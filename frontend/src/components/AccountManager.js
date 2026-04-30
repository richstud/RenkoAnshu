import { jsx as _jsx, jsxs as _jsxs, Fragment as _Fragment } from "react/jsx-runtime";
import { useState, useEffect } from 'react';
export default function AccountManager() {
    const [accounts, setAccounts] = useState([]);
    const [fetchingAccounts, setFetchingAccounts] = useState(false);
    const [connecting, setConnecting] = useState(false);
    const [disconnecting, setDisconnecting] = useState(null);
    const [error, setError] = useState(null);
    const [success, setSuccess] = useState(null);
    const [formData, setFormData] = useState({
        login: '',
        password: '',
        server: 'XMGlobal-MT5 7'
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
                const list = Array.isArray(data) ? data : (data.data || data.accounts || []);
                setAccounts(Array.isArray(list) ? list : []);
            }
            else {
                setAccounts([]);
            }
        }
        catch (err) {
            setAccounts([]);
        }
        finally {
            setFetchingAccounts(false);
        }
    };
    const handleAddAccount = async (e) => {
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
                if (data.verified === false) {
                    setSuccess(`⏳ Account ${formData.login} saved! MT5 is busy — it will connect automatically on next VPS restart.`);
                }
                else {
                    setSuccess(`✅ Account ${formData.login} connected! Balance: $${data.balance?.toFixed(2) ?? '?'}`);
                }
                setFormData({ login: '', password: '', server: formData.server });
                fetchAccounts();
                setTimeout(() => setSuccess(null), 8000);
            }
            else {
                const errData = await res.json().catch(() => ({ detail: res.statusText }));
                setError(`❌ ${errData.detail || 'Connection failed'}`);
            }
        }
        catch (err) {
            clearTimeout(slowTimer);
            if (err.name === 'AbortError') {
                setError('❌ Connection timed out (25s). Is MetaTrader 5 running on the VPS?');
            }
            else {
                setError(`❌ ${err.message || 'Connection failed'}`);
            }
        }
        finally {
            setConnecting(false);
        }
    };
    const handleDisconnect = async (login) => {
        if (!confirm(`Disconnect account ${login}? Auto-trading for this account will stop.`))
            return;
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
            }
            else {
                const errData = await res.json().catch(() => ({ detail: 'Unknown error' }));
                setError(`❌ Failed to disconnect: ${errData.detail}`);
            }
        }
        catch (err) {
            setError(`❌ ${err.message || 'Disconnect failed'}`);
        }
        finally {
            setDisconnecting(null);
        }
    };
    return (_jsx("div", { className: "space-y-6", children: _jsxs("div", { className: "bg-slate-800 p-6 rounded-lg border border-slate-700", children: [_jsx("h2", { className: "text-2xl font-bold mb-4 flex items-center gap-2", children: "\uD83D\uDD10 MT5 Account Manager" }), _jsxs("form", { onSubmit: handleAddAccount, className: "space-y-4 mb-6 p-4 bg-slate-700 rounded-lg", children: [_jsx("h3", { className: "font-semibold text-lg", children: "Link New MT5 Account" }), _jsxs("div", { className: "grid grid-cols-1 md:grid-cols-2 gap-4", children: [_jsxs("div", { children: [_jsx("label", { className: "block text-sm font-medium mb-1", children: "Account Login Number" }), _jsx("input", { type: "number", value: formData.login, onChange: (e) => setFormData({ ...formData, login: e.target.value }), placeholder: "e.g., 101510620", className: "w-full px-3 py-2 bg-slate-600 rounded border border-slate-500 text-white focus:outline-none focus:border-emerald-500", disabled: connecting })] }), _jsxs("div", { children: [_jsx("label", { className: "block text-sm font-medium mb-1", children: "Password" }), _jsx("input", { type: "password", value: formData.password, onChange: (e) => setFormData({ ...formData, password: e.target.value }), placeholder: "MT5 password", className: "w-full px-3 py-2 bg-slate-600 rounded border border-slate-500 text-white focus:outline-none focus:border-emerald-500", disabled: connecting })] }), _jsxs("div", { children: [_jsx("label", { className: "block text-sm font-medium mb-1", children: "Server" }), _jsx("input", { type: "text", value: formData.server, onChange: (e) => setFormData({ ...formData, server: e.target.value }), placeholder: "e.g., XMGlobal-MT5 6, ICMarkets-MT5", className: "w-full px-3 py-2 bg-slate-600 rounded border border-slate-500 text-white focus:outline-none focus:border-emerald-500", disabled: connecting })] }), _jsx("div", { className: "flex items-end", children: _jsx("button", { type: "submit", disabled: connecting, className: "w-full px-4 py-2 bg-blue-600 hover:bg-blue-700 disabled:bg-slate-600 rounded font-medium transition flex items-center justify-center gap-2", children: connecting ? (_jsxs(_Fragment, { children: [_jsx("span", { className: "animate-spin", children: "\u231B" }), "Connecting to MT5..."] })) : ('🔗 Link Account') }) })] }), error && (_jsx("div", { className: "p-3 bg-red-900/40 border border-red-600 rounded text-red-200 text-sm", children: error })), success && (_jsx("div", { className: "p-3 bg-green-900/40 border border-green-600 rounded text-green-200 text-sm", children: success }))] }), _jsxs("div", { className: "space-y-3", children: [_jsxs("div", { className: "flex items-center justify-between", children: [_jsx("h3", { className: "font-semibold text-lg", children: "Connected Accounts" }), _jsx("button", { onClick: fetchAccounts, disabled: fetchingAccounts, className: "text-xs text-slate-400 hover:text-white px-2 py-1 rounded border border-slate-600 hover:border-slate-400 transition", children: fetchingAccounts ? '⌛' : '🔄 Refresh' })] }), accounts.length === 0 ? (_jsx("div", { className: "text-slate-400 p-4 bg-slate-700 rounded", children: fetchingAccounts ? 'Loading accounts...' : 'No accounts linked yet. Link an MT5 account above.' })) : (_jsx("div", { className: "space-y-2", children: accounts.map((account) => (_jsxs("div", { className: "bg-slate-700 p-4 rounded border border-slate-600 flex justify-between items-center hover:border-slate-500 transition", children: [_jsxs("div", { className: "flex-1", children: [_jsxs("div", { className: "flex items-center gap-3 flex-wrap", children: [_jsx("span", { className: "text-lg font-bold font-mono", children: account.login }), _jsx("span", { className: `px-2 py-0.5 rounded text-xs font-medium ${account.status === 'active'
                                                            ? 'bg-green-900/60 text-green-300 border border-green-700'
                                                            : 'bg-red-900/40 text-red-300 border border-red-800'}`, children: account.status === 'active' ? '🟢 Active' : '🔴 Offline' }), account.balance > 0 && (_jsxs("span", { className: "text-emerald-400 text-sm font-mono font-bold", children: ["$", account.balance.toFixed(2)] }))] }), _jsxs("div", { className: "text-sm text-slate-400 mt-1", children: ["\uD83D\uDDA5\uFE0F ", account.server] })] }), _jsx("button", { onClick: () => handleDisconnect(account.login), disabled: disconnecting === account.login, className: "px-4 py-2 bg-red-700 hover:bg-red-600 disabled:bg-slate-600 rounded text-sm font-medium transition ml-4 whitespace-nowrap", children: disconnecting === account.login ? '⌛ ...' : '🔌 Disconnect' })] }, account.login))) }))] }), _jsxs("div", { className: "mt-6 p-4 bg-blue-900/30 border border-blue-700 rounded text-sm text-blue-200", children: [_jsx("p", { className: "font-semibold mb-2", children: "\u2139\uFE0F How to use:" }), _jsxs("ul", { className: "space-y-1 list-disc list-inside", children: [_jsx("li", { children: "Enter your MT5 account login, password and exact server name" }), _jsx("li", { children: "Click \"Link Account\" \u2014 MT5 terminal must be running on the VPS" }), _jsxs("li", { children: ["Once connected, go to ", _jsx("strong", { children: "Watchlist" }), " and add symbols with algo trading enabled"] }), _jsx("li", { children: "Auto-trading starts automatically within 30 seconds of adding watchlist items" }), _jsx("li", { children: "Multiple accounts trade simultaneously with separate positions" })] })] })] }) }));
}
