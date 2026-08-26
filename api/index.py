# Vercel Python serverless entrypoint.
# Wraps the FastAPI app so the WHOLE FlowMind backend deploys on Vercel —
# no separate Render/Railway service needed. MongoDB Atlas free tier supplies
# persistence via the MONGODB_URI environment variable; without it, the app
# auto-falls back to an in-memory store (transparently labeled in /health).
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BACKEND = os.path.join(ROOT, "backend")
if BACKEND not in sys.path:
    sys.path.insert(0, BACKEND)

from fastapi.middleware.cors import CORSMiddleware  # noqa: E402

from app.main import app  # noqa: E402

# Serverless origins vary; allow everything (API is read-mostly + demo).
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

handler = app  # Vercel ASGI support detects a FastAPI/ASGI callable directly
