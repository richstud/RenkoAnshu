import { useEffect, useState } from 'react';
import { getAccounts, getTrades, startBot, stopBot, updateSettings } from './services/api';
import AccountsPanel from './components/AccountsPanel';
import TradeDashboard from './components/TradeDashboard';
import Controls from './components/Controls';
import LogsViewer from './components/LogsViewer';
import TickersPanel from './components/TickersPanel';
import WatchlistManager from './components/WatchlistManager';
import LivePositions from './components/LivePositions';
import TradeExecutor from './components/TradeExecutor';
import { useWebSocket } from './hooks/useWebSocket';

export type Trade = { id: number; account_id: number; symbol: string; type: string; lot: number; entry_price: number; exit_price?: number; profit?: number; timestamp: string };
export type Account = { id: number; login: number; server: string; status: string };

function App() {
  const [accounts, setAccounts] = useState<Account[]>([]);
  const [selectedAccount, setSelectedAccount] = useState<Account | null>(null);
  const [trades, setTrades] = useState<Trade[]>([]);
  const [watchlistSymbols, setWatchlistSymbols] = useState<string[]>([]);
  const [watchlistRefresh, setWatchlistRefresh] = useState(0);
  const [loading, setLoading] = useState(false);
  const [isRunning, setIsRunning] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [wsNotification, setWsNotification] = useState<{ type: 'success' | 'error'; message: string } | null>(null);

  // WebSocket for real-time updates
  const { connected: wsConnected } = useWebSocket((data) => {
    if (data.type === 'trade_executed') {
      setWsNotification({ type: 'success', message: 'Trade executed successfully!' });
      // Refresh trades
      load();
      setTimeout(() => setWsNotification(null), 3000);
    } else if (data.type === 'trade_error') {
      setWsNotification({ type: 'error', message: `Trade error: ${data.error}` });
      setTimeout(() => setWsNotification(null), 3000);
    }
  });

  const load = async () => {
    try {
      setLoading(true);
      setError(null);
      const accs = await getAccounts();
      const trades = await getTrades();
      setAccounts(accs || []);
      setTrades(trades || []);
    } catch (err) {
      console.error('Load error:', err);
      setError(err instanceof Error ? err.message : 'Failed to load data');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    load();
    const interval = setInterval(load, 5000);
    return () => clearInterval(interval);
  }, []);

  const handleAddToWatchlist = async (symbol: string) => {
    if (!selectedAccount) {
      alert('Please select an account first');
      return;
    }

    try {
      const res = await fetch(
        `${import.meta.env.VITE_API_URL || 'http://localhost:8000'}/api/watchlist`,
        {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            account_id: selectedAccount.login,
            symbol,
            lot_size: 0.01,
            stop_loss_pips: 50,
            take_profit_pips: 100,
            trailing_stop_pips: 30,
            use_trailing_stop: false,
            brick_size: 1.0,
            algo_enabled: true,
          }),
        }
      );

      if (res.ok) {
        setWatchlistSymbols([...watchlistSymbols, symbol]);
        setWatchlistRefresh(watchlistRefresh + 1);
      }
    } catch (error) {
      console.error('Failed to add to watchlist:', error);
    }
  };

  const handleWatchlistUpdate = () => {
    setWatchlistRefresh(watchlistRefresh + 1);
  };

  return (
    <div className="min-h-screen bg-slate-900 text-white p-4">
      <header className="mb-6">
        <div className="flex justify-between items-start mb-3">
          <div>
            <h1 className="text-4xl font-bold mb-2">🟡 Renko Reversal Gold Bot</h1>
            <p className="text-slate-400">Automated XAUUSD trading powered by MetaTrader 5</p>
          </div>
          <div className={`text-xs font-semibold px-3 py-1 rounded ${wsConnected ? 'bg-green-900 text-green-200' : 'bg-red-900 text-red-200'}`}>
            {wsConnected ? '● Live' : '● Offline'}
          </div>
        </div>
        {loading && <p className="text-slate-500 text-sm">Refreshing…</p>}
        {error && <p className="text-red-400 text-sm">Error: {error}</p>}
        {wsNotification && (
          <div className={`p-2 rounded text-sm mt-2 ${wsNotification.type === 'success' ? 'bg-green-900 text-green-200' : 'bg-red-900 text-red-200'}`}>
            {wsNotification.message}
          </div>
        )}
      </header>

      <div className="space-y-4">
        {/* Control Row */}
        <div className="grid grid-cols-1 lg:grid-cols-4 gap-4">
          <div className="lg:col-span-1">
            <AccountsPanel 
              accounts={accounts} 
              selectedAccount={selectedAccount}
              onSelectAccount={setSelectedAccount}
            />
          </div>
          <div className="lg:col-span-3">
            <Controls
              onStart={async () => {
                await startBot();
                setIsRunning(true);
                load();
              }}
              onStop={async () => {
                await stopBot();
                setIsRunning(false);
                load();
              }}
              onUpdateSettings={async (brickSize: number) => {
                await updateSettings(brickSize);
                load();
              }}
            />
          </div>
        </div>

        {/* Main Dashboard */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
          <div className="lg:col-span-2">
            {selectedAccount ? (
              <>
                <TickersPanel 
                  onAddToWatchlist={handleAddToWatchlist}
                  watchlistSymbols={watchlistSymbols}
                />
                <div className="mt-4">
                  <WatchlistManager 
                    accountId={selectedAccount.login}
                    onUpdate={handleWatchlistUpdate}
                  />
                </div>
                <div className="mt-4">
                  <LivePositions accountId={selectedAccount.login} />
                </div>
              </>
            ) : (
              <div className="bg-slate-800 p-8 rounded-lg text-center text-slate-400">
                Select an account to start trading
              </div>
            )}
          </div>

          <div className="space-y-4">
            {selectedAccount && (
              <TradeExecutor 
                accountId={selectedAccount.login}
                symbol="XAUUSD"
              />
            )}
            <TradeDashboard trades={trades} />
            <LogsViewer />
          </div>
        </div>
      </div>
    </div>
  );
}

export default App;
