export default function AnalyticsCards({ analytics }) {
  const cards = [
    { label: 'Total Tasks', value: analytics.total_tasks || 0 },
    { label: 'Completed %', value: `${analytics.completion_rate || 0}%` },
    { label: 'Delayed', value: analytics.delayed_tasks || 0 },
    { label: 'Delays Prevented', value: analytics.delays_prevented || 0 },
    { label: 'Time Saved (hrs)', value: analytics.time_saved_hours || 0 },
    { label: 'Escalations', value: analytics.escalations_triggered || 0 },
  ];

  return (
    <section className="grid gap-3 sm:grid-cols-2 xl:grid-cols-6">
      {cards.map((card, index) => (
        <article
          key={card.label}
          className="glass animate-rise rounded-2xl p-4"
          style={{ animationDelay: `${120 + index * 70}ms` }}
        >
          <p className="font-body text-xs uppercase tracking-[0.16em] text-cyan-100/80">{card.label}</p>
          <p className="mt-2 font-display text-3xl text-white">{card.value}</p>
        </article>
      ))}
    </section>
  );
}
