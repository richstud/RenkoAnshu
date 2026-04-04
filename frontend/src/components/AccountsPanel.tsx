import { Account } from '../App';

export default function AccountsPanel({ accounts }: { accounts: Account[] }) {
  return (
    <div className="bg-slate-800 p-4 rounded-lg">
      <h2 className="text-xl font-semibold mb-3">Accounts</h2>
      <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
        {accounts.map((acc) => (
          <div key={acc.login} className="bg-slate-700 p-3 rounded">
            <div className="text-sm text-slate-300">Login: {acc.login}</div>
            <div className="text-sm">Server: {acc.server}</div>
            <div className="text-sm">Status: {acc.status}</div>
          </div>
        ))}
      </div>
    </div>
  );
}
