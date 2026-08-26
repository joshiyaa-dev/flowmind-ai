function formatEvent(log) {
  if (log.action === 'ai_decision_made') {
    const decision = log.payload?.decision || 'none';
    const days = log.payload?.overdue_demo_days ?? 0;
    return {
      title: `AI Decision: ${decision.toUpperCase()}`,
      subtitle: `Reason: ${log.reason}`,
      badge: `Delay ${Number(days).toFixed(1)}d`,
      tone: decision === 'escalate' ? 'border-rose-400/40 bg-rose-500/10' : 'border-amber-300/40 bg-amber-400/10',
    };
  }

  if (log.action === 'reminder_sent') {
    return {
      title: `Notification: Reminder sent to ${log.payload?.owner || 'owner'}`,
      subtitle: log.reason,
      badge: 'Reminder',
      tone: 'border-sky-300/40 bg-sky-500/10',
    };
  }

  return {
    title: `Notification: Escalated to ${log.payload?.manager || 'Manager'}`,
    subtitle: log.reason,
    badge: 'Escalation',
    tone: 'border-rose-400/40 bg-rose-500/10',
  };
}

export default function AutonomyPanel({ logs }) {
  const seen = new Set();
  const visible = logs
    .filter((log) => ['ai_decision_made', 'reminder_sent', 'escalation_triggered', 'scheduled_reminder_sent'].includes(log.action))
    .filter((log) => {
      const key = `${log.task_id || 'none'}|${log.action}|${log.reason}`;
      if (seen.has(key)) return false;
      seen.add(key);
      return true;
    })
    .slice(0, 8);

  return (
    <section className="glass animate-rise rounded-3xl p-5 sm:p-7" style={{ animationDelay: '200ms' }}>
      <div className="mb-4 flex items-center justify-between">
        <h2 className="font-display text-xl font-semibold text-white sm:text-2xl">Visible Autonomy</h2>
        <span className="rounded-full border border-cyan-200/30 bg-cyan-300/10 px-3 py-1 text-xs font-semibold text-cyan-100">
          AI Acting Live
        </span>
      </div>
      <div className="space-y-3">
        {visible.length === 0 && (
          <div className="rounded-2xl border border-white/10 bg-slate-900/30 p-3 text-sm text-cyan-50/80">
            No autonomous decisions yet. Trigger a monitoring cycle or accelerate demo delay.
          </div>
        )}
        {visible.map((log) => {
          const formatted = formatEvent(log);
          return (
            <article key={log.log_id} className={`rounded-2xl border p-3 ${formatted.tone}`}>
              <div className="flex items-center justify-between gap-3">
                <p className="font-display text-sm text-white">{formatted.title}</p>
                <span className="rounded-full bg-slate-900/50 px-2 py-1 text-[10px] font-semibold uppercase tracking-[0.12em] text-cyan-100">
                  {formatted.badge}
                </span>
              </div>
              <p className="mt-1 text-sm text-cyan-50/90">{formatted.subtitle}</p>
              <p className="mt-1 text-[11px] text-cyan-50/70">{new Date(log.timestamp).toLocaleString()}</p>
            </article>
          );
        })}
      </div>
    </section>
  );
}
