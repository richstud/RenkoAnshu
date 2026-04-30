import { jsx as _jsx, jsxs as _jsxs } from "react/jsx-runtime";
import { useEffect, useState } from 'react';
export default function WatchlistManager({ accountId, onUpdate, refreshTrigger }) {
    const [watchlist, setWatchlist] = useState([]);
    const [editingId, setEditingId] = useState(null);
    const [editData, setEditData] = useState({});
    const [loading, setLoading] = useState(true);
    useEffect(() => {
        setLoading(true);
        fetchWatchlist();
        const interval = setInterval(fetchWatchlist, 5000);
        return () => clearInterval(interval);
    }, [accountId, refreshTrigger]);
    const fetchWatchlist = async () => {
        try {
            const controller = new AbortController();
            const timeoutId = setTimeout(() => controller.abort(), 8000);
            const res = await fetch(`${import.meta.env.VITE_API_URL || 'http://localhost:8000'}/api/watchlist?account_id=${accountId}`, { signal: controller.signal });
            clearTimeout(timeoutId);
            if (res.ok) {
                const data = await res.json();
                const list = data.data || data.symbols || [];
                setWatchlist(list);
            }
            // If not ok, keep existing data (don't reset to empty)
        }
        catch (error) {
            if (error.name !== 'AbortError') {
                console.error('Failed to fetch watchlist:', error);
            }
            // On error/timeout, keep existing data displayed
        }
        finally {
            setLoading(false);
        }
    };
    const handleEdit = (item) => {
        setEditingId(item.id);
        setEditData(item);
    };
    const handleSave = async (id) => {
        try {
            const item = watchlist.find(w => w.id === id);
            if (!item)
                return;
            // Update via PUT endpoint with symbol and brick_size
            const res = await fetch(`${import.meta.env.VITE_API_URL || 'http://localhost:8000'}/api/watchlist/${item.symbol}?account_id=${accountId}`, {
                method: 'PUT',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(editData),
            });
            if (res.ok) {
                setEditingId(null);
                fetchWatchlist();
                onUpdate();
            }
        }
        catch (error) {
            console.error('Failed to save watchlist:', error);
        }
    };
    const handleDelete = async (id) => {
        if (confirm('Remove from watchlist?')) {
            try {
                const item = watchlist.find(w => w.id === id);
                if (!item)
                    return;
                const url = `${import.meta.env.VITE_API_URL || 'http://localhost:8000'}/api/watchlist/${item.symbol}?account_id=${accountId}`;
                console.log('DELETE request to:', url);
                const res = await fetch(url, { method: 'DELETE' });
                const responseText = await res.text();
                console.log('DELETE response status:', res.status, 'body:', responseText);
                if (res.ok) {
                    setWatchlist(watchlist.filter(w => w.id !== id));
                    onUpdate();
                }
                else {
                    console.error('Failed to delete. Status:', res.status, 'Response:', responseText);
                    alert(`Failed to delete ${item.symbol}. Please try again.`);
                }
            }
            catch (error) {
                console.error('Failed to delete from watchlist:', error);
                alert('Error deleting from watchlist');
            }
        }
    };
    const toggleAlgo = async (item) => {
        try {
            const res = await fetch(`${import.meta.env.VITE_API_URL || 'http://localhost:8000'}/api/watchlist/${item.symbol}/algo?account_id=${accountId}&algo_enabled=${!item.algo_enabled}`, {
                method: 'PUT',
                headers: { 'Content-Type': 'application/json' },
            });
            if (res.ok) {
                fetchWatchlist();
                onUpdate();
            }
        }
        catch (error) {
            console.error('Failed to toggle algo:', error);
        }
    };
    if (loading && watchlist.length === 0) {
        return (_jsxs("div", { className: "bg-slate-800 p-4 rounded-lg text-slate-400 flex items-center gap-2", children: [_jsx("span", { className: "animate-spin", children: "\u23F3" }), " Loading watchlist..."] }));
    }
    if (watchlist.length === 0) {
        return (_jsx("div", { className: "bg-slate-800 p-4 rounded-lg text-slate-400", children: "No symbols in watchlist yet. Add some from the Tickers panel above." }));
    }
    return (_jsxs("div", { className: "bg-slate-800 p-4 rounded-lg", children: [_jsx("h2", { className: "text-xl font-semibold mb-4", children: "\uD83D\uDCCB Watchlist" }), _jsx("div", { className: "space-y-3", children: watchlist.map((item) => (_jsx("div", { className: "bg-slate-700 p-3 rounded border border-slate-600", children: editingId === item.id ? (_jsxs("div", { className: "space-y-2", children: [_jsxs("div", { className: "flex justify-between items-center mb-2", children: [_jsx("span", { className: "font-semibold", children: item.symbol }), _jsx("button", { onClick: () => handleSave(item.id), className: "px-2 py-1 bg-green-600 hover:bg-green-700 rounded text-sm", children: "Save" })] }), _jsxs("div", { className: "grid grid-cols-2 gap-2 text-sm", children: [_jsxs("div", { children: [_jsx("label", { className: "text-slate-400", children: "SL (pips):" }), _jsx("input", { type: "number", value: editData.stop_loss_pips || 0, onChange: (e) => setEditData({ ...editData, stop_loss_pips: parseFloat(e.target.value) }), className: "w-full px-2 py-1 rounded bg-slate-600 text-white" })] }), _jsxs("div", { children: [_jsx("label", { className: "text-slate-400", children: "TP (pips):" }), _jsx("input", { type: "number", value: editData.take_profit_pips || 0, onChange: (e) => setEditData({ ...editData, take_profit_pips: parseFloat(e.target.value) }), className: "w-full px-2 py-1 rounded bg-slate-600 text-white" })] }), _jsxs("div", { children: [_jsx("label", { className: "text-slate-400", children: "Trailing (pips):" }), _jsx("input", { type: "number", value: editData.trailing_stop_pips || 0, onChange: (e) => setEditData({ ...editData, trailing_stop_pips: parseFloat(e.target.value) }), className: "w-full px-2 py-1 rounded bg-slate-600 text-white" })] }), _jsxs("div", { children: [_jsx("label", { className: "text-slate-400", children: "Brick Size:" }), _jsx("input", { type: "number", value: editData.brick_size || 0, onChange: (e) => setEditData({ ...editData, brick_size: parseFloat(e.target.value) }), className: "w-full px-2 py-1 rounded bg-slate-600 text-white" })] }), _jsxs("div", { children: [_jsx("label", { className: "text-slate-400", children: "Lot Size:" }), _jsx("input", { type: "number", step: "0.01", value: editData.lot_size || 0, onChange: (e) => setEditData({ ...editData, lot_size: parseFloat(e.target.value) }), className: "w-full px-2 py-1 rounded bg-slate-600 text-white" })] }), _jsxs("div", { className: "flex items-center", children: [_jsx("label", { className: "text-slate-400 mr-2", children: "Use Trailing:" }), _jsx("input", { type: "checkbox", checked: editData.use_trailing_stop || false, onChange: (e) => setEditData({ ...editData, use_trailing_stop: e.target.checked }), className: "w-4 h-4" })] })] })] })) : (_jsxs("div", { children: [_jsxs("div", { className: "flex justify-between items-center mb-2", children: [_jsxs("div", { children: [_jsx("span", { className: "font-semibold text-lg", children: item.symbol }), _jsxs("span", { className: "ml-3 text-sm text-slate-400", children: ["SL: ", item.stop_loss_pips, "p | TP: ", item.take_profit_pips, "p | Trail: ", item.trailing_stop_pips, "p"] })] }), _jsxs("div", { className: "flex gap-2", children: [_jsx("button", { onClick: () => toggleAlgo(item), className: `px-3 py-1 rounded text-sm transition ${item.algo_enabled
                                                    ? 'bg-emerald-600 hover:bg-emerald-700'
                                                    : 'bg-red-600 hover:bg-red-700'}`, children: item.algo_enabled ? '✅ ON' : '❌ OFF' }), _jsx("button", { onClick: () => handleEdit(item), className: "px-3 py-1 bg-blue-600 hover:bg-blue-700 rounded text-sm", children: "Edit" }), _jsx("button", { onClick: () => handleDelete(item.id), className: "px-3 py-1 bg-red-600 hover:bg-red-700 rounded text-sm", children: "Delete" })] })] }), _jsxs("div", { className: "text-xs text-slate-400 mt-1", children: ["Lot: ", item.lot_size, " | Brick: ", item.brick_size, " | ", item.use_trailing_stop && '📈 Trailing'] })] })) }, item.id))) })] }));
}
