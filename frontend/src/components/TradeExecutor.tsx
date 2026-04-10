import { useState, useEffect } from 'react';
import { executeTrade } from '../services/api';

interface SymbolData {
  symbol: string;
  description?: string;
}

interface TradeExecutorProps {
  accountId: number | null;
  availableSymbols: string[];
  symbolData?: SymbolData[];
  onSymbolSelected?: (symbol: string) => void;
}

export default function TradeExecutor({ accountId, availableSymbols, symbolData = [], onSymbolSelected }: TradeExecutorProps) {
  const [symbol, setSymbol] = useState<string>(availableSymbols[0] || 'XAUUSD');
  const [tradeType, setTradeType] = useState<'buy' | 'sell'>('buy');
  const [lotSize, setLotSize] = useState(0.01);
  const [stopLoss, setStopLoss] = useState<number>();
  const [takeProfit, setTakeProfit] = useState<number>();
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState<{ type: 'success' | 'error'; text: string } | null>(null);

  useEffect(() => {
    if (availableSymbols.length > 0 && !availableSymbols.includes(symbol)) {
      setSymbol(availableSymbols[0]);
    }
  }, [availableSymbols, symbol]);

  const getSymbolDisplay = (sym: string) => {
    const data = symbolData.find(s => s.symbol === sym);
    if (data?.description) {
      return `${sym} - ${data.description}`;
    }
    return sym;
  };

  const handleSymbolChange = (newSymbol: string) => {
    setSymbol(newSymbol);
    if (onSymbolSelected) {
      onSymbolSelected(newSymbol);
    }
  };

  const handleExecute = async () => {
    if (!accountId) {
      setMessage({ type: 'error', text: 'Please select an account first' });
      return;
    }

    setLoading(true);
    setMessage(null);

    try {
      const result = await executeTrade({
        account_id: accountId,
        symbol,
        trade_type: tradeType,
        lot_size: lotSize,
        stop_loss: stopLoss,
        take_profit: takeProfit,
      });

      if (result) {
        setMessage({ type: 'success', text: result.message || 'Trade executed successfully!' });
        setLotSize(0.01);
        setStopLoss(undefined);
        setTakeProfit(undefined);
      } else {
        setMessage({ type: 'error', text: 'Failed to execute trade' });
      }
    } catch (error) {
      setMessage({ type: 'error', text: error instanceof Error ? error.message : 'Trade execution failed' });
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="bg-slate-700 p-4 rounded-lg border border-slate-600">
      <h3 className="text-lg font-semibold mb-4">📈 Manual Trade Execution</h3>
      
      <div className="space-y-3">
        {/* Trade Type Selection */}
        <div className="flex gap-2">
          <button
            onClick={() => setTradeType('buy')}
            className={`flex-1 py-2 rounded font-semibold transition ${
              tradeType === 'buy'
                ? 'bg-green-600 text-white'
                : 'bg-slate-600 text-slate-300 hover:bg-slate-500'
            }`}
          >
            🟢 BUY
          </button>
          <button
            onClick={() => setTradeType('sell')}
            className={`flex-1 py-2 rounded font-semibold transition ${
              tradeType === 'sell'
                ? 'bg-red-600 text-white'
                : 'bg-slate-600 text-slate-300 hover:bg-slate-500'
            }`}
          >
            🔴 SELL
          </button>
        </div>

        {/* Symbol Selection */}
        <div>
          <label className="text-slate-400 text-sm block mb-1">Select Symbol</label>
          <select
            value={symbol}
            onChange={(e) => handleSymbolChange(e.target.value)}
            className="w-full px-3 py-2 rounded bg-slate-600 text-white border border-slate-500 focus:border-blue-400 outline-none text-sm"
          >
            {availableSymbols.length > 0 ? (
              availableSymbols.map((sym) => (
                <option key={sym} value={sym}>
                  {getSymbolDisplay(sym)}
                </option>
              ))
            ) : (
              <option>No symbols available</option>
            )}
          </select>
          <div className="text-xs text-slate-500 mt-1">
            Selected: <span className="text-slate-300 font-semibold">{getSymbolDisplay(symbol)}</span>
          </div>
        </div>

        {/* Lot Size */}
        <div>
          <label className="text-slate-400 text-sm block mb-1">Lot Size</label>
          <input
            type="number"
            min="0.01"
            step="0.01"
            value={lotSize}
            onChange={(e) => setLotSize(parseFloat(e.target.value))}
            className="w-full px-3 py-2 rounded bg-slate-600 text-white border border-slate-500 focus:border-blue-400 outline-none"
          />
        </div>

        {/* Stop Loss */}
        <div>
          <label className="text-slate-400 text-sm block mb-1">Stop Loss in Pips (optional)</label>
          <input
            type="number"
            step="0.1"
            value={stopLoss || ''}
            onChange={(e) => setStopLoss(e.target.value ? parseFloat(e.target.value) : undefined)}
            placeholder="e.g., 10"
            className="w-full px-3 py-2 rounded bg-slate-600 text-white border border-slate-500 focus:border-blue-400 outline-none"
          />
          <div className="text-xs text-slate-500 mt-1">Enter number of pips below current price</div>
        </div>

        {/* Take Profit */}
        <div>
          <label className="text-slate-400 text-sm block mb-1">Take Profit in Pips (optional)</label>
          <input
            type="number"
            step="0.1"
            value={takeProfit || ''}
            onChange={(e) => setTakeProfit(e.target.value ? parseFloat(e.target.value) : undefined)}
            placeholder="e.g., 20"
            className="w-full px-3 py-2 rounded bg-slate-600 text-white border border-slate-500 focus:border-blue-400 outline-none"
          />
          <div className="text-xs text-slate-500 mt-1">Enter number of pips above current price</div>
        </div>

        {/* Execute Button */}
        <button
          onClick={handleExecute}
          disabled={loading || !accountId}
          className={`w-full py-3 rounded font-bold transition ${
            loading || !accountId
              ? 'bg-slate-600 text-slate-400 cursor-not-allowed'
              : tradeType === 'buy'
              ? 'bg-green-600 hover:bg-green-700 text-white'
              : 'bg-red-600 hover:bg-red-700 text-white'
          }`}
        >
          {loading ? '⏳ Executing...' : `Execute ${tradeType.toUpperCase()}`}
        </button>

        {/* Status Message */}
        {message && (
          <div
            className={`p-3 rounded text-sm font-semibold text-center ${
              message.type === 'success'
                ? 'bg-green-900 text-green-200'
                : 'bg-red-900 text-red-200'
            }`}
          >
            {message.text}
          </div>
        )}
      </div>
    </div>
  );
}
