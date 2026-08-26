# FlowMind AI Agent — Autonomous Workflow Command Center

An agentic workflow system: ingest meeting notes → extract accountable tasks →
monitor deadlines → autonomously send reminders and escalations, with a fully
auditable reasoning trail. Deploys as **one Vercel project** (React frontend +
FastAPI serverless functions) and **degrades gracefully**: no MongoDB →
in-memory store; no LLM key → deterministic rule parser. Every mode is honestly
labeled in the UI.

## Features

| Area | What it does |
|---|---|
| Multi-agent pipeline | Understanding → Planning → Task Manager → Monitoring agents with per-step audit logs |
| Autonomous monitoring | Background loop flags overdue/inactive tasks, sends reminders (cooldown-limited), escalates to manager |
| Task management | Status updates, inline edit (title/owner/deadline), delete with confirm; optional `X-Admin-Token` protection |
| Analytics dashboard | KPI cards + SVG donut (outcomes) + owner-workload bars |
| Deadline calendar | Month grid of upcoming deadlines; CSV + iCal exports of tasks |
| Audit trail | Searchable/filterable log viewer with CSV export |
| Live agent feed | Recent reminder/escalation decisions as a polling timeline (serverless-safe, no WebSockets) |
| Meeting intake | Paste text, voice capture (Web Speech), or upload .txt/.md transcripts |
| Resilience | MongoDB auto-fallback to in-memory (`db_mode` badge); Groq/OpenAI optional, heuristic parser fallback (`llm_provider` shown) |
| Demo script | One click seeds tasks → accelerates deadlines → triggers monitoring decisions |

## Architecture

```
frontend/  React + Vite (Vercel static build)
api/index.py  FastAPI ASGI wrapper for Vercel Python functions
backend/app/
├── agents/        understanding, planning, task_manager, monitoring…
├── core/          config (pydantic-settings), database (Mongo→mongomock fallback)
├── routes/        meetings, tasks, logs, analytics, monitoring, demo
└── services/      orchestrator, llm_client (groq/openai/heuristic), notifications
```

## Run locally

```bash
# backend
cd backend
python -m venv .venv && .venv\Scripts\activate    # Windows
pip install -r requirements.txt
uvicorn app.main:app --reload                     # http://localhost:8000/api/health

# frontend
cd ../frontend
npm install
npm run dev                                       # http://localhost:5173
```

Optional env vars (see `.env.example`): `MONGODB_URI` (Atlas free tier),
`GROQ_API_KEY` / `OPENAI_API_KEY`, `ADMIN_TOKEN`, SMTP creds.

## Deploy (Vercel)

Import this repo root → Vercel auto-detects `vercel.json`: builds
`frontend/` statically and serves FastAPI at `/api/*`. Set `MONGODB_URI`
(Atlas) for persistence; set frontend env `VITE_API_BASE=/api`.

## Limitations

- Serverless functions are short-lived: the monitor loop is invoked on request/
  schedule rather than running continuously (use Vercel Cron for periodic runs).
- In-memory mode resets data on cold start (badge tells you when).
- Heuristic task extraction handles "task … owner: X deadline: YYYY-MM-DD"
  style notes; LLM providers handle open-ended text.
