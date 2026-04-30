import { jsx as _jsx, jsxs as _jsxs } from "react/jsx-runtime";
import { useEffect, useState } from 'react';
export default function LivePositions({ accountId, onAccountInfo }) {
    const [positions, setPositions] = useState([]);
    const [loading, setLoading] = useState(false);
    const [source, setSource] = useState('');
    useEffect(() => {
        // Clear immediately when account changes
        setPositions([]);
        setSource('');
        setLoading(true);
        const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';
        const WS_BASE = API_URL.replace(/^https/, 'wss').replace(/^http/, 'ws');
        const url = `${WS_BASE}/ws/live`;
        let ws;
        let reconnectTimer;
        let reconnectDelay = 1000;
        const connect = () => {
            ws = new WebSocket(url);
            ws.onopen = () => {
                ws.send(JSON.stringify({ symbols: [], account_id: accountId }));
                reconnectDelay = 1000;
            };
            ws.onmessage = (event) => {
                try {
                    const data = JSON.parse(event.data);
                    if (data.positions !== undefined) {
                        setPositions(data.positions || []);
                        setSource('mt5');
                        setLoading(false);
                    }
                    if (data.account && onAccountInfo) {
                        onAccountInfo(data.account);
                    }
                }
                catch { /* ignore */ }
            };
            ws.onclose = () => {
                reconnectTimer = window.setTimeout(() => {
                    reconnectDelay = Math.min(reconnectDelay * 1.5, 8000);
                    connect();
                }, reconnectDelay);
            };
            ws.onerror = () => { };
        };
        connect();
        return () => {
            clearTimeout(reconnectTimer);
            ws?.close();
        };
    }, [accountId]);
    const getSymbol = (pos) => pos.symbol;
    const getType = (pos) => pos.type;
    const getLot = (pos) => pos.volume ?? pos.lot ?? 0;
    const getEntryPrice = (pos) => pos.open_price ?? pos.entry_price ?? 0;
    const getCurrentPrice = (pos) => pos.current_price ?? null;
    const getSL = (pos) => pos.sl ?? pos.sl_price ?? null;
    const getTP = (pos) => pos.tp ?? pos.tp_price ?? null;
    const getProfit = (pos) => pos.profit ?? null;
    const getOpenTime = (pos) => {
        if (pos.open_time)
            return new Date(pos.open_time * 1000).toLocaleString();
        if (pos.entry_time)
            return new Date(pos.entry_time).toLocaleString();
        return '—';
    };
    const getId = (pos) => pos.ticket ?? pos.id ?? Math.random();
    const totalPnL = positions.reduce((sum, p) => sum + (getProfit(p) ?? 0), 0);
    if (loading && positions.length === 0) {
        return (_jsx("div", { className: "bg-slate-800 p-4 rounded-lg text-slate-400 text-center", children: "Loading live positions..." }));
    }
    if (positions.length === 0) {
        return (_jsx("div", { className: "bg-slate-800 p-4 rounded-lg text-slate-400", children: "No open positions" }));
    }
    return (_jsxs("div", { className: "bg-slate-800 p-4 rounded-lg", children: [_jsxs("div", { className: "flex justify-between items-center mb-4", children: [_jsxs("h2", { className: "text-xl font-semibold", children: ["\uD83D\uDCC8 Live Positions (", positions.length, ")"] }), _jsxs("div", { className: "flex items-center gap-3", children: [source === 'mt5' && _jsx("span", { className: "text-xs text-emerald-400 bg-emerald-900/30 px-2 py-1 rounded", children: "\u25CF Live MT5" }), _jsxs("span", { className: `text-sm font-bold font-mono ${totalPnL >= 0 ? 'text-green-400' : 'text-red-400'}`, children: ["Total P&L: ", totalPnL >= 0 ? '+' : '', totalPnL.toFixed(2)] })] })] }), _jsx("div", { className: "overflow-x-auto", children: _jsxs("table", { className: "w-full text-left text-sm", children: [_jsx("thead", { children: _jsxs("tr", { className: "border-b border-slate-600 text-slate-400 text-xs", children: [_jsx("th", { className: "px-3 py-2", children: "Symbol" }), _jsx("th", { className: "px-3 py-2", children: "Type" }), _jsx("th", { className: "px-3 py-2", children: "Lot" }), _jsx("th", { className: "px-3 py-2", children: "Entry" }), _jsx("th", { className: "px-3 py-2", children: "Current" }), _jsx("th", { className: "px-3 py-2", children: "SL" }), _jsx("th", { className: "px-3 py-2", children: "TP" }), _jsx("th", { className: "px-3 py-2", children: "P&L" }), _jsx("th", { className: "px-3 py-2", children: "Opened" })] }) }), _jsx("tbody", { children: positions.map((pos) => {
                                const pnl = getProfit(pos);
                                return (_jsxs("tr", { className: "border-b border-slate-700 hover:bg-slate-700/50", children: [_jsx("td", { className: "px-3 py-2 font-semibold text-blue-300", children: getSymbol(pos) }), _jsx("td", { className: "px-3 py-2", children: _jsx("span", { className: `px-2 py-1 rounded text-xs font-semibold ${getType(pos) === 'buy' ? 'bg-green-900/50 text-green-300' : 'bg-red-900/50 text-red-300'}`, children: getType(pos).toUpperCase() }) }), _jsx("td", { className: "px-3 py-2 text-yellow-300", children: getLot(pos) }), _jsx("td", { className: "px-3 py-2 font-mono text-xs", children: getEntryPrice(pos).toFixed(getEntryPrice(pos) < 100 ? 5 : 2) }), _jsx("td", { className: "px-3 py-2 font-mono text-xs text-cyan-300", children: getCurrentPrice(pos) ? getCurrentPrice(pos).toFixed(getCurrentPrice(pos) < 100 ? 5 : 2) : '—' }), _jsx("td", { className: "px-3 py-2 text-red-400 font-mono text-xs", children: getSL(pos) ? getSL(pos).toFixed(getSL(pos) < 100 ? 5 : 2) : '—' }), _jsx("td", { className: "px-3 py-2 text-green-400 font-mono text-xs", children: getTP(pos) ? getTP(pos).toFixed(getTP(pos) < 100 ? 5 : 2) : '—' }), _jsx("td", { className: `px-3 py-2 font-bold font-mono text-sm ${pnl === null ? 'text-slate-400' : pnl >= 0 ? 'text-green-400' : 'text-red-400'}`, children: pnl !== null ? `${pnl >= 0 ? '+' : ''}${pnl.toFixed(2)}` : '—' }), _jsx("td", { className: "px-3 py-2 text-xs text-slate-400", children: getOpenTime(pos) })] }, getId(pos)));
                            }) })] }) })] }));
}
