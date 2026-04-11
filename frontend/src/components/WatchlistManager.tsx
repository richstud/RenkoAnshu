import { useEffect, useState } from 'react';

type WatchlistItem = {
  id: number;
  account_id: number;
  symbol: string;
  is_active: boolean;
  lot_size: number;
  stop_loss_pips: number;
  take_profit_pips: number;
  trailing_stop_pips: number;
  use_trailing_stop: boolean;
  brick_size: number;
  algo_enabled: boolean;
};

interface WatchlistManagerProps {
  accountId: number;
  onUpdate: () => void;
}

export default function WatchlistManager({ accountId, onUpdate }: WatchlistManagerProps) {
  const [watchlist, setWatchlist] = useState<WatchlistItem[]>([]);
  const [editingId, setEditingId] = useState<number | null>(null);
  const [editData, setEditData] = useState<Partial<WatchlistItem>>({});

  useEffect(() => {
    fetchWatchlist();
    // Auto-refresh every 3 seconds
    const interval = setInterval(fetchWatchlist, 3000);
    return () => clearInterval(interval);
  }, [accountId]);

  const fetchWatchlist = async () => {
    try {
      const res = await fetch(
        `${import.meta.env.VITE_API_URL || 'http://localhost:8000'}/api/watchlist?account_id=${accountId}`
      );
      if (res.ok) {
        const data = await res.json();
        setWatchlist(data.symbols || []);
      }
    } catch (error) {
      console.error('Failed to fetch watchlist:', error);
    }
  };

  const handleEdit = (item: WatchlistItem) => {
    setEditingId(item.id);
    setEditData(item);
  };

  const handleSave = async (id: number) => {
    try {
      const item = watchlist.find(w => w.id === id);
      if (!item) return;

      // Update via PUT endpoint with symbol and brick_size
      const res = await fetch(
        `${import.meta.env.VITE_API_URL || 'http://localhost:8000'}/api/watchlist/${item.symbol}?account_id=${accountId}`,
        {
          method: 'PUT',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(editData),
        }
      );

      if (res.ok) {
        setEditingId(null);
        fetchWatchlist();
        onUpdate();
      }
    } catch (error) {
      console.error('Failed to save watchlist:', error);
    }
  };

  const handleDelete = async (id: number) => {
    if (confirm('Remove from watchlist?')) {
      try {
        const item = watchlist.find(w => w.id === id);
        if (!item) return;

        const res = await fetch(
          `${import.meta.env.VITE_API_URL || 'http://localhost:8000'}/api/watchlist/${item.symbol}?account_id=${accountId}`,
          { method: 'DELETE' }
        );

        if (res.ok) {
          fetchWatchlist();
          onUpdate();
        }
      } catch (error) {
        console.error('Failed to delete from watchlist:', error);
      }
    }
  };

  const toggleAlgo = async (item: WatchlistItem) => {
    try {
      const res = await fetch(
        `${import.meta.env.VITE_API_URL || 'http://localhost:8000'}/api/watchlist/${item.symbol}/algo?account_id=${accountId}&algo_enabled=${!item.algo_enabled}`,
        {
          method: 'PUT',
          headers: { 'Content-Type': 'application/json' },
        }
      );

      if (res.ok) {
        fetchWatchlist();
        onUpdate();
      }
    } catch (error) {
      console.error('Failed to toggle algo:', error);
    }
  };

  if (watchlist.length === 0) {
    return (
      <div className="bg-slate-800 p-4 rounded-lg text-slate-400">
        No symbols in watchlist yet. Add some from the Tickers panel above.
      </div>
    );
  }

  return (
    <div className="bg-slate-800 p-4 rounded-lg">
      <h2 className="text-xl font-semibold mb-4">📋 Watchlist</h2>
      <div className="space-y-3">
        {watchlist.map((item) => (
          <div key={item.id} className="bg-slate-700 p-3 rounded border border-slate-600">
            {editingId === item.id ? (
              <div className="space-y-2">
                <div className="flex justify-between items-center mb-2">
                  <span className="font-semibold">{item.symbol}</span>
                  <button
                    onClick={() => handleSave(item.id)}
                    className="px-2 py-1 bg-green-600 hover:bg-green-700 rounded text-sm"
                  >
                    Save
                  </button>
                </div>

                <div className="grid grid-cols-2 gap-2 text-sm">
                  <div>
                    <label className="text-slate-400">SL (pips):</label>
                    <input
                      type="number"
                      value={editData.stop_loss_pips || 0}
                      onChange={(e) =>
                        setEditData({ ...editData, stop_loss_pips: parseFloat(e.target.value) })
                      }
                      className="w-full px-2 py-1 rounded bg-slate-600 text-white"
                    />
                  </div>
                  <div>
                    <label className="text-slate-400">TP (pips):</label>
                    <input
                      type="number"
                      value={editData.take_profit_pips || 0}
                      onChange={(e) =>
                        setEditData({ ...editData, take_profit_pips: parseFloat(e.target.value) })
                      }
                      className="w-full px-2 py-1 rounded bg-slate-600 text-white"
                    />
                  </div>
                  <div>
                    <label className="text-slate-400">Trailing (pips):</label>
                    <input
                      type="number"
                      value={editData.trailing_stop_pips || 0}
                      onChange={(e) =>
                        setEditData({ ...editData, trailing_stop_pips: parseFloat(e.target.value) })
                      }
                      className="w-full px-2 py-1 rounded bg-slate-600 text-white"
                    />
                  </div>
                  <div>
                    <label className="text-slate-400">Brick Size:</label>
                    <input
                      type="number"
                      value={editData.brick_size || 0}
                      onChange={(e) =>
                        setEditData({ ...editData, brick_size: parseFloat(e.target.value) })
                      }
                      className="w-full px-2 py-1 rounded bg-slate-600 text-white"
                    />
                  </div>
                  <div>
                    <label className="text-slate-400">Lot Size:</label>
                    <input
                      type="number"
                      step="0.01"
                      value={editData.lot_size || 0}
                      onChange={(e) =>
                        setEditData({ ...editData, lot_size: parseFloat(e.target.value) })
                      }
                      className="w-full px-2 py-1 rounded bg-slate-600 text-white"
                    />
                  </div>
                  <div className="flex items-center">
                    <label className="text-slate-400 mr-2">Use Trailing:</label>
                    <input
                      type="checkbox"
                      checked={editData.use_trailing_stop || false}
                      onChange={(e) =>
                        setEditData({ ...editData, use_trailing_stop: e.target.checked })
                      }
                      className="w-4 h-4"
                    />
                  </div>
                </div>
              </div>
            ) : (
              <div>
                <div className="flex justify-between items-center mb-2">
                  <div>
                    <span className="font-semibold text-lg">{item.symbol}</span>
                    <span className="ml-3 text-sm text-slate-400">
                      SL: {item.stop_loss_pips}p | TP: {item.take_profit_pips}p | Trail: {item.trailing_stop_pips}p
                    </span>
                  </div>
                  <div className="flex gap-2">
                    <button
                      onClick={() => toggleAlgo(item)}
                      className={`px-3 py-1 rounded text-sm transition ${
                        item.algo_enabled
                          ? 'bg-emerald-600 hover:bg-emerald-700'
                          : 'bg-red-600 hover:bg-red-700'
                      }`}
                    >
                      {item.algo_enabled ? '✅ ON' : '❌ OFF'}
                    </button>
                    <button
                      onClick={() => handleEdit(item)}
                      className="px-3 py-1 bg-blue-600 hover:bg-blue-700 rounded text-sm"
                    >
                      Edit
                    </button>
                    <button
                      onClick={() => handleDelete(item.id)}
                      className="px-3 py-1 bg-red-600 hover:bg-red-700 rounded text-sm"
                    >
                      Delete
                    </button>
                  </div>
                </div>
                <div className="text-xs text-slate-400 mt-1">
                  Lot: {item.lot_size} | Brick: {item.brick_size} | {item.use_trailing_stop && '📈 Trailing'}
                </div>
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}
