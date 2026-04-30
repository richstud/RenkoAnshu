import { jsx as _jsx, jsxs as _jsxs } from "react/jsx-runtime";
import { useState, useEffect } from 'react';
import { executeTrade } from '../services/api';
export default function TradeExecutor({ accountId, availableSymbols, symbolData = [], onSymbolSelected }) {
    const [symbol, setSymbol] = useState(availableSymbols[0] || 'XAUUSD');
    const [tradeType, setTradeType] = useState('buy');
    const [lotSize, setLotSize] = useState(0.01);
    const [stopLoss, setStopLoss] = useState();
    const [takeProfit, setTakeProfit] = useState();
    const [loading, setLoading] = useState(false);
    const [message, setMessage] = useState(null);
    useEffect(() => {
        if (availableSymbols.length > 0 && !availableSymbols.includes(symbol)) {
            setSymbol(availableSymbols[0]);
        }
    }, [availableSymbols, symbol]);
    const getSymbolDisplay = (sym) => {
        const data = symbolData.find(s => s.symbol === sym);
        if (data?.description) {
            return `${sym} - ${data.description}`;
        }
        return sym;
    };
    const handleSymbolChange = (newSymbol) => {
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
            }
            else {
                setMessage({ type: 'error', text: 'Failed to execute trade' });
            }
        }
        catch (error) {
            setMessage({ type: 'error', text: error instanceof Error ? error.message : 'Trade execution failed' });
        }
        finally {
            setLoading(false);
        }
    };
    return (_jsxs("div", { className: "bg-slate-700 p-4 rounded-lg border border-slate-600", children: [_jsx("h3", { className: "text-lg font-semibold mb-4", children: "\uD83D\uDCC8 Manual Trade Execution" }), _jsxs("div", { className: "space-y-3", children: [_jsxs("div", { className: "flex gap-2", children: [_jsx("button", { onClick: () => setTradeType('buy'), className: `flex-1 py-2 rounded font-semibold transition ${tradeType === 'buy'
                                    ? 'bg-green-600 text-white'
                                    : 'bg-slate-600 text-slate-300 hover:bg-slate-500'}`, children: "\uD83D\uDFE2 BUY" }), _jsx("button", { onClick: () => setTradeType('sell'), className: `flex-1 py-2 rounded font-semibold transition ${tradeType === 'sell'
                                    ? 'bg-red-600 text-white'
                                    : 'bg-slate-600 text-slate-300 hover:bg-slate-500'}`, children: "\uD83D\uDD34 SELL" })] }), _jsxs("div", { children: [_jsx("label", { className: "text-slate-400 text-sm block mb-1", children: "Select Symbol" }), _jsx("select", { value: symbol, onChange: (e) => handleSymbolChange(e.target.value), className: "w-full px-3 py-2 rounded bg-slate-600 text-white border border-slate-500 focus:border-blue-400 outline-none text-sm", children: availableSymbols.length > 0 ? (availableSymbols.map((sym) => (_jsx("option", { value: sym, children: getSymbolDisplay(sym) }, sym)))) : (_jsx("option", { children: "No symbols available" })) }), _jsxs("div", { className: "text-xs text-slate-500 mt-1", children: ["Selected: ", _jsx("span", { className: "text-slate-300 font-semibold", children: getSymbolDisplay(symbol) })] })] }), _jsxs("div", { children: [_jsx("label", { className: "text-slate-400 text-sm block mb-1", children: "Lot Size" }), _jsx("input", { type: "number", min: "0.01", step: "0.01", value: lotSize, onChange: (e) => setLotSize(parseFloat(e.target.value)), className: "w-full px-3 py-2 rounded bg-slate-600 text-white border border-slate-500 focus:border-blue-400 outline-none" })] }), _jsxs("div", { children: [_jsx("label", { className: "text-slate-400 text-sm block mb-1", children: "Stop Loss in Pips (optional)" }), _jsx("input", { type: "number", step: "0.1", value: stopLoss || '', onChange: (e) => setStopLoss(e.target.value ? parseFloat(e.target.value) : undefined), placeholder: "e.g., 10", className: "w-full px-3 py-2 rounded bg-slate-600 text-white border border-slate-500 focus:border-blue-400 outline-none" }), _jsx("div", { className: "text-xs text-slate-500 mt-1", children: "Enter number of pips below current price" })] }), _jsxs("div", { children: [_jsx("label", { className: "text-slate-400 text-sm block mb-1", children: "Take Profit in Pips (optional)" }), _jsx("input", { type: "number", step: "0.1", value: takeProfit || '', onChange: (e) => setTakeProfit(e.target.value ? parseFloat(e.target.value) : undefined), placeholder: "e.g., 20", className: "w-full px-3 py-2 rounded bg-slate-600 text-white border border-slate-500 focus:border-blue-400 outline-none" }), _jsx("div", { className: "text-xs text-slate-500 mt-1", children: "Enter number of pips above current price" })] }), _jsx("button", { onClick: handleExecute, disabled: loading || !accountId, className: `w-full py-3 rounded font-bold transition ${loading || !accountId
                            ? 'bg-slate-600 text-slate-400 cursor-not-allowed'
                            : tradeType === 'buy'
                                ? 'bg-green-600 hover:bg-green-700 text-white'
                                : 'bg-red-600 hover:bg-red-700 text-white'}`, children: loading ? '⏳ Executing...' : `Execute ${tradeType.toUpperCase()}` }), message && (_jsx("div", { className: `p-3 rounded text-sm font-semibold text-center ${message.type === 'success'
                            ? 'bg-green-900 text-green-200'
                            : 'bg-red-900 text-red-200'}`, children: message.text }))] })] }));
}
