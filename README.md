<p align="center">
  <img src="docs/hero.svg" width="100%" alt="FlowMind AI Animated Hero" />
</p>

<h1 align="center">FlowMind AI</h1>

<p align="center">
  <strong>AI-Powered Productivity OS with Smart Task Routing</strong><br/>
  Combines Kanban, time-blocking, focus mode, and AI prioritization into a single flow-state productivity system.
</p>

<p align="center">
  <a href="https://capsule-render.vercel.app/api?type=waving&color=0:0a0a1a,100:6c5ce7&text=FlowMind+AI&fontSize=36&fontColor=ffffff&height=120&animation=fadeIn">
    <img src="https://capsule-render.vercel.app/api?type=waving&color=0:0a0a1a,100:6c5ce7&text=FlowMind+AI&fontSize=36&fontColor=ffffff&height=120&animation=fadeIn" />
  </a>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/React-61DAFB?style=flat-square&logo=react&logoColor=black" />
  <img src="https://img.shields.io/badge/TypeScript-3178C6?style=flat-square&logo=typescript&logoColor=white" />
  <img src="https://img.shields.io/badge/Node.js-339933?style=flat-square&logo=node.js&logoColor=white" />
  <img src="https://img.shields.io/badge/Vitest-6E9F17?style=flat-square&logo=vitest&logoColor=white" />
  <img src="https://img.shields.io/badge/Backend-Express-black?style=flat-square" />
</p>

---

### The Problem

Productivity tools force you to choose: Kanban OR calendar? Tasks OR focus? Manual OR automated? FlowMind AI unifies everything into one system that **learns your patterns** and routes you into flow state.

### What It Does

```
  ┌──────────┐     ┌──────────────┐     ┌──────────────┐
  │  Add     │────▶│  AI Priority │────▶│  Smart       │
  │  Tasks   │     │  Scoring     │     │  Scheduler   │
  └──────────┘     └──────────────┘     └──────┬───────┘
                                                │
              ┌──────────────┐           ┌──────▼───────┐
              │  Focus Mode  │◀──────────│  Time Block  │
              │  + Binaural  │           │  Generator   │
              └──────────────┘           └──────────────┘
```

### Features

| # | Feature | Description |
|---|---------|-------------|
| 1 | **Smart Inbox** | Add tasks with natural language |
| 2 | **AI Prioritization** | Urgency × importance × deadline scoring |
| 3 | **Kanban Board** | Drag-and-drop columns |
| 4 | **Time Blocking** | Auto-fills calendar with task slots |
| 5 | **Focus Mode** | Full-screen single-task with timer |
| 6 | **Binaural Beats** | Ambient audio for concentration |
| 7 | **Pomodoro +** | Adaptive intervals based on energy |
| 8 | **EOD Review** | Daily summary + tomorrow preview |
| 9 | **Weekly Analytics** | Time spent, completion rates, patterns |
| 10 | **Backend API** | Express server for data persistence |
| 11 | **Multi-Project** | Separate boards for different projects |
| 12 | **Dark Theme** | Eye-friendly dark mode default |
| 13 | **Keyboard Shortcuts** | VIM-like keybindings |
| 14 | **Export Reports** | Markdown + CSV analytics export |

### Quick Start

```bash
# Frontend
npm install
npm run dev        # → http://localhost:5173

# Backend
cd server
npm install
node index.js      # → http://localhost:4000

npm test           # tests pass
```

### Architecture

```
flowmind-ai/
├── src/
│   ├── components/    # TaskBoard, FocusTimer, Analytics
│   ├── hooks/         # useFlow, useAI, useTimer
│   ├── lib/           # Types, AI scoring, scheduler
│   └── App.tsx
├── server/
│   ├── index.js       # Express API
│   └── routes/        # tasks, projects, analytics
├── docs/hero.svg
└── package.json
```

### Data Honesty

| What we store | Where | Retention |
|---------------|-------|-----------|
| Tasks | Backend + localStorage | Until deleted |
| Focus sessions | localStorage | Session |
| Analytics | Backend | Until deleted |
| No telemetry | — | — |
| No third-party AI | — | — |
| No PII | — | — |

### Built by

**[@joshiyaa-dev](https://github.com/joshiyaa-dev)** — Flow state, engineered.

---

<p align="center">
  <img src="docs/hero.svg" width="60%" />
</p>
<p align="center">
  <sub>Stop managing tasks. Start flowing.</sub>
</p>
