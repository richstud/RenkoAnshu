import { jsx as _jsx, jsxs as _jsxs } from "react/jsx-runtime";
import { useEffect, useState } from 'react';
export default function LogsViewer() {
    const [logs, setLogs] = useState([]);
    useEffect(() => {
        const fetchLogs = async () => {
            try {
                const res = await fetch(`${import.meta.env.VITE_API_URL || 'http://localhost:8000'}/api/logs`);
                if (res.ok) {
                    const data = await res.json();
                    const logsArray = Array.isArray(data) ? data : (data.data || []);
                    setLogs(logsArray);
                }
            }
            catch {
                // noop - logs endpoint not available
            }
        };
        fetchLogs();
        const interval = setInterval(fetchLogs, 5000);
        return () => clearInterval(interval);
    }, []);
    return (_jsxs("div", { className: "bg-slate-800 p-4 rounded-lg", children: [_jsx("h2", { className: "text-xl font-semibold mb-3", children: "Logs Viewer" }), _jsx("div", { className: "h-56 overflow-y-auto", children: logs.length === 0 ? (_jsx("div", { className: "text-slate-300", children: "No logs yet" })) : (logs.map((log) => (_jsxs("div", { className: "border-b border-slate-700 py-1 text-sm", children: [_jsx("span", { className: "text-emerald-300", children: log.created_at }), " \u2013 Account ", log.account_id, ": ", log.event] }, log.id)))) })] }));
}
