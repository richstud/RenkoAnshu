import { jsx as _jsx, jsxs as _jsxs } from "react/jsx-runtime";
import { useEffect, useState } from 'react';
export default function TickersPanel({ onAddToWatchlist, watchlistSymbols }) {
    const [tickers, setTickers] = useState([]);
    const [quotes, setQuotes] = useState({});
    const [loading, setLoading] = useState(true);
    useEffect(() => {
        fetchTickers();
    }, []);
    // Fetch initial quotes via REST so they appear immediately on load
    useEffect(() => {
        if (tickers.length === 0)
            return;
        const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';
        fetch(`${API_URL}/api/tickers/quotes/batch`)
            .then(r => r.ok ? r.json() : null)
            .then(data => {
            if (data?.quotes && Object.keys(data.quotes).length > 0) {
                setQuotes(prev => ({ ...prev, ...data.quotes }));
            }
        })
            .catch(() => { });
    }, [tickers]);
    // WebSocket for real-time quotes — replaces REST polling
    useEffect(() => {
        if (tickers.length === 0)
            return;
        const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';
        const WS_BASE = API_URL.replace(/^https/, 'wss').replace(/^http/, 'ws');
        const url = `${WS_BASE}/ws/live`;
        let ws;
        let reconnectTimer;
        let reconnectDelay = 1000;
        let active = true;
        const connect = () => {
            if (!active)
                return;
            ws = new WebSocket(url);
            ws.onopen = () => {
                ws.send(JSON.stringify({ symbols: tickers.map(t => t.symbol) }));
                reconnectDelay = 1000;
            };
            ws.onmessage = (event) => {
                if (!active)
                    return;
                try {
                    const data = JSON.parse(event.data);
                    if (data.quotes && Object.keys(data.quotes).length > 0) {
                        setQuotes(prev => ({ ...prev, ...data.quotes }));
                    }
                }
                catch { /* ignore */ }
            };
            ws.onclose = () => {
                if (!active)
                    return;
                reconnectTimer = window.setTimeout(() => {
                    reconnectDelay = Math.min(reconnectDelay * 1.5, 8000);
                    connect();
                }, reconnectDelay);
            };
            ws.onerror = () => { };
        };
        connect();
        return () => {
            active = false;
            clearTimeout(reconnectTimer);
            ws?.close();
        };
    }, [tickers]);
    const fetchTickers = async () => {
        setLoading(true);
        try {
            const res = await fetch(`${import.meta.env.VITE_API_URL || 'http://localhost:8000'}/api/tickers`);
            if (res.ok) {
                const data = await res.json();
                const list = data.data || data || [];
                setTickers(Array.isArray(list) ? list : []);
            }
        }
        catch (error) {
            console.error('Failed to fetch tickers:', error);
        }
        finally {
            setLoading(false);
        }
    };
    const getSpread = (symbol) => {
        const quote = quotes[symbol];
        return quote ? (quote.ask - quote.bid).toFixed(4) : 'N/A';
    };
    const isInWatchlist = (symbol) => watchlistSymbols.includes(symbol);
    return (_jsxs("div", { className: "bg-slate-800 p-4 rounded-lg", children: [_jsx("h2", { className: "text-xl font-semibold mb-4", children: "\uD83D\uDCCA Available Tickers" }), _jsx("div", { className: "overflow-x-auto", children: _jsxs("table", { className: "w-full text-sm", children: [_jsx("thead", { children: _jsxs("tr", { className: "border-b border-slate-600", children: [_jsx("th", { className: "text-left p-2", children: "Symbol" }), _jsx("th", { className: "text-left p-2", children: "Description" }), _jsx("th", { className: "text-right p-2", children: "Bid" }), _jsx("th", { className: "text-right p-2", children: "Ask" }), _jsx("th", { className: "text-right p-2", children: "Spread" }), _jsx("th", { className: "text-center p-2", children: "Action" })] }) }), _jsx("tbody", { children: tickers.map((ticker) => {
                                const quote = quotes[ticker.symbol];
                                const inWatchlist = isInWatchlist(ticker.symbol);
                                return (_jsxs("tr", { className: "border-b border-slate-700 hover:bg-slate-700", children: [_jsx("td", { className: "p-2 font-semibold", children: ticker.symbol }), _jsx("td", { className: "p-2 text-slate-300", children: ticker.description }), _jsx("td", { className: "p-2 text-right text-red-400", children: quote ? quote.bid.toFixed(4) : '---' }), _jsx("td", { className: "p-2 text-right text-green-400", children: quote ? quote.ask.toFixed(4) : '---' }), _jsx("td", { className: "p-2 text-right text-slate-300", children: getSpread(ticker.symbol) }), _jsx("td", { className: "p-2 text-center", children: inWatchlist ? (_jsx("span", { className: "px-2 py-1 bg-emerald-600 rounded text-sm", children: "\u2705 Added" })) : (_jsx("button", { onClick: () => onAddToWatchlist(ticker.symbol), className: "px-3 py-1 bg-blue-600 hover:bg-blue-700 rounded text-sm transition", children: "Add" })) })] }, ticker.symbol));
                            }) })] }) }), _jsxs("div", { className: "mt-2 text-sm text-slate-400", children: ["Total: ", tickers.length, " symbols"] })] }));
}
