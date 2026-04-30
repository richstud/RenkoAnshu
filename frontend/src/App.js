import { jsx as _jsx, jsxs as _jsxs } from "react/jsx-runtime";
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
function App() {
    const [session, setSession] = useState(undefined);
    const [accounts, setAccounts] = useState([]);
    const [selectedAccount, setSelectedAccount] = useState(null);
    const [trades, setTrades] = useState([]);
    const [availableSymbols, setAvailableSymbols] = useState([]);
    const [symbolData, setSymbolData] = useState([]);
    const [selectedSymbol, setSelectedSymbol] = useState('GOLD');
    const [watchlistSymbols, setWatchlistSymbols] = useState([]);
    const [watchlistRefresh, setWatchlistRefresh] = useState(0);
    const [loading, setLoading] = useState(false);
    const [isRunning, setIsRunning] = useState(false);
    const [error, setError] = useState(null);
    const [wsNotification, setWsNotification] = useState(null);
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
        }
        else if (data.type === 'trade_error') {
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
                    const symbols = tickers.map((t) => t.symbol);
                    setAvailableSymbols(symbols);
                    if (symbols.length > 0 && !symbols.includes(selectedSymbol)) {
                        setSelectedSymbol(symbols[0]);
                    }
                }
            }
            catch (err) {
                console.error('Failed to fetch symbols:', err);
            }
        }
        catch (err) {
            console.error('Load error:', err);
            setError(err instanceof Error ? err.message : 'Failed to load data');
        }
        finally {
            setLoading(false);
        }
    };
    useEffect(() => {
        if (!session)
            return; // Only load when authenticated
        load();
        const interval = setInterval(load, 5000);
        return () => clearInterval(interval);
    }, [session]); // Re-run when session changes (i.e., after login)
    const handleAddToWatchlist = async (symbol) => {
        if (!selectedAccount) {
            setWsNotification({ type: 'error', message: '⚠️ Select an account first to add to watchlist' });
            setTimeout(() => setWsNotification(null), 3000);
            return;
        }
        try {
            const res = await fetch(`${import.meta.env.VITE_API_URL || 'http://localhost:8000'}/api/watchlist`, {
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
            });
            if (res.ok) {
                setWatchlistSymbols([...watchlistSymbols, symbol]);
                // Trigger immediate refresh in WatchlistManager
                setWatchlistRefresh(watchlistRefresh + 1);
                // Also show success feedback
                setWsNotification({ type: 'success', message: `✅ ${symbol} added to watchlist!` });
                setTimeout(() => setWsNotification(null), 3000);
            }
            else {
                const errorData = await res.json();
                setWsNotification({ type: 'error', message: `Failed to add ${symbol}: ${errorData.detail || 'Unknown error'}` });
                setTimeout(() => setWsNotification(null), 3000);
            }
        }
        catch (error) {
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
        return (_jsx("div", { className: "min-h-screen bg-slate-900 flex items-center justify-center", children: _jsx("div", { className: "text-white text-xl", children: "\u23F3 Loading..." }) }));
    }
    // Show login page if not authenticated
    if (!session) {
        return _jsx(AuthPage, {});
    }
    return (_jsxs("div", { className: "min-h-screen bg-slate-900 text-white p-4", children: [_jsxs("header", { className: "mb-6", children: [_jsxs("div", { className: "flex justify-between items-start mb-3", children: [_jsxs("div", { children: [_jsx("h1", { className: "text-4xl font-bold mb-2", children: "\uD83D\uDFE1 Renko Reversal Gold Bot" }), _jsx("p", { className: "text-slate-400", children: "Automated Gold (GOLD) trading powered by MetaTrader 5" })] }), _jsxs("div", { className: "flex flex-col items-end gap-1", children: [_jsxs("button", { onClick: () => supabase.auth.signOut(), className: "text-xs text-slate-400 hover:text-red-400 transition-colors mb-1", title: `Signed in as ${session.user.email}`, children: ["\uD83D\uDD13 Sign Out (", session.user.email, ")"] }), _jsx("div", { className: `text-xs font-semibold px-3 py-1 rounded ${wsConnected ? 'bg-green-900 text-green-200' : 'bg-red-900 text-red-200'}`, children: wsConnected ? '🟢 Live' : '🔴 Offline' }), !wsConnected && _jsx("div", { className: "text-xs text-slate-500", children: "Connecting to backend..." })] })] }), loading && _jsx("p", { className: "text-slate-500 text-sm", children: "Refreshing\u2026" }), error && _jsxs("p", { className: "text-red-400 text-sm", children: ["Error: ", error] }), wsNotification && (_jsx("div", { className: `p-2 rounded text-sm mt-2 ${wsNotification.type === 'success' ? 'bg-green-900 text-green-200' : 'bg-red-900 text-red-200'}`, children: wsNotification.message }))] }), _jsxs("div", { className: "space-y-4", children: [_jsx(AccountManager, {}), _jsxs("div", { className: "grid grid-cols-1 lg:grid-cols-4 gap-4", children: [_jsx("div", { className: "lg:col-span-1", children: _jsx(AccountsPanel, { accounts: accounts, selectedAccount: selectedAccount, onSelectAccount: setSelectedAccount }) }), _jsx("div", { className: "lg:col-span-3", children: _jsx(Controls, { onStart: async () => {
                                        await startBot();
                                        setIsRunning(true);
                                        load();
                                    }, onStop: async () => {
                                        await stopBot();
                                        setIsRunning(false);
                                        load();
                                    }, onUpdateSettings: async (brickSize) => {
                                        await updateSettings(brickSize);
                                        load();
                                    } }) })] }), _jsxs("div", { className: "grid grid-cols-1 lg:grid-cols-3 gap-4", children: [_jsxs("div", { className: "lg:col-span-2", children: [_jsx(TickersPanel, { onAddToWatchlist: handleAddToWatchlist, watchlistSymbols: watchlistSymbols }), selectedAccount && (_jsx("div", { className: "mt-4", children: _jsx(WatchlistManager, { accountId: selectedAccount.login, onUpdate: handleWatchlistUpdate, refreshTrigger: watchlistRefresh }) })), selectedAccount && (_jsx("div", { className: "mt-4", children: _jsx(LivePositions, { accountId: selectedAccount.login, onAccountInfo: (info) => {
                                                setAccounts(prev => prev.map(a => a.login === selectedAccount.login
                                                    ? { ...a, balance: info.balance, equity: info.equity }
                                                    : a));
                                                setSelectedAccount(prev => prev ? { ...prev, balance: info.balance, equity: info.equity } : prev);
                                            } }, selectedAccount.login) })), _jsx("div", { className: "mt-4", children: _jsx(RenkoChart, { symbol: selectedSymbol || 'GOLD', accountId: selectedAccount?.login, onAddToWatchlist: handleAddToWatchlist }) })] }), _jsxs("div", { className: "space-y-4", children: [selectedAccount && (_jsx(TradeExecutor, { accountId: selectedAccount.login, availableSymbols: availableSymbols.length > 0 ? availableSymbols : ['GOLD'], symbolData: symbolData, onSymbolSelected: setSelectedSymbol })), _jsx(TradeDashboard, { trades: trades }), selectedAccount && (_jsx(TradeHistory, { accountId: selectedAccount.login }, selectedAccount.login)), _jsx(LogsViewer, {})] })] })] })] }));
}
export default App;
