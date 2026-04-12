import { useEffect, useState } from 'react';

export default function LogsViewer() {
  const [logs, setLogs] = useState<{ id: number; account_id: number; event: string; created_at: string }[]>([]);

  useEffect(() => {
    const fetchLogs = async () => {
      try {
        const res = await fetch(`${import.meta.env.VITE_API_URL || 'http://localhost:8000'}/api/logs`);
        if (res.ok) {
          const data = await res.json();
          const logsArray = Array.isArray(data) ? data : (data.data || []);
          setLogs(logsArray);
        }
      } catch {
        // noop - logs endpoint not available
      }
    };
    fetchLogs();
    const interval = setInterval(fetchLogs, 5000);
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="bg-slate-800 p-4 rounded-lg">
      <h2 className="text-xl font-semibold mb-3">Logs Viewer</h2>
      <div className="h-56 overflow-y-auto">
        {logs.length === 0 ? (
          <div className="text-slate-300">No logs yet</div>
        ) : (
          logs.map((log) => (
            <div key={log.id} className="border-b border-slate-700 py-1 text-sm">
              <span className="text-emerald-300">{log.created_at}</span> – Account {log.account_id}: {log.event}
            </div>
          ))
        )}
      </div>
    </div>
  );
}
