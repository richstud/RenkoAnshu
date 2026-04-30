import { jsx as _jsx, jsxs as _jsxs, Fragment as _Fragment } from "react/jsx-runtime";
import { useEffect, useState, useCallback } from 'react';
const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';
export default function TradeHistory({ accountId }) {
    const [deals, setDeals] = useState([]);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);
    const [source, setSource] = useState('');
    const [days, setDays] = useState(2);
    const fetchHistory = useCallback(async () => {
        if (!accountId)
            return;
        setLoading(true);
        setError(null);
        try {
            const res = await fetch(`${API_URL}/api/mt5/history?account_id=${accountId}&days=${days}`);
            if (res.ok) {
                const data = await res.json();
                setDeals(data.data || []);
                setSource(data.source || 'mt5');
            }
            else {
                const errText = await res.text();
                setError(`Failed to load history: ${errText}`);
            }
        }
        catch (err) {
            setError('Network error loading history');
            console.error('Error fetching history:', err);
        }
        finally {
            setLoading(false);
        }
    }, [accountId, days]);
    useEffect(() => {
        fetchHistory();
    }, [fetchHistory]);
    const exportToExcel = () => {
        if (deals.length === 0)
            return;
        const headers = ['Ticket', 'Symbol', 'Type', 'Volume', 'Price', 'Profit', 'Swap', 'Commission', 'Time', 'Comment'];
        const rows = deals.map(d => [
            d.ticket ?? d.id ?? '',
            d.symbol,
            d.type.toUpperCase(),
            d.volume ?? d.lot ?? '',
            d.price ?? d.entry_price ?? '',
            d.profit,
            d.swap ?? 0,
            d.commission ?? 0,
            d.time ? new Date(d.time * 1000).toLocaleString() : (d.created_at ? new Date(d.created_at).toLocaleString() : ''),
            d.comment ?? '',
        ]);
        // Build CSV content (Excel-compatible UTF-8 BOM)
        const BOM = '\uFEFF';
        const csv = BOM + [headers, ...rows].map(row => row.map(v => `"${String(v).replace(/"/g, '""')}"`).join(',')).join('\r\n');
        const blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `trade_history_${accountId}_last${days}days.csv`;
        document.body.appendChild(a);
        a.click();
        URL.revokeObjectURL(url);
        document.body.removeChild(a);
    };
    const totalProfit = deals.reduce((sum, d) => sum + (d.profit ?? 0), 0);
    const totalSwap = deals.reduce((sum, d) => sum + (d.swap ?? 0), 0);
    const totalCommission = deals.reduce((sum, d) => sum + (d.commission ?? 0), 0);
    const getTime = (d) => d.time ? new Date(d.time * 1000).toLocaleString() : (d.created_at ? new Date(d.created_at).toLocaleString() : '—');
    return (_jsxs("div", { className: "bg-slate-800 p-4 rounded-lg", children: [_jsxs("div", { className: "flex justify-between items-center mb-4", children: [_jsx("h2", { className: "text-xl font-semibold", children: "\uD83D\uDCCA Trade History" }), _jsxs("div", { className: "flex items-center gap-2", children: [source === 'mt5' && _jsx("span", { className: "text-xs text-emerald-400 bg-emerald-900/30 px-2 py-1 rounded", children: "\u25CF MT5" }), _jsxs("select", { value: days, onChange: e => setDays(Number(e.target.value)), className: "px-2 py-1 bg-slate-700 border border-slate-600 rounded text-white text-sm", children: [_jsx("option", { value: 1, children: "Today" }), _jsx("option", { value: 2, children: "Today + Yesterday" }), _jsx("option", { value: 7, children: "Last 7 days" }), _jsx("option", { value: 30, children: "Last 30 days" })] }), _jsx("button", { onClick: fetchHistory, disabled: loading, className: "px-3 py-1 bg-blue-600 hover:bg-blue-700 disabled:bg-slate-600 rounded text-sm", children: loading ? '⟳' : 'Refresh' }), _jsx("button", { onClick: exportToExcel, disabled: deals.length === 0, className: "px-3 py-1 bg-green-600 hover:bg-green-700 disabled:bg-slate-600 rounded text-sm", children: "\uD83D\uDCE5 Excel" })] })] }), error && (_jsx("div", { className: "bg-red-900/50 border border-red-600 text-red-200 p-3 rounded mb-4 text-sm", children: error })), loading && deals.length === 0 ? (_jsx("div", { className: "text-center text-slate-400 py-8", children: "Loading history..." })) : deals.length === 0 ? (_jsxs("div", { className: "text-center text-slate-400 py-8", children: ["No closed trades in the last ", days, " day", days !== 1 ? 's' : ''] })) : (_jsxs(_Fragment, { children: [_jsxs("div", { className: "flex gap-4 mb-3 text-sm", children: [_jsxs("span", { className: `font-bold ${totalProfit >= 0 ? 'text-green-400' : 'text-red-400'}`, children: ["Net P&L: ", totalProfit >= 0 ? '+' : '', totalProfit.toFixed(2)] }), _jsxs("span", { className: "text-slate-400", children: ["Swap: ", totalSwap.toFixed(2)] }), _jsxs("span", { className: "text-slate-400", children: ["Commission: ", totalCommission.toFixed(2)] }), _jsxs("span", { className: "text-slate-400", children: [deals.length, " trades"] })] }), _jsx("div", { className: "overflow-x-auto", children: _jsxs("table", { className: "w-full text-left text-sm", children: [_jsx("thead", { children: _jsxs("tr", { className: "border-b border-slate-600 text-slate-400 text-xs", children: [_jsx("th", { className: "px-3 py-2", children: "Ticket" }), _jsx("th", { className: "px-3 py-2", children: "Symbol" }), _jsx("th", { className: "px-3 py-2", children: "Type" }), _jsx("th", { className: "px-3 py-2", children: "Vol" }), _jsx("th", { className: "px-3 py-2", children: "Price" }), _jsx("th", { className: "px-3 py-2", children: "Profit" }), _jsx("th", { className: "px-3 py-2", children: "Swap" }), _jsx("th", { className: "px-3 py-2", children: "Time" })] }) }), _jsx("tbody", { children: deals.map((deal, idx) => (_jsxs("tr", { className: "border-b border-slate-700 hover:bg-slate-700/50 text-xs", children: [_jsx("td", { className: "px-3 py-2 text-slate-400", children: deal.ticket ?? deal.id ?? '—' }), _jsx("td", { className: "px-3 py-2 font-semibold text-blue-300", children: deal.symbol }), _jsx("td", { className: "px-3 py-2", children: _jsx("span", { className: `px-2 py-0.5 rounded text-xs ${deal.type === 'buy' ? 'bg-green-900/50 text-green-300' : 'bg-red-900/50 text-red-300'}`, children: deal.type.toUpperCase() }) }), _jsx("td", { className: "px-3 py-2 text-yellow-300", children: deal.volume ?? deal.lot ?? '—' }), _jsx("td", { className: "px-3 py-2 font-mono", children: (deal.price ?? deal.entry_price ?? 0).toFixed((deal.price ?? 0) < 100 ? 5 : 2) }), _jsxs("td", { className: `px-3 py-2 font-bold font-mono ${(deal.profit ?? 0) >= 0 ? 'text-green-400' : 'text-red-400'}`, children: [(deal.profit ?? 0) >= 0 ? '+' : '', (deal.profit ?? 0).toFixed(2)] }), _jsx("td", { className: "px-3 py-2 text-slate-400 font-mono", children: (deal.swap ?? 0).toFixed(2) }), _jsx("td", { className: "px-3 py-2 text-slate-400", children: getTime(deal) })] }, deal.ticket ?? idx))) })] }) })] }))] }));
}
