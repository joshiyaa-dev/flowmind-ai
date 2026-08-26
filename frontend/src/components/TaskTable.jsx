import { useState } from 'react';
import { Calendar1, Download, Pencil, Trash2, X } from 'lucide-react';

const statusColors = {
  pending: 'bg-amber-400/20 text-amber-100',
  completed: 'bg-emerald-500/20 text-emerald-100',
  delayed: 'bg-rose-500/20 text-rose-100',
};

const rowColors = {
  pending: 'bg-amber-500/10',
  completed: 'bg-emerald-600/10',
  delayed: 'bg-rose-700/20',
};

function toICSDate(d) {
  return new Date(d).toISOString().replace(/[-:]/g, '').split('.')[0] + 'Z';
}

function exportCsv(tasks) {
  const rows = [
    ['task_id', 'task', 'owner', 'deadline', 'status', 'reminders_sent', 'escalated'],
    ...tasks.map((t) => [t.task_id, t.task, t.owner, new Date(t.deadline).toISOString(), t.status, t.reminders_sent ?? 0, String(Boolean(t.escalated))]),
  ];
  const csv = rows.map((r) => r.map((c) => `"${String(c).replace(/"/g, '""')}"`).join(',')).join('\n');
  const url = URL.createObjectURL(new Blob([csv], { type: 'text/csv' }));
  const a = document.createElement('a');
  a.href = url;
  a.download = `flowmind-tasks-${new Date().toISOString().slice(0, 10)}.csv`;
  a.click();
  URL.revokeObjectURL(url);
}

function exportIcal(tasks) {
  const lines = [
    'BEGIN:VCALENDAR', 'VERSION:2.0', 'PRODID:-//FlowMind AI//Task Deadlines//EN',
  ];
  for (const t of tasks) {
    if (t.status === 'completed') continue;
    lines.push(
      'BEGIN:VEVENT',
      `UID:${t.task_id}@flowmind`,
      `DTSTAMP:${toICSDate(new Date())}`,
      `DTSTART:${toICSDate(t.deadline)}`,
      `SUMMARY:Deadline — ${t.task.replace(/\n/g, ' ')}`,
      `DESCRIPTION:Owner: ${t.owner} · Status: ${t.status}`,
      'END:VEVENT',
    );
  }
  lines.push('END:VCALENDAR');
  const url = URL.createObjectURL(new Blob([lines.join('\r\n')], { type: 'text/calendar' }));
  const a = document.createElement('a');
  a.href = url;
  a.download = `flowmind-deadlines-${new Date().toISOString().slice(0, 10)}.ics`;
  a.click();
  URL.revokeObjectURL(url);
}

/** Month-grid view of upcoming deadlines. */
function DeadlineCalendar({ tasks }) {
  const now = new Date();
  const year = now.getFullYear();
  const month = now.getMonth();
  const firstDay = (new Date(year, month, 1).getDay() + 6) % 7; // Monday-first
  const daysInMonth = new Date(year, month + 1, 0).getDate();
  const byDay = {};
  for (const t of tasks) {
    const d = new Date(t.deadline);
    if (d.getFullYear() === year && d.getMonth() === month) {
      byDay[d.getDate()] = byDay[d.getDate()] || [];
      byDay[d.getDate()].push(t);
    }
  }
  const cells = [];
  for (let i = 0; i < firstDay; i++) cells.push(null);
  for (let d = 1; d <= daysInMonth; d++) cells.push(d);

  return (
    <div className="rounded-2xl border border-white/10 bg-slate-950/40 p-4">
      <p className="mb-3 font-display text-sm font-semibold text-white">
        {now.toLocaleString('en', { month: 'long', year: 'numeric' })} — deadlines
      </p>
      <div className="grid grid-cols-7 gap-1 text-center">
        {['M', 'T', 'W', 'T', 'F', 'S', 'S'].map((d, i) => (
          <span key={i} className="text-[10px] font-bold uppercase text-cyan-100/50">{d}</span>
        ))}
        {cells.map((d, i) => (
          <div
            key={i}
            className={`min-h-[52px] rounded-lg border p-1 text-left ${
              d === null ? 'border-transparent' : byDay[d] ? 'border-cyan-300/40 bg-cyan-500/10' : 'border-white/5'
            }`}
          >
            {d && <span className="text-[10px] text-white/60">{d}</span>}
            {(byDay[d] ?? []).slice(0, 2).map((t) => (
              <p key={t.task_id} className="truncate text-[9px] font-semibold text-orange-200" title={t.task}>
                • {t.owner.split('@')[0]}
              </p>
            ))}
            {(byDay[d]?.length ?? 0) > 2 && (
              <p className="text-[9px] text-cyan-100/60">+{byDay[d].length - 2} more</p>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}

export default function TaskTable({ tasks, onStatusChange, onEditTask, onDeleteTask }) {
  const [showCalendar, setShowCalendar] = useState(false);
  const [editing, setEditing] = useState(null); // task_id being edited
  const [editForm, setEditForm] = useState({});
  const [confirmDelete, setConfirmDelete] = useState(null);

  const startEdit = (task) => {
    setEditing(task.task_id);
    setEditForm({
      title: task.task,
      owner: task.owner,
      deadline: new Date(task.deadline).toISOString().slice(0, 16),
    });
  };

  const saveEdit = () => {
    onEditTask?.(editing, editForm);
    setEditing(null);
  };

  return (
    <section className="glass animate-rise rounded-3xl p-5 sm:p-7" style={{ animationDelay: '180ms' }}>
      <div className="mb-4 flex flex-wrap items-center justify-between gap-2">
        <h2 className="font-display text-xl font-semibold text-white sm:text-2xl">Task Board</h2>
        <div className="flex items-center gap-2">
          <span className="rounded-full bg-white/10 px-3 py-1 text-xs font-semibold text-cyan-100">{tasks.length} items</span>
          <button onClick={() => setShowCalendar(!showCalendar)} className="flex items-center gap-1 rounded-full border border-white/15 bg-slate-900/60 px-3 py-1 text-xs font-bold text-cyan-100 hover:bg-slate-800">
            <Calendar1 size={12} /> {showCalendar ? 'Hide' : 'Calendar'}
          </button>
          <button onClick={() => exportCsv(tasks)} className="rounded-full border border-white/15 bg-slate-900/60 px-3 py-1 text-xs font-bold text-cyan-100 hover:bg-slate-800">CSV</button>
          <button onClick={() => exportIcal(tasks)} className="rounded-full border border-white/15 bg-slate-900/60 px-3 py-1 text-xs font-bold text-cyan-100 hover:bg-slate-800">iCal</button>
        </div>
      </div>

      {showCalendar && (
        <div className="mb-4">
          <DeadlineCalendar tasks={tasks} />
        </div>
      )}

      <div className="overflow-x-auto">
        <table className="min-w-full border-separate border-spacing-y-2 text-left text-sm">
          <thead>
            <tr className="text-cyan-50/70">
              <th className="py-2 font-body">Task</th>
              <th className="py-2 font-body">Owner</th>
              <th className="py-2 font-body">Deadline</th>
              <th className="py-2 font-body">Status</th>
              <th className="py-2 font-body">Action</th>
              <th className="py-2 font-body">Manage</th>
            </tr>
          </thead>
          <tbody>
            {tasks.map((task) =>
              editing === task.task_id ? (
                <tr key={task.task_id} className="bg-cyan-500/10">
                  <td colSpan={6} className="rounded-2xl p-3">
                    <div className="flex flex-wrap items-end gap-2">
                      <label className="text-xs text-cyan-100/70">
                        Title
                        <input value={editForm.title} onChange={(e) => setEditForm((f) => ({ ...f, title: e.target.value }))} className="mt-1 block w-56 rounded-lg border border-white/20 bg-slate-900 px-2 py-1 text-sm text-white" />
                      </label>
                      <label className="text-xs text-cyan-100/70">
                        Owner
                        <input value={editForm.owner} onChange={(e) => setEditForm((f) => ({ ...f, owner: e.target.value }))} className="mt-1 block w-40 rounded-lg border border-white/20 bg-slate-900 px-2 py-1 text-sm text-white" placeholder="email" />
                      </label>
                      <label className="text-xs text-cyan-100/70">
                        Deadline
                        <input type="datetime-local" value={editForm.deadline} onChange={(e) => setEditForm((f) => ({ ...f, deadline: e.target.value }))} className="mt-1 block rounded-lg border border-white/20 bg-slate-900 px-2 py-1 text-sm text-white" />
                      </label>
                      <button onClick={saveEdit} className="rounded-full bg-emerald-500 px-4 py-1.5 text-xs font-black text-black hover:bg-emerald-400">Save</button>
                      <button onClick={() => setEditing(null)} className="flex items-center gap-1 rounded-full bg-slate-800 px-3 py-1.5 text-xs font-bold text-white"><X size={11} /> Cancel</button>
                    </div>
                  </td>
                </tr>
              ) : (
                <tr key={task.task_id} className={`rounded-2xl ${rowColors[task.status] || 'bg-slate-950/30'}`}>
                  <td className="rounded-l-2xl p-3 text-white">{task.task}</td>
                  <td className="p-3 text-cyan-100">{task.owner}</td>
                  <td className="p-3 text-cyan-100">{new Date(task.deadline).toLocaleDateString()}</td>
                  <td className="p-3">
                    <span className={`rounded-full px-3 py-1 text-xs font-semibold ${statusColors[task.status]}`}>{task.status}</span>
                  </td>
                  <td className="p-3">
                    <select
                      value={task.status}
                      onChange={(event) => onStatusChange(task.task_id, event.target.value)}
                      className="rounded-lg border border-white/20 bg-slate-900/60 px-2 py-1 text-white outline-none"
                    >
                      <option value="pending">pending</option>
                      <option value="completed">completed</option>
                      <option value="delayed">delayed</option>
                    </select>
                  </td>
                  <td className="rounded-r-2xl p-3">
                    <div className="flex items-center gap-1.5">
                      <button onClick={() => startEdit(task)} aria-label="Edit task" className="rounded-lg bg-slate-900/60 p-1.5 text-cyan-200 hover:bg-slate-800">
                        <Pencil size={13} />
                      </button>
                      <button
                        onClick={() => {
                          if (confirmDelete === task.task_id) {
                            onDeleteTask?.(task.task_id);
                            setConfirmDelete(null);
                          } else {
                            setConfirmDelete(task.task_id);
                            setTimeout(() => setConfirmDelete(null), 3000);
                          }
                        }}
                        aria-label="Delete task"
                        className={`rounded-lg p-1.5 ${confirmDelete === task.task_id ? 'animate-pulse bg-red-600 text-white' : 'bg-slate-900/60 text-rose-300 hover:bg-slate-800'}`}
                      >
                        <Trash2 size={13} />
                      </button>
                    </div>
                  </td>
                </tr>
              ),
            )}
          </tbody>
        </table>
      </div>
    </section>
  );
}
