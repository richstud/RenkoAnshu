import { Account } from '../App';

interface AccountsPanelProps {
  accounts: Account[];
  selectedAccount: Account | null;
  onSelectAccount: (account: Account) => void;
}

export default function AccountsPanel({ accounts, selectedAccount, onSelectAccount }: AccountsPanelProps) {
  return (
    <div className="bg-slate-800 p-4 rounded-lg">
      <h2 className="text-xl font-semibold mb-3">📊 Accounts</h2>
      {accounts.length === 0 ? (
        <div className="text-slate-400 text-sm">No accounts loaded</div>
      ) : (
        <div className="space-y-2">
          {accounts.map((acc) => (
            <button
              key={acc.login}
              onClick={() => onSelectAccount(acc)}
              className={`w-full p-3 rounded text-left transition ${
                selectedAccount?.login === acc.login
                  ? 'bg-blue-600 border-2 border-blue-400'
                  : 'bg-slate-700 border-2 border-slate-600 hover:border-slate-500'
              }`}
            >
              <div className="text-sm text-slate-300">Login: {acc.login}</div>
              <div className="text-sm">Server: {acc.server}</div>
              <div className={`text-sm ${acc.status === 'active' ? 'text-green-400' : 'text-red-400'}`}>
                Status: {acc.status}
              </div>
            </button>
          ))}
        </div>
      )}
    </div>
  );
}
