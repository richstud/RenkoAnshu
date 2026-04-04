import { Trade } from '../App';

export default function TradeDashboard({ trades }: { trades: Trade[] }) {
  return (
    <div className="bg-slate-800 p-4 rounded-lg">
      <h2 className="text-xl font-semibold mb-3">Live Trades</h2>
      <div className="overflow-auto">
        <table className="w-full text-left text-sm">
          <thead>
            <tr className="border-b border-slate-600">
              <th>Account</th>
              <th>Type</th>
              <th>Symbol</th>
              <th>Lot</th>
              <th>Entry</th>
              <th>Exit</th>
              <th>PnL</th>
            </tr>
          </thead>
          <tbody>
            {trades.map((trade) => (
              <tr key={trade.id} className="border-b border-slate-700">
                <td>{trade.account_id}</td>
                <td>{trade.type}</td>
                <td>{trade.symbol}</td>
                <td>{trade.lot}</td>
                <td>{trade.entry_price}</td>
                <td>{trade.exit_price ?? '---'}</td>
                <td>{trade.profit ?? '---'}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
