import { useEffect, useState } from 'react';

type Position = {
  ticket?: number;
  id?: number;
  symbol: string;
  type: 'buy' | 'sell';
  volume?: number;
  lot?: number;
  open_price?: number;
  entry_price?: number;
  current_price?: number;
  sl?: number;
  sl_price?: number;
  tp?: number;
  tp_price?: number;
  profit?: number;
  swap?: number;
  commission?: number;
  open_time?: number;
  entry_time?: string;
  brick_size?: number;
};

interface LivePositionsProps {
  accountId: number;
}

export default function LivePositions({ accountId }: LivePositionsProps) {
  const [positions, setPositions] = useState<Position[]>([]);
  const [loading, setLoading] = useState(false);
  const [source, setSource] = useState<string>('');

  useEffect(() => {
    const fetchPositions = async () => {
      try {
        setLoading(true);
        // Try MT5 direct positions first (has real PnL)
        const res = await fetch(
          `${import.meta.env.VITE_API_URL || 'http://localhost:8000'}/api/mt5/positions?account_id=${accountId}`
        );
        if (res.ok) {
          const data = await res.json();
          setPositions(data.data || []);
          setSource(data.source || 'mt5');
        }
      } catch (error) {
        console.error('Failed to fetch positions:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchPositions();
    const interval = setInterval(fetchPositions, 3000); // Refresh every 3s for live PnL
    return () => clearInterval(interval);
  }, [accountId]);

  const getSymbol = (pos: Position) => pos.symbol;
  const getType = (pos: Position) => pos.type;
  const getLot = (pos: Position) => pos.volume ?? pos.lot ?? 0;
  const getEntryPrice = (pos: Position) => pos.open_price ?? pos.entry_price ?? 0;
  const getCurrentPrice = (pos: Position) => pos.current_price ?? null;
  const getSL = (pos: Position) => pos.sl ?? pos.sl_price ?? null;
  const getTP = (pos: Position) => pos.tp ?? pos.tp_price ?? null;
  const getProfit = (pos: Position) => pos.profit ?? null;
  const getOpenTime = (pos: Position) => {
    if (pos.open_time) return new Date(pos.open_time * 1000).toLocaleString();
    if (pos.entry_time) return new Date(pos.entry_time).toLocaleString();
    return '—';
  };
  const getId = (pos: Position) => pos.ticket ?? pos.id ?? Math.random();

  const totalPnL = positions.reduce((sum, p) => sum + (getProfit(p) ?? 0), 0);

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
      <div className="flex justify-between items-center mb-4">
        <h2 className="text-xl font-semibold">📈 Live Positions ({positions.length})</h2>
        <div className="flex items-center gap-3">
          {source === 'mt5' && <span className="text-xs text-emerald-400 bg-emerald-900/30 px-2 py-1 rounded">● Live MT5</span>}
          <span className={`text-sm font-bold font-mono ${totalPnL >= 0 ? 'text-green-400' : 'text-red-400'}`}>
            Total P&L: {totalPnL >= 0 ? '+' : ''}{totalPnL.toFixed(2)}
          </span>
        </div>
      </div>
      <div className="overflow-x-auto">
        <table className="w-full text-left text-sm">
          <thead>
            <tr className="border-b border-slate-600 text-slate-400 text-xs">
              <th className="px-3 py-2">Symbol</th>
              <th className="px-3 py-2">Type</th>
              <th className="px-3 py-2">Lot</th>
              <th className="px-3 py-2">Entry</th>
              <th className="px-3 py-2">Current</th>
              <th className="px-3 py-2">SL</th>
              <th className="px-3 py-2">TP</th>
              <th className="px-3 py-2">P&L</th>
              <th className="px-3 py-2">Opened</th>
            </tr>
          </thead>
          <tbody>
            {positions.map((pos) => {
              const pnl = getProfit(pos);
              return (
                <tr key={getId(pos)} className="border-b border-slate-700 hover:bg-slate-700/50">
                  <td className="px-3 py-2 font-semibold text-blue-300">{getSymbol(pos)}</td>
                  <td className="px-3 py-2">
                    <span className={`px-2 py-1 rounded text-xs font-semibold ${getType(pos) === 'buy' ? 'bg-green-900/50 text-green-300' : 'bg-red-900/50 text-red-300'}`}>
                      {getType(pos).toUpperCase()}
                    </span>
                  </td>
                  <td className="px-3 py-2 text-yellow-300">{getLot(pos)}</td>
                  <td className="px-3 py-2 font-mono text-xs">{getEntryPrice(pos).toFixed(getEntryPrice(pos) < 100 ? 5 : 2)}</td>
                  <td className="px-3 py-2 font-mono text-xs text-cyan-300">
                    {getCurrentPrice(pos) ? getCurrentPrice(pos)!.toFixed(getCurrentPrice(pos)! < 100 ? 5 : 2) : '—'}
                  </td>
                  <td className="px-3 py-2 text-red-400 font-mono text-xs">
                    {getSL(pos) ? getSL(pos)!.toFixed(getSL(pos)! < 100 ? 5 : 2) : '—'}
                  </td>
                  <td className="px-3 py-2 text-green-400 font-mono text-xs">
                    {getTP(pos) ? getTP(pos)!.toFixed(getTP(pos)! < 100 ? 5 : 2) : '—'}
                  </td>
                  <td className={`px-3 py-2 font-bold font-mono text-sm ${pnl === null ? 'text-slate-400' : pnl >= 0 ? 'text-green-400' : 'text-red-400'}`}>
                    {pnl !== null ? `${pnl >= 0 ? '+' : ''}${pnl.toFixed(2)}` : '—'}
                  </td>
                  <td className="px-3 py-2 text-xs text-slate-400">{getOpenTime(pos)}</td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
    </div>
  );
}

