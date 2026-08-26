import { useEffect, useState } from 'react';
import { api } from './api';
import AnalyticsCards from './components/AnalyticsCards';
import AnalyticsCharts from './components/AnalyticsCharts';
import AutonomousSummary from './components/AutonomousSummary';
import AutonomyPanel from './components/AutonomyPanel';
import AuditLogPanel from './components/AuditLogPanel';
import LiveFeed from './components/LiveFeed';
import MeetingInput from './components/MeetingInput';
import NotificationPanel from './components/NotificationPanel';
import TaskTable from './components/TaskTable';

const MONITOR_INTERVAL_SECONDS = Number(import.meta.env.VITE_MONITOR_INTERVAL_SECONDS || 10);

export default function App() {
  const [tasks, setTasks] = useState([]);
  const [logs, setLogs] = useState([]);
  const [analytics, setAnalytics] = useState({});
  const [processing, setProcessing] = useState(false);
  const [banner, setBanner] = useState('System booted. Awaiting meeting input.');
  const [countdown, setCountdown] = useState(MONITOR_INTERVAL_SECONDS);
  const [lastCheck, setLastCheck] = useState(null);
  const [aiThinking, setAiThinking] = useState(false);
const [systemStatus, setSystemStatus] = useState(null);

  async function refreshAll() {
    const [taskRes, logRes, analyticsRes] = await Promise.all([
      api.getTasks(),
      api.getLogs(),
      api.getAnalytics(),
    ]);

    if (!taskRes.error) setTasks(taskRes.items || []);
    if (!logRes.error) setLogs(logRes.items || []);
    if (!analyticsRes.error) setAnalytics(analyticsRes || {});
  }

  useEffect(() => {
    refreshAll();
    api.getHealth().then((h) => { if (!h.error) setSystemStatus(h); });

    const countdownTimer = setInterval(() => {
      setCountdown((prev) => (prev <= 1 ? MONITOR_INTERVAL_SECONDS : prev - 1));
    }, 1000);

    const timer = setInterval(async () => {
      await api.runMonitoring();
      await refreshAll();
      setLastCheck(new Date());
    }, MONITOR_INTERVAL_SECONDS * 1000);

    return () => {
      clearInterval(timer);
      clearInterval(countdownTimer);
    };
  }, []);

  async function handleMeetingSubmit(payload) {
    setProcessing(true);
    const result = await api.processMeeting(payload);
    if (result.error) {
      setBanner(`Processing failed: ${result.error}`);
      setProcessing(false);
      return;
    }

    setBanner(`Meeting processed. ${result.tasks_created} tasks generated.`);
    await refreshAll();
    setProcessing(false);
  }

  async function handleStatusChange(taskId, status) {
    const res = await api.updateTaskStatus(taskId, status);
    if (res.error) {
      setBanner(`Status update failed: ${res.error}`);
      return;
    }
    setBanner(`Task ${taskId.slice(0, 8)} updated to ${status}.`);
    await refreshAll();
  }

  async function handleEditTask(taskId, fields) {
    const res = await api.editTask(taskId, fields);
    if (res.error) {
      setBanner(`Edit failed: ${res.error}`);
      return;
    }
    setBanner(`Task ${taskId.slice(0, 8)} updated (${res.updated_fields?.join(', ') ?? 'saved'}).`);
    await refreshAll();
  }

  async function handleDeleteTask(taskId) {
    const res = await api.deleteTask(taskId);
    if (res.error) {
      setBanner(`Delete failed: ${res.error}`);
      return;
    }
    setBanner(`Task ${taskId.slice(0, 8)} deleted.`);
    await refreshAll();
  }

  async function handleAccelerateDemo() {
    const result = await api.accelerateDemoDelay();
    if (result.error) {
      setBanner(`Demo acceleration failed: ${result.error}`);
      return;
    }
    setBanner('Demo mode: selected tasks pushed into delay window. AI actions incoming.');
    setAiThinking(true);
    await new Promise((resolve) => setTimeout(resolve, 1200));
    await api.runMonitoring();
    await refreshAll();
    setLastCheck(new Date());
    setCountdown(MONITOR_INTERVAL_SECONDS);
    setAiThinking(false);
  }

  async function handleRunFullDemo() {
    setBanner('Running full demo script...');
    setAiThinking(true);
    const result = await api.runFullDemo();
    if (result.error) {
      setBanner(`Full demo failed: ${result.error}`);
      setAiThinking(false);
      return;
    }
    setBanner(
      `Demo complete: ${result.tasks_created} tasks created, ${result.monitor_result?.escalations || 0} escalations triggered.`
    );
    await refreshAll();
    setLastCheck(new Date());
    setCountdown(MONITOR_INTERVAL_SECONDS);
    setAiThinking(false);
  }

  async function handleResetDemo() {
    const result = await api.resetDemoData();
    if (result.error) {
      setBanner(`Reset failed: ${result.error}`);
      return;
    }
    setBanner('Demo state reset. Clean slate ready.');
    setTasks([]);
    setLogs([]);
    setAnalytics({});
    await refreshAll();
    setLastCheck(new Date());
    setCountdown(MONITOR_INTERVAL_SECONDS);
  }

  return (
    <main className="min-h-screen bg-canvas px-4 py-6 text-white sm:px-8">
      <div className="mx-auto max-w-7xl space-y-5">
        <header className="animate-rise rounded-3xl border border-white/15 bg-slate-950/35 p-6 backdrop-blur-lg">
          <p className="font-body text-xs uppercase tracking-[0.16em] text-cyan-100/80">Agentic AI for Autonomous Enterprise Workflows</p>
          <h1 className="mt-2 font-display text-3xl sm:text-5xl">Workflow Command Center</h1>
          <p className="mt-3 rounded-2xl border border-orange-300/30 bg-orange-500/10 px-4 py-3 font-display text-sm text-orange-100 sm:text-base">
            Instead of tracking work, our system completes workflows autonomously by detecting, deciding, and acting without human intervention.
          </p>
          <p className="mt-3 max-w-3xl font-body text-sm text-cyan-50/85 sm:text-base">
            Ingest meeting notes, generate accountable tasks, monitor slippage, and let autonomous agents trigger reminders and escalations with auditable reasoning.
          </p>
          <div className="mt-4 flex flex-wrap items-center gap-3">
            {systemStatus && (
              <>
                <p
                  className={`inline-flex items-center gap-2 rounded-full px-4 py-2 text-xs font-semibold ${
                    systemStatus.db_mode === 'mongodb'
                      ? 'border border-emerald-300/30 bg-emerald-500/10 text-emerald-100'
                      : 'border border-sky-300/30 bg-sky-500/10 text-sky-100'
                  }`}
                  title={systemStatus.db_mode === 'mongodb' ? 'Connected to MongoDB' : 'No MongoDB found — running with an in-memory store. Data resets on restart.'}
                >
                  <span className="h-2 w-2 animate-pulse rounded-full bg-current" />
                  {systemStatus.db_mode === 'mongodb' ? 'Database: MongoDB' : 'Database: in-memory (auto-fallback)'}
                </p>
                <p className="inline-block rounded-full border border-white/15 bg-white/5 px-4 py-2 text-xs font-semibold text-cyan-50">
                  Task engine: {systemStatus.llm_provider === 'heuristic-parser' ? 'deterministic rule parser (offline)' : `LLM: ${systemStatus.llm_provider}`}
                </p>
              </>
            )}
            <p className="inline-block rounded-full bg-white/10 px-4 py-2 text-xs font-semibold text-orange-100">{banner}</p>
            <p className="inline-flex items-center gap-2 rounded-full border border-cyan-200/30 bg-cyan-400/10 px-4 py-2 text-xs font-semibold text-cyan-100">
              <span className="h-2 w-2 animate-pulse rounded-full bg-cyan-300" />
              Checking tasks in {countdown}s
            </p>
            {aiThinking && (
              <p className="inline-flex items-center gap-2 rounded-full border border-amber-200/30 bg-amber-500/15 px-4 py-2 text-xs font-semibold text-amber-100">
                <span className="h-2 w-2 animate-pulse rounded-full bg-amber-200" />
                AI analyzing workflow...
              </p>
            )}
            <button
              type="button"
              onClick={handleAccelerateDemo}
              className="rounded-full border border-rose-300/40 bg-rose-500/20 px-4 py-2 text-xs font-semibold uppercase tracking-[0.12em] text-rose-100 transition hover:bg-rose-500/35"
            >
              Simulate Delay Fast
            </button>
            <button
              type="button"
              onClick={handleRunFullDemo}
              className="rounded-full border border-emerald-300/40 bg-emerald-500/20 px-4 py-2 text-xs font-semibold uppercase tracking-[0.12em] text-emerald-100 transition hover:bg-emerald-500/35"
            >
              Run Full Demo
            </button>
            <button
              type="button"
              onClick={handleResetDemo}
              className="rounded-full border border-cyan-300/40 bg-cyan-500/20 px-4 py-2 text-xs font-semibold uppercase tracking-[0.12em] text-cyan-100 transition hover:bg-cyan-500/35"
            >
              Reset Demo State
            </button>
          </div>
          {lastCheck && (
            <p className="mt-2 text-xs text-cyan-50/70">Last monitoring cycle: {lastCheck.toLocaleTimeString()}</p>
          )}
        </header>

        <AnalyticsCards analytics={analytics} />
        <AnalyticsCharts analytics={analytics} tasks={tasks} />
        <AutonomousSummary analytics={analytics} />

        <section className="grid gap-5 xl:grid-cols-5">
          <div className="xl:col-span-2">
            <MeetingInput onSubmit={handleMeetingSubmit} loading={processing} />
          </div>
          <div className="space-y-5 xl:col-span-3">
            <LiveFeed logs={logs} />
            <AutonomyPanel logs={logs} />
            <NotificationPanel logs={logs} />
            <TaskTable
              tasks={tasks}
              onStatusChange={handleStatusChange}
              onEditTask={handleEditTask}
              onDeleteTask={handleDeleteTask}
            />
            <AuditLogPanel logs={logs} />
          </div>
        </section>
      </div>
    </main>
  );
}
