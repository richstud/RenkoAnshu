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
          {accounts.map((acc) => {
            const isSelected = selectedAccount?.login === acc.login;
            return (
              <button
                key={acc.login}
                onClick={() => onSelectAccount(acc)}
                className={`w-full p-3 rounded text-left transition ${
                  isSelected
                    ? 'bg-blue-600 border-2 border-blue-400'
                    : 'bg-slate-700 border-2 border-slate-600 hover:border-slate-500'
                }`}
              >
                <div className="flex justify-between items-center">
                  <span className="text-sm font-semibold text-white">{acc.login}</span>
                  <span className={`text-xs px-2 py-0.5 rounded ${acc.status === 'active' ? 'bg-green-900 text-green-300' : 'bg-red-900 text-red-300'}`}>
                    {acc.status}
                  </span>
                </div>
                <div className="text-xs text-slate-400 mt-1">{acc.server}</div>
                {acc.balance !== undefined && (
                  <div className="mt-1 flex gap-3">
                    <span className="text-xs text-yellow-300 font-mono">
                      💰 ${acc.balance.toFixed(2)}
                    </span>
                    {acc.equity !== undefined && acc.equity !== acc.balance && (
                      <span className={`text-xs font-mono ${acc.equity >= acc.balance ? 'text-green-400' : 'text-red-400'}`}>
                        Eq: ${acc.equity.toFixed(2)}
                      </span>
                    )}
                  </div>
                )}
              </button>
            );
          })}
        </div>
      )}
    </div>
  );
}
