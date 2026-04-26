import { useEffect, useState } from 'react';

type Ticker = {
  id: number;
  symbol: string;
  description: string;
  pip_value: number;
  is_active: boolean;
};

type Quote = {
  symbol: string;
  bid: number;
  ask: number;
  last_update: number;
};

interface TickersPanelProps {
  onAddToWatchlist: (symbol: string) => void;
  watchlistSymbols: string[];
}

export default function TickersPanel({ onAddToWatchlist, watchlistSymbols }: TickersPanelProps) {
  const [tickers, setTickers] = useState<Ticker[]>([]);
  const [quotes, setQuotes] = useState<Record<string, Quote>>({});
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchTickers();
  }, []);

  // Fetch initial quotes via REST so they appear immediately on load
  useEffect(() => {
    if (tickers.length === 0) return;
    const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';
    fetch(`${API_URL}/api/tickers/quotes/batch`)
      .then(r => r.ok ? r.json() : null)
      .then(data => {
        if (data?.quotes && Object.keys(data.quotes).length > 0) {
          setQuotes(prev => ({ ...prev, ...data.quotes }));
        }
      })
      .catch(() => {});
  }, [tickers]);

  // WebSocket for real-time quotes — replaces REST polling
  useEffect(() => {
    if (tickers.length === 0) return;

    const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';
    const WS_BASE = API_URL.replace(/^https/, 'wss').replace(/^http/, 'ws');
    const url = `${WS_BASE}/ws/live`;
    let ws: WebSocket;
    let reconnectTimer: number;
    let reconnectDelay = 1000;
    let active = true;

    const connect = () => {
      if (!active) return;
      ws = new WebSocket(url);

      ws.onopen = () => {
        ws.send(JSON.stringify({ symbols: tickers.map(t => t.symbol) }));
        reconnectDelay = 1000;
      };

      ws.onmessage = (event) => {
        if (!active) return;
        try {
          const data = JSON.parse(event.data);
          if (data.quotes && Object.keys(data.quotes).length > 0) {
            setQuotes(prev => ({ ...prev, ...data.quotes }));
          }
        } catch { /* ignore */ }
      };

      ws.onclose = () => {
        if (!active) return;
        reconnectTimer = window.setTimeout(() => {
          reconnectDelay = Math.min(reconnectDelay * 1.5, 8000);
          connect();
        }, reconnectDelay);
      };

      ws.onerror = () => { /* onclose handles reconnect */ };
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
    } catch (error) {
      console.error('Failed to fetch tickers:', error);
    } finally {
      setLoading(false);
    }
  };

  const getSpread = (symbol: string) => {
    const quote = quotes[symbol];
    return quote ? (quote.ask - quote.bid).toFixed(4) : 'N/A';
  };

  const isInWatchlist = (symbol: string) => watchlistSymbols.includes(symbol);

  return (
    <div className="bg-slate-800 p-4 rounded-lg">
      <h2 className="text-xl font-semibold mb-4">📊 Available Tickers</h2>
      <div className="overflow-x-auto">
        <table className="w-full text-sm">
          <thead>
            <tr className="border-b border-slate-600">
              <th className="text-left p-2">Symbol</th>
              <th className="text-left p-2">Description</th>
              <th className="text-right p-2">Bid</th>
              <th className="text-right p-2">Ask</th>
              <th className="text-right p-2">Spread</th>
              <th className="text-center p-2">Action</th>
            </tr>
          </thead>
          <tbody>
            {tickers.map((ticker) => {
              const quote = quotes[ticker.symbol];
              const inWatchlist = isInWatchlist(ticker.symbol);
              
              return (
                <tr key={ticker.symbol} className="border-b border-slate-700 hover:bg-slate-700">
                  <td className="p-2 font-semibold">{ticker.symbol}</td>
                  <td className="p-2 text-slate-300">{ticker.description}</td>
                  <td className="p-2 text-right text-red-400">
                    {quote ? quote.bid.toFixed(4) : '---'}
                  </td>
                  <td className="p-2 text-right text-green-400">
                    {quote ? quote.ask.toFixed(4) : '---'}
                  </td>
                  <td className="p-2 text-right text-slate-300">
                    {getSpread(ticker.symbol)}
                  </td>
                  <td className="p-2 text-center">
                    {inWatchlist ? (
                      <span className="px-2 py-1 bg-emerald-600 rounded text-sm">✅ Added</span>
                    ) : (
                      <button
                        onClick={() => onAddToWatchlist(ticker.symbol)}
                        className="px-3 py-1 bg-blue-600 hover:bg-blue-700 rounded text-sm transition"
                      >
                        Add
                      </button>
                    )}
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
      <div className="mt-2 text-sm text-slate-400">
        Total: {tickers.length} symbols
      </div>
    </div>
  );
}
