import { useMemo, useState } from 'react';
import { Download, Search } from 'lucide-react';

export default function AuditLogPanel({ logs }) {
  const [query, setQuery] = useState('');
  const [actionFilter, setActionFilter] = useState('all');

  const actions = useMemo(
    () => ['all', ...Array.from(new Set(logs.map((l) => l.action))).sort()],
    [logs],
  );

  const filtered = useMemo(
    () =>
      logs.filter((log) => {
        if (actionFilter !== 'all' && log.action !== actionFilter) return false;
        if (!query.trim()) return true;
        const q = query.toLowerCase();
        return (
          String(log.reason).toLowerCase().includes(q) ||
          String(log.actor).toLowerCase().includes(q) ||
          String(log.task_id ?? '').toLowerCase().includes(q)
        );
      }),
    [logs, query, actionFilter],
  );

  const exportCsv = () => {
    const rows = [
      ['timestamp', 'actor', 'action', 'task_id', 'reason'],
      ...filtered.map((l) => [
        new Date(l.timestamp).toISOString(),
        l.actor,
        l.action,
        l.task_id ?? '',
        String(l.reason).replace(/"/g, '""'),
      ]),
    ];
    const csv = rows.map((r) => r.map((c) => `"${c}"`).join(',')).join('\n');
    const url = URL.createObjectURL(new Blob([csv], { type: 'text/csv' }));
    const a = document.createElement('a');
    a.href = url;
    a.download = `flowmind-audit-${new Date().toISOString().slice(0, 10)}.csv`;
    a.click();
    URL.revokeObjectURL(url);
  };

  return (
    <section className="glass animate-rise rounded-3xl p-5 sm:p-7" style={{ animationDelay: '240ms' }}>
      <div className="mb-4 flex flex-wrap items-center justify-between gap-3">
        <h2 className="font-display text-xl font-semibold text-white sm:text-2xl">Audit Trail</h2>
        <div className="flex items-center gap-2">
          <span className="rounded-full bg-white/10 px-3 py-1 text-xs font-semibold text-cyan-100">
            {filtered.length}/{logs.length} events
          </span>
          <button
            onClick={exportCsv}
            className="flex items-center gap-1 rounded-full border border-cyan-200/40 bg-cyan-500/10 px-3 py-1 text-xs font-bold text-cyan-100 hover:bg-cyan-500/25"
          >
            <Download size={12} /> CSV
          </button>
        </div>
      </div>

      <div className="mb-3 flex flex-wrap gap-2">
        <div className="relative min-w-[180px] flex-1">
          <Search size={14} className="absolute left-3 top-1/2 -translate-y-1/2 text-cyan-100/50" />
          <input
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Search reason / actor / task…"
            className="w-full rounded-full border border-white/15 bg-slate-950/60 py-2 pl-9 pr-3 text-sm text-white placeholder:text-cyan-100/40 focus:border-cyan-300 focus:outline-none"
          />
        </div>
        <select
          value={actionFilter}
          onChange={(e) => setActionFilter(e.target.value)}
          className="rounded-full border border-white/15 bg-slate-950/60 px-3 text-xs text-white"
        >
          {actions.map((a) => (
            <option key={a} value={a}>
              {a === 'all' ? 'All actions' : a}
            </option>
          ))}
        </select>
      </div>

      <div className="max-h-[360px] space-y-3 overflow-auto pr-1">
        {filtered.map((log) => (
          <article key={log.log_id} className="rounded-2xl border border-white/10 bg-slate-950/40 p-3">
            <div className="flex items-center justify-between gap-3">
              <p className="font-display text-sm text-orange-200">{log.action}</p>
              <p className="text-xs text-cyan-100/80">{new Date(log.timestamp).toLocaleString()}</p>
            </div>
            <p className="mt-1 text-sm text-white/90">{log.reason}</p>
            <p className="mt-2 text-xs text-cyan-50/70">Actor: {log.actor}</p>
            {log.task_id && <p className="text-xs text-cyan-50/70">Task ID: {log.task_id}</p>}
          </article>
        ))}
        {filtered.length === 0 && (
          <p className="py-6 text-center text-sm italic text-white/40">No matching audit events.</p>
        )}
      </div>
    </section>
  );
}
