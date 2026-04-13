import { useEffect, useState, useCallback } from 'react';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

interface Deal {
  ticket: number;
  order?: number;
  symbol: string;
  type: 'buy' | 'sell';
  volume: number;
  price: number;
  profit: number;
  swap: number;
  commission: number;
  time: number;
  comment: string;
  // DB fallback fields
  id?: number;
  lot?: number;
  entry_price?: number;
  closed?: boolean;
  created_at?: string;
  sl_price?: number;
  tp_price?: number;
}

interface TradeHistoryProps {
  accountId: number;
}

export default function TradeHistory({ accountId }: TradeHistoryProps) {
  const [deals, setDeals] = useState<Deal[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [source, setSource] = useState<string>('');
  const [days, setDays] = useState(2);

  const fetchHistory = useCallback(async () => {
    if (!accountId) return;
    setLoading(true);
    setError(null);
    try {
      const res = await fetch(`${API_URL}/api/mt5/history?account_id=${accountId}&days=${days}`);
      if (res.ok) {
        const data = await res.json();
        setDeals(data.data || []);
        setSource(data.source || 'mt5');
      } else {
        const errText = await res.text();
        setError(`Failed to load history: ${errText}`);
      }
    } catch (err) {
      setError('Network error loading history');
      console.error('Error fetching history:', err);
    } finally {
      setLoading(false);
    }
  }, [accountId, days]);

  useEffect(() => {
    fetchHistory();
  }, [fetchHistory]);

  const exportToExcel = () => {
    if (deals.length === 0) return;

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
    const csv = BOM + [headers, ...rows].map(row =>
      row.map(v => `"${String(v).replace(/"/g, '""')}"`).join(',')
    ).join('\r\n');

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

  const getTime = (d: Deal) =>
    d.time ? new Date(d.time * 1000).toLocaleString() : (d.created_at ? new Date(d.created_at).toLocaleString() : '—');

  return (
    <div className="bg-slate-800 p-4 rounded-lg">
      <div className="flex justify-between items-center mb-4">
        <h2 className="text-xl font-semibold">📊 Trade History</h2>
        <div className="flex items-center gap-2">
          {source === 'mt5' && <span className="text-xs text-emerald-400 bg-emerald-900/30 px-2 py-1 rounded">● MT5</span>}
          <select
            value={days}
            onChange={e => setDays(Number(e.target.value))}
            className="px-2 py-1 bg-slate-700 border border-slate-600 rounded text-white text-sm"
          >
            <option value={1}>Today</option>
            <option value={2}>Today + Yesterday</option>
            <option value={7}>Last 7 days</option>
            <option value={30}>Last 30 days</option>
          </select>
          <button
            onClick={fetchHistory}
            disabled={loading}
            className="px-3 py-1 bg-blue-600 hover:bg-blue-700 disabled:bg-slate-600 rounded text-sm"
          >
            {loading ? '⟳' : 'Refresh'}
          </button>
          <button
            onClick={exportToExcel}
            disabled={deals.length === 0}
            className="px-3 py-1 bg-green-600 hover:bg-green-700 disabled:bg-slate-600 rounded text-sm"
          >
            📥 Excel
          </button>
        </div>
      </div>

      {error && (
        <div className="bg-red-900/50 border border-red-600 text-red-200 p-3 rounded mb-4 text-sm">
          {error}
        </div>
      )}

      {loading && deals.length === 0 ? (
        <div className="text-center text-slate-400 py-8">Loading history...</div>
      ) : deals.length === 0 ? (
        <div className="text-center text-slate-400 py-8">No closed trades in the last {days} day{days !== 1 ? 's' : ''}</div>
      ) : (
        <>
          <div className="flex gap-4 mb-3 text-sm">
            <span className={`font-bold ${totalProfit >= 0 ? 'text-green-400' : 'text-red-400'}`}>
              Net P&L: {totalProfit >= 0 ? '+' : ''}{totalProfit.toFixed(2)}
            </span>
            <span className="text-slate-400">Swap: {totalSwap.toFixed(2)}</span>
            <span className="text-slate-400">Commission: {totalCommission.toFixed(2)}</span>
            <span className="text-slate-400">{deals.length} trades</span>
          </div>
          <div className="overflow-x-auto">
            <table className="w-full text-left text-sm">
              <thead>
                <tr className="border-b border-slate-600 text-slate-400 text-xs">
                  <th className="px-3 py-2">Ticket</th>
                  <th className="px-3 py-2">Symbol</th>
                  <th className="px-3 py-2">Type</th>
                  <th className="px-3 py-2">Vol</th>
                  <th className="px-3 py-2">Price</th>
                  <th className="px-3 py-2">Profit</th>
                  <th className="px-3 py-2">Swap</th>
                  <th className="px-3 py-2">Time</th>
                </tr>
              </thead>
              <tbody>
                {deals.map((deal, idx) => (
                  <tr key={deal.ticket ?? idx} className="border-b border-slate-700 hover:bg-slate-700/50 text-xs">
                    <td className="px-3 py-2 text-slate-400">{deal.ticket ?? deal.id ?? '—'}</td>
                    <td className="px-3 py-2 font-semibold text-blue-300">{deal.symbol}</td>
                    <td className="px-3 py-2">
                      <span className={`px-2 py-0.5 rounded text-xs ${deal.type === 'buy' ? 'bg-green-900/50 text-green-300' : 'bg-red-900/50 text-red-300'}`}>
                        {deal.type.toUpperCase()}
                      </span>
                    </td>
                    <td className="px-3 py-2 text-yellow-300">{deal.volume ?? deal.lot ?? '—'}</td>
                    <td className="px-3 py-2 font-mono">{(deal.price ?? deal.entry_price ?? 0).toFixed((deal.price ?? 0) < 100 ? 5 : 2)}</td>
                    <td className={`px-3 py-2 font-bold font-mono ${(deal.profit ?? 0) >= 0 ? 'text-green-400' : 'text-red-400'}`}>
                      {(deal.profit ?? 0) >= 0 ? '+' : ''}{(deal.profit ?? 0).toFixed(2)}
                    </td>
                    <td className="px-3 py-2 text-slate-400 font-mono">{(deal.swap ?? 0).toFixed(2)}</td>
                    <td className="px-3 py-2 text-slate-400">{getTime(deal)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </>
      )}
    </div>
  );
}
