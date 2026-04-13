import { useEffect, useState } from 'react';

interface Trade {
  id: number;
  account_id: number;
  symbol: string;
  type: 'buy' | 'sell';
  lot: number;
  entry_price: number;
  sl_price?: number;
  tp_price?: number;
  closed: boolean;
  created_at: string;
  brick_size: number;
}

interface TradeHistoryProps {
  accountId: number;
}

export default function TradeHistory({ accountId }: TradeHistoryProps) {
  const [trades, setTrades] = useState<Trade[]>([]);
  const [selectedDate, setSelectedDate] = useState<string>(new Date().toISOString().split('T')[0]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchTradesByDate = async () => {
    if (!accountId || !selectedDate) return;
    
    setLoading(true);
    setError(null);
    
    try {
      const res = await fetch(
        `${import.meta.env.VITE_API_URL || 'http://localhost:8000'}/api/trades/by-date/${accountId}?date_str=${selectedDate}`
      );
      
      if (res.ok) {
        const data = await res.json();
        setTrades(data.data || []);
      } else {
        setError('Failed to fetch trades');
      }
    } catch (err) {
      console.error('Error fetching trades:', err);
      setError('Error fetching trades');
    } finally {
      setLoading(false);
    }
  };

  const exportToCSV = async () => {
    if (!accountId || !selectedDate) return;
    
    try {
      const res = await fetch(
        `${import.meta.env.VITE_API_URL || 'http://localhost:8000'}/api/trades/export/${accountId}?date_str=${selectedDate}`
      );
      
      if (res.ok) {
        const blob = await res.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `trades_${selectedDate}_${accountId}.csv`;
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
        document.body.removeChild(a);
      } else {
        alert('Failed to export trades');
      }
    } catch (err) {
      console.error('Error exporting trades:', err);
      alert('Error exporting trades');
    }
  };

  useEffect(() => {
    fetchTradesByDate();
  }, [accountId, selectedDate]);

  return (
    <div className="bg-slate-800 p-4 rounded-lg">
      <h2 className="text-xl font-semibold mb-4">📊 Trade History</h2>
      
      <div className="flex gap-4 mb-4">
        <div>
          <label className="text-sm text-slate-400 block mb-1">Date</label>
          <input
            type="date"
            value={selectedDate}
            onChange={(e) => setSelectedDate(e.target.value)}
            className="px-3 py-2 bg-slate-700 border border-slate-600 rounded text-white text-sm"
          />
        </div>
        <div className="flex items-end gap-2">
          <button
            onClick={fetchTradesByDate}
            disabled={loading}
            className="px-4 py-2 bg-blue-600 hover:bg-blue-700 disabled:bg-slate-600 rounded text-sm"
          >
            {loading ? 'Loading...' : 'Load Trades'}
          </button>
          <button
            onClick={exportToCSV}
            disabled={loading || trades.length === 0}
            className="px-4 py-2 bg-green-600 hover:bg-green-700 disabled:bg-slate-600 rounded text-sm"
          >
            📥 Export CSV
          </button>
        </div>
      </div>

      {error && (
        <div className="bg-red-900/50 border border-red-600 text-red-200 p-3 rounded mb-4">
          {error}
        </div>
      )}

      {trades.length === 0 ? (
        <div className="bg-slate-700 p-4 rounded text-slate-400 text-center">
          No trades found for {selectedDate}
        </div>
      ) : (
        <div className="overflow-x-auto">
          <table className="w-full text-left text-sm">
            <thead>
              <tr className="border-b border-slate-600">
                <th className="px-3 py-2">Symbol</th>
                <th className="px-3 py-2">Type</th>
                <th className="px-3 py-2">Lot</th>
                <th className="px-3 py-2">Entry Price</th>
                <th className="px-3 py-2">SL</th>
                <th className="px-3 py-2">TP</th>
                <th className="px-3 py-2">Status</th>
                <th className="px-3 py-2">Time</th>
              </tr>
            </thead>
            <tbody>
              {trades.map((trade) => (
                <tr key={trade.id} className="border-b border-slate-700 hover:bg-slate-700">
                  <td className="px-3 py-2 font-semibold">{trade.symbol}</td>
                  <td className="px-3 py-2">
                    <span
                      className={`px-2 py-1 rounded text-xs ${
                        trade.type === 'buy'
                          ? 'bg-green-900/50 text-green-300'
                          : 'bg-red-900/50 text-red-300'
                      }`}
                    >
                      {trade.type.toUpperCase()}
                    </span>
                  </td>
                  <td className="px-3 py-2">{trade.lot}</td>
                  <td className="px-3 py-2">{trade.entry_price.toFixed(5)}</td>
                  <td className="px-3 py-2 text-red-400">
                    {trade.sl_price?.toFixed(5) || '—'}
                  </td>
                  <td className="px-3 py-2 text-green-400">
                    {trade.tp_price?.toFixed(5) || '—'}
                  </td>
                  <td className="px-3 py-2">
                    <span
                      className={`text-xs px-2 py-1 rounded ${
                        trade.closed
                          ? 'bg-slate-600 text-slate-300'
                          : 'bg-emerald-900/50 text-emerald-300'
                      }`}
                    >
                      {trade.closed ? 'Closed' : 'Open'}
                    </span>
                  </td>
                  <td className="px-3 py-2 text-xs text-slate-400">
                    {new Date(trade.created_at).toLocaleTimeString()}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
          <div className="mt-3 text-sm text-slate-400">
            Total: {trades.length} trades
          </div>
        </div>
      )}
    </div>
  );
}
