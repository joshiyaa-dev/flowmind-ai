// Live monitoring feed: recent autonomous decisions (reminders/escalations)
// derived from the audit log — polling-friendly, no WebSockets needed.
import { useMemo } from 'react';
import { Radio } from 'lucide-react';

export default function LiveFeed({ logs }) {
  const events = useMemo(
    () =>
      logs
        .filter((l) => /reminder|escalat|monitor/i.test(String(l.action)))
        .slice(0, 8),
    [logs],
  );

  return (
    <section className="glass animate-rise rounded-3xl p-5 sm:p-7" style={{ animationDelay: '300ms' }}>
      <div className="mb-4 flex items-center justify-between">
        <h2 className="flex items-center gap-2 font-display text-xl font-semibold text-white sm:text-2xl">
          <Radio size={20} className="animate-pulse text-emerald-400" /> Live Agent Feed
        </h2>
        <span className="rounded-full bg-white/10 px-3 py-1 text-xs font-semibold text-cyan-100">last {events.length} decisions</span>
      </div>

      {events.length === 0 ? (
        <p className="rounded-2xl border border-dashed border-white/10 p-6 text-center text-sm italic text-white/40">
          No monitoring events yet. The agent loop checks deadlines every cycle.
        </p>
      ) : (
        <ol className="relative space-y-3 border-l border-cyan-300/30 pl-5">
          {events.map((e) => (
            <li key={e.log_id} className="relative">
              <span className="absolute -left-[26px] top-1.5 h-2.5 w-2.5 rounded-full bg-emerald-400 shadow-[0_0_10px] shadow-emerald-400/60" />
              <p className="text-sm text-white">{String(e.reason).slice(0, 140)}</p>
              <p className="mt-0.5 text-xs text-cyan-100/60">
                {e.action} · {new Date(e.timestamp).toLocaleTimeString()} {e.task_id ? `· ${e.task_id}` : ''}
              </p>
            </li>
          ))}
        </ol>
      )}
    </section>
  );
}
