import asyncio
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.agents.monitoring_agent import MonitoringAgent
from app.core.config import get_settings
from app.core.database import get_db, mongo_manager
from app.routes.analytics import router as analytics_router
from app.routes.demo import router as demo_router
from app.routes.logs import router as logs_router
from app.routes.meetings import router as meetings_router
from app.routes.monitoring import router as monitoring_router
from app.routes.tasks import router as tasks_router


monitor_task: asyncio.Task | None = None


async def monitoring_loop() -> None:
    settings = get_settings()
    while True:
        try:
            agent = MonitoringAgent()
            await agent.run_cycle(settings.inactivity_hours)
        except Exception:
            # Monitoring failures are isolated to keep API available.
            pass
        await asyncio.sleep(settings.monitor_interval_seconds)


@asynccontextmanager
async def lifespan(_: FastAPI):
    global monitor_task

    db = get_db()
    try:
        await db["tasks"].create_index("task_id", unique=True)
        await db["tasks"].create_index("deadline")
        await db["tasks"].create_index("status")
        await db["audit_logs"].create_index("timestamp")
    except Exception:
        # Index creation must never prevent the API from starting.
        pass

    monitor_task = asyncio.create_task(monitoring_loop())
    yield

    if monitor_task:
        monitor_task.cancel()
        try:
            await monitor_task
        except asyncio.CancelledError:
            pass
    await mongo_manager.close()


settings = get_settings()
app = FastAPI(title=settings.app_name, lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
async def health() -> dict:
    return {
        "ok": True,
        "service": settings.app_name,
        "db_mode": mongo_manager.db_mode,
        "llm_provider": settings.llm_provider if (settings.groq_api_key or settings.openai_api_key) else "heuristic-parser",
    }


app.include_router(meetings_router, prefix=settings.api_prefix)
app.include_router(tasks_router, prefix=settings.api_prefix)
app.include_router(logs_router, prefix=settings.api_prefix)
app.include_router(analytics_router, prefix=settings.api_prefix)
app.include_router(monitoring_router, prefix=settings.api_prefix)
app.include_router(demo_router, prefix=settings.api_prefix)
