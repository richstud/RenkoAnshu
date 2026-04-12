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
};

interface LivePositionsProps {
  accountId: number;
}

export default function LivePositions({ accountId }: LivePositionsProps) {
  const [positions, setPositions] = useState<Position[]>([]);

  useEffect(() => {
    const fetchPositions = async () => {
      try {
        const res = await fetch(
          `${import.meta.env.VITE_API_URL || 'http://localhost:8000'}/api/trades?account_id=${accountId}`
        );
        if (res.ok) {
          const data = await res.json();
          const trades = Array.isArray(data) ? data : (data.data || []);
          const openPositions = trades.filter((trade: Position) => !trade.closed);
          setPositions(openPositions);
        }
      } catch (error) {
        console.error('Failed to fetch positions:', error);
      }
    };

    fetchPositions();
    const interval = setInterval(fetchPositions, 5000);
    return () => clearInterval(interval);
  }, [accountId]);

  if (positions.length === 0) {
    return (
      <div className="bg-slate-800 p-4 rounded-lg text-slate-400">
        No open positions
      </div>
    );
  }

  return (
    <div className="bg-slate-800 p-4 rounded-lg">
      <h2 className="text-xl font-semibold mb-4">📈 Live Positions</h2>
      <div className="space-y-2">
        {positions.map((pos) => (
          <div key={pos.id} className="bg-slate-700 p-3 rounded border border-slate-600">
            <div className="flex justify-between items-center">
              <div>
                <span className="font-semibold">{pos.symbol}</span>
                <span
                  className={`ml-2 px-2 py-1 rounded text-sm ${
                    pos.type === 'buy' ? 'bg-green-900 text-green-200' : 'bg-red-900 text-red-200'
                  }`}
                >
                  {pos.type.toUpperCase()}
                </span>
              </div>
              <div className="text-right text-sm">
                <div>Entry: {pos.entry_price.toFixed(2)}</div>
                {pos.sl_price && <div className="text-red-400">SL: {pos.sl_price.toFixed(2)}</div>}
                {pos.tp_price && <div className="text-green-400">TP: {pos.tp_price.toFixed(2)}</div>}
              </div>
            </div>
            <div className="mt-2 text-xs text-slate-300">
              <span>Lot: {pos.lot}</span>
              <span className="ml-4">Time: {new Date(pos.entry_time).toLocaleTimeString()}</span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
