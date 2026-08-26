export default function NotificationPanel({ logs }) {
  const notifications = logs
    .filter((log) => ['reminder_sent', 'escalation_triggered'].includes(log.action))
    .slice(0, 8);

  return (
    <section className="glass animate-rise rounded-3xl p-5 sm:p-7" style={{ animationDelay: '220ms' }}>
      <div className="mb-4 flex items-center justify-between">
        <h2 className="font-display text-xl font-semibold text-white sm:text-2xl">Notification Delivery</h2>
        <span className="rounded-full border border-emerald-300/30 bg-emerald-500/15 px-3 py-1 text-xs font-semibold text-emerald-100">
          Email Only
        </span>
      </div>
      <div className="space-y-3">
        {notifications.length === 0 && (
          <div className="rounded-2xl border border-white/10 bg-slate-900/30 p-3 text-sm text-cyan-50/80">
            No delivery actions yet.
          </div>
        )}
        {notifications.map((log) => {
          const email = log.payload?.email;
          const delivered = email?.sent ?? (email?.ok ? 1 : 0);
          const failed = email?.failed ?? (email?.ok ? 0 : 1);
          const recipients = log.payload?.recipients || [];
          return (
            <article key={log.log_id} className="rounded-2xl border border-white/15 bg-slate-900/35 p-3">
              <p className="font-display text-sm text-white">{log.action === 'reminder_sent' ? 'Reminder sent' : 'Escalation sent'}</p>
              <p className="mt-1 text-sm text-cyan-50/90">{log.reason}</p>
              {recipients.length > 0 && (
                <p className="mt-1 text-xs text-cyan-100/75">To: {recipients.join(', ')}</p>
              )}
              <div className="mt-2 flex flex-wrap gap-2 text-[11px]">
                <span className={`rounded-full px-2 py-1 ${failed === 0 ? 'bg-emerald-500/25 text-emerald-100' : 'bg-rose-500/25 text-rose-100'}`}>
                  Email: {delivered} delivered, {failed} failed
                </span>
              </div>
            </article>
          );
        })}
      </div>
    </section>
  );
}
