export default function AutonomousSummary({ analytics }) {
  const rows = [
    ['Tasks Created Automatically', analytics.total_tasks || 0],
    ['Delays Prevented', analytics.delays_prevented || 0],
    ['Escalations Triggered', analytics.escalations_triggered || 0],
    ['Hours Saved', analytics.time_saved_hours || 0],
  ];

  return (
    <section className="glass animate-rise rounded-3xl p-5 sm:p-7" style={{ animationDelay: '160ms' }}>
      <h2 className="font-display text-xl font-semibold text-white sm:text-2xl">Autonomous Actions Summary</h2>
      <div className="mt-4 grid gap-2 sm:grid-cols-2">
        {rows.map(([label, value]) => (
          <div key={label} className="rounded-2xl border border-white/10 bg-slate-900/35 p-3">
            <p className="text-xs uppercase tracking-[0.14em] text-cyan-100/75">{label}</p>
            <p className="mt-1 font-display text-2xl text-white">{value}</p>
          </div>
        ))}
      </div>
    </section>
  );
}
