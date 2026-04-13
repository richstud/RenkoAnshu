import { useEffect, useState } from 'react';

type Position = {
  id: number;
  account_id: number;
  symbol: string;
  type: 'buy' | 'sell';
  lot: number;
  entry_price: number;
  entry_time: string;
  sl_price?: number;
  tp_price?: number;
  closed: boolean;
  brick_size?: number;
};

interface LivePositionsProps {
  accountId: number;
}

export default function LivePositions({ accountId }: LivePositionsProps) {
  const [positions, setPositions] = useState<Position[]>([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    const fetchPositions = async () => {
      try {
        setLoading(true);
        const res = await fetch(
          `${import.meta.env.VITE_API_URL || 'http://localhost:8000'}/api/trades?account_id=${accountId}&closed=false`
        );
        if (res.ok) {
          const data = await res.json();
          const trades = Array.isArray(data) ? data : (data.data || []);
          const openPositions = trades.filter((trade: Position) => !trade.closed);
          setPositions(openPositions);
        }
      } catch (error) {
        console.error('Failed to fetch positions:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchPositions();
    const interval = setInterval(fetchPositions, 5000);
    return () => clearInterval(interval);
  }, [accountId]);

  if (loading && positions.length === 0) {
    return (
      <div className="bg-slate-800 p-4 rounded-lg text-slate-400 text-center">
        Loading live positions...
      </div>
    );
  }

  if (positions.length === 0) {
    return (
      <div className="bg-slate-800 p-4 rounded-lg text-slate-400">
        No open positions
      </div>
    );
  }

  return (
    <div className="bg-slate-800 p-4 rounded-lg">
      <h2 className="text-xl font-semibold mb-4">📈 Live Positions ({positions.length})</h2>
      <div className="overflow-x-auto">
        <table className="w-full text-left text-sm">
          <thead>
            <tr className="border-b border-slate-600">
              <th className="px-3 py-2">Symbol</th>
              <th className="px-3 py-2">Type</th>
              <th className="px-3 py-2">Lot</th>
              <th className="px-3 py-2">Entry Price</th>
              <th className="px-3 py-2">SL Price</th>
              <th className="px-3 py-2">TP Price</th>
              <th className="px-3 py-2">Brick Size</th>
              <th className="px-3 py-2">Opened</th>
            </tr>
          </thead>
          <tbody>
            {positions.map((pos) => (
              <tr key={pos.id} className="border-b border-slate-700 hover:bg-slate-700/50">
                <td className="px-3 py-2 font-semibold text-blue-300">{pos.symbol}</td>
                <td className="px-3 py-2">
                  <span
                    className={`px-2 py-1 rounded text-xs font-semibold ${
                      pos.type === 'buy'
                        ? 'bg-green-900/50 text-green-300'
                        : 'bg-red-900/50 text-red-300'
                    }`}
                  >
                    {pos.type.toUpperCase()}
                  </span>
                </td>
                <td className="px-3 py-2 text-yellow-300">{pos.lot}</td>
                <td className="px-3 py-2 font-mono">{pos.entry_price.toFixed(5)}</td>
                <td className="px-3 py-2 text-red-400 font-mono">
                  {pos.sl_price ? pos.sl_price.toFixed(5) : '—'}
                </td>
                <td className="px-3 py-2 text-green-400 font-mono">
                  {pos.tp_price ? pos.tp_price.toFixed(5) : '—'}
                </td>
                <td className="px-3 py-2 text-slate-300">
                  {pos.brick_size ? pos.brick_size.toFixed(4) : '—'}
                </td>
                <td className="px-3 py-2 text-xs text-slate-400">
                  {new Date(pos.entry_time).toLocaleString()}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      <div className="mt-3 text-xs text-slate-400">
        Total: {positions.length} open trade{positions.length !== 1 ? 's' : ''}
      </div>
    </div>
  );
}
