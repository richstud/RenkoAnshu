import { useEffect, useState } from 'react';
import { getAccounts, getTrades, startBot, stopBot, updateSettings } from './services/api';
import AccountsPanel from './components/AccountsPanel';
import TradeDashboard from './components/TradeDashboard';
import Controls from './components/Controls';
import LogsViewer from './components/LogsViewer';

export type Trade = { id: number; account_id: number; symbol: string; type: string; lot: number; entry_price: number; exit_price?: number; profit?: number; timestamp: string };
export type Account = { id: number; login: number; server: string; status: string };

function App() {
  const [accounts, setAccounts] = useState<Account[]>([]);
  const [trades, setTrades] = useState<Trade[]>([]);
  const [loading, setLoading] = useState(false);

  const load = async () => {
    setLoading(true);
    setAccounts(await getAccounts());
    setTrades(await getTrades());
    setLoading(false);
  };

  useEffect(() => {
    load();
    const interval = setInterval(load, 5000);
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="min-h-screen p-4 space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-2xl font-bold">RENKO XAUUSD BOT</h1>
        <div>{loading ? 'Refreshing…' : ''}</div>
      </div>

      <Controls
        onStart={async () => {
          await startBot();
          load();
        }}
        onStop={async () => {
          await stopBot();
          load();
        }}
        onUpdateSettings={async (brickSize: number) => {
          await updateSettings(brickSize);
          load();
        }}
      />

      <AccountsPanel accounts={accounts} />
      <TradeDashboard trades={trades} />
      <LogsViewer />
    </div>
  );
}

export default App;
