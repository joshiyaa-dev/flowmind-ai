// SVG charts over live analytics: status donut + owner workload bars.
export default function AnalyticsCharts({ analytics, tasks }) {
  const completed = analytics.completed_tasks ?? 0;
  const delayed = analytics.delayed_tasks ?? 0;
  const total = analytics.total_tasks ?? 0;
  const pending = Math.max(0, total - completed - delayed);

  // Donut
  const R = 52;
  const CIRC = 2 * Math.PI * R;
  const segs = [
    { label: 'completed', value: completed, color: '#34d399' },
    { label: 'delayed', value: delayed, color: '#fb7185' },
    { label: 'pending', value: pending, color: '#fbbf24' },
  ].filter((s) => s.value > 0);
  let offset = 0;

  // Owner workload
  const byOwner = {};
  for (const t of tasks) {
    byOwner[t.owner] = (byOwner[t.owner] ?? 0) + 1;
  }
  const owners = Object.entries(byOwner).sort((a, b) => b[1] - a[1]).slice(0, 6);
  const maxOwner = Math.max(1, ...owners.map(([, n]) => n));

  return (
    <section className="grid gap-4 lg:grid-cols-2">
      <div className="glass animate-rise rounded-3xl p-5" style={{ animationDelay: '140ms' }}>
        <h3 className="mb-3 font-display text-lg font-semibold text-white">Task outcomes</h3>
        <div className="flex items-center gap-6">
          <svg viewBox="0 0 140 140" className="h-36 w-36 -rotate-90">
            <circle cx="70" cy="70" r={R} fill="none" stroke="rgba(255,255,255,0.08)" strokeWidth="16" />
            {segs.map((s) => {
              const len = (s.value / Math.max(1, total)) * CIRC;
              const el = (
                <circle
                  key={s.label}
                  cx="70" cy="70" r={R} fill="none"
                  stroke={s.color} strokeWidth="16"
                  strokeDasharray={`${len} ${CIRC - len}`}
                  strokeDashoffset={-offset}
                  strokeLinecap="butt"
                />
              );
              offset += len;
              return el;
            })}
          </svg>
          <ul className="space-y-2 text-sm">
            {[
              ['Completed', completed, '#34d399'],
              ['Pending', pending, '#fbbf24'],
              ['Delayed', delayed, '#fb7185'],
            ].map(([label, v, c]) => (
              <li key={label} className="flex items-center gap-2 text-white/90">
                <span className="h-3 w-3 rounded-full" style={{ background: c }} />
                {label}: <b>{v}</b>
              </li>
            ))}
          </ul>
        </div>
      </div>

      <div className="glass animate-rise rounded-3xl p-5" style={{ animationDelay: '210ms' }}>
        <h3 className="mb-3 font-display text-lg font-semibold text-white">Workload by owner</h3>
        {owners.length === 0 ? (
          <p className="py-8 text-center text-sm italic text-white/40">Run a meeting through the workflow to see workload.</p>
        ) : (
          <div className="space-y-2.5">
            {owners.map(([owner, n]) => (
              <div key={owner} className="flex items-center gap-3">
                <span className="w-28 truncate text-xs text-cyan-100/80">{owner.split('@')[0]}</span>
                <div className="h-4 flex-1 overflow-hidden rounded-full bg-white/10">
                  <div
                    className="h-full rounded-full bg-gradient-to-r from-cyan-400 to-emerald-400 transition-all duration-700"
                    style={{ width: `${(n / maxOwner) * 100}%` }}
                  />
                </div>
                <span className="w-6 text-right text-xs font-bold text-white">{n}</span>
              </div>
            ))}
          </div>
        )}
      </div>
    </section>
  );
}
