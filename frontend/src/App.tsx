import { useEffect, useState } from 'react';
import { getAccounts, getTrades, startBot, stopBot, updateSettings } from './services/api';
import { supabase } from './services/supabase';
import AuthPage from './components/AuthPage';
import AccountsPanel from './components/AccountsPanel';
import AccountManager from './components/AccountManager';
import TradeDashboard from './components/TradeDashboard';
import TradeHistory from './components/TradeHistory';
import Controls from './components/Controls';
import LogsViewer from './components/LogsViewer';
import TickersPanel from './components/TickersPanel';
import WatchlistManager from './components/WatchlistManager';
import LivePositions from './components/LivePositions';
import TradeExecutor from './components/TradeExecutor';
import RenkoChart from './components/RenkoChart';
import { useWebSocket } from './hooks/useWebSocket';
import type { Session } from '@supabase/supabase-js';

export type Trade = { id: number; account_id: number; symbol: string; type: string; lot: number; entry_price: number; exit_price?: number; profit?: number; timestamp: string };
export type Account = { id: number; login: number; server: string; status: string };

function App() {
  const [session, setSession] = useState<Session | null | undefined>(undefined);
  const [accounts, setAccounts] = useState<Account[]>([]);
  const [selectedAccount, setSelectedAccount] = useState<Account | null>(null);
  const [trades, setTrades] = useState<Trade[]>([]);
  const [availableSymbols, setAvailableSymbols] = useState<string[]>([]);
  const [symbolData, setSymbolData] = useState<any[]>([]);
  const [selectedSymbol, setSelectedSymbol] = useState<string>('XAUUSD');
  const [watchlistSymbols, setWatchlistSymbols] = useState<string[]>([]);
  const [watchlistRefresh, setWatchlistRefresh] = useState(0);
  const [loading, setLoading] = useState(false);
  const [isRunning, setIsRunning] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [wsNotification, setWsNotification] = useState<{ type: 'success' | 'error'; message: string } | null>(null);

  // Auth session listener
  useEffect(() => {
    supabase.auth.getSession().then(({ data: { session } }) => setSession(session));
    const { data: { subscription } } = supabase.auth.onAuthStateChange((_event, session) => {
      setSession(session);
    });
    return () => subscription.unsubscribe();
  }, []);

  // WebSocket for real-time updates
  const { connected: wsConnected, ws } = useWebSocket((data) => {
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
      
      // Fetch available symbols
      try {
        const res = await fetch(`${import.meta.env.VITE_API_URL || 'http://localhost:8000'}/api/tickers`);
        if (res.ok) {
          const response = await res.json();
          const tickers = response.data || response;
          setSymbolData(tickers);
          const symbols = tickers.map((t: any) => t.symbol);
          setAvailableSymbols(symbols);
          if (symbols.length > 0 && !symbols.includes(selectedSymbol)) {
            setSelectedSymbol(symbols[0]);
          }
        }
      } catch (err) {
        console.error('Failed to fetch symbols:', err);
      }
    } catch (err) {
      console.error('Load error:', err);
      setError(err instanceof Error ? err.message : 'Failed to load data');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (!session) return; // Only load when authenticated
    load();
    const interval = setInterval(load, 5000);
    return () => clearInterval(interval);
  }, [session]); // Re-run when session changes (i.e., after login)

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
        // Trigger immediate refresh in WatchlistManager
        setWatchlistRefresh(watchlistRefresh + 1);
        // Also show success feedback
        setWsNotification({ type: 'success', message: `✅ ${symbol} added to watchlist!` });
        setTimeout(() => setWsNotification(null), 3000);
      } else {
        const errorData = await res.json();
        setWsNotification({ type: 'error', message: `Failed to add ${symbol}: ${errorData.detail || 'Unknown error'}` });
        setTimeout(() => setWsNotification(null), 3000);
      }
    } catch (error) {
      console.error('Failed to add to watchlist:', error);
      setWsNotification({ type: 'error', message: `Error adding ${symbol} to watchlist` });
      setTimeout(() => setWsNotification(null), 3000);
    }
  };

  const handleWatchlistUpdate = () => {
    setWatchlistRefresh(watchlistRefresh + 1);
  };

  // Show loading spinner while checking auth
  if (session === undefined) {
    return (
      <div className="min-h-screen bg-slate-900 flex items-center justify-center">
        <div className="text-white text-xl">⏳ Loading...</div>
      </div>
    );
  }

  // Show login page if not authenticated
  if (!session) {
    return <AuthPage />;
  }

  return (
    <div className="min-h-screen bg-slate-900 text-white p-4">
      <header className="mb-6">
        <div className="flex justify-between items-start mb-3">
          <div>
            <h1 className="text-4xl font-bold mb-2">🟡 Renko Reversal Gold Bot</h1>
            <p className="text-slate-400">Automated XAUUSD trading powered by MetaTrader 5</p>
          </div>
          <div className="flex flex-col items-end gap-1">
            <button
              onClick={() => supabase.auth.signOut()}
              className="text-xs text-slate-400 hover:text-red-400 transition-colors mb-1"
              title={`Signed in as ${session.user.email}`}
            >
              🔓 Sign Out ({session.user.email})
            </button>
            <div className={`text-xs font-semibold px-3 py-1 rounded ${wsConnected ? 'bg-green-900 text-green-200' : 'bg-red-900 text-red-200'}`}>
              {wsConnected ? '🟢 Live' : '🔴 Offline'}
            </div>
            {!wsConnected && <div className="text-xs text-slate-500">Connecting to backend...</div>}
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
        {/* Account Manager - For linking/unlinking MT5 accounts */}
        <AccountManager />
        
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
                    refreshTrigger={watchlistRefresh}
                  />
                </div>
                <div className="mt-4">
                  <LivePositions key={selectedAccount.login} accountId={selectedAccount.login} />
                </div>
                <div className="mt-4">
                  <RenkoChart 
                    symbol={selectedSymbol || 'EURUSD'} 
                    accountId={selectedAccount.login}
                    onAddToWatchlist={handleAddToWatchlist}
                  />
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
                availableSymbols={availableSymbols.length > 0 ? availableSymbols : ['XAUUSD']}
                symbolData={symbolData}
                onSymbolSelected={setSelectedSymbol}
              />
            )}
            <TradeDashboard trades={trades} />
            {selectedAccount && (
              <TradeHistory key={selectedAccount.login} accountId={selectedAccount.login} />
            )}
            <LogsViewer />
          </div>
        </div>
      </div>
    </div>
  );
}

export default App;
