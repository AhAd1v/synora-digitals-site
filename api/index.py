"""Vercel's Python runtime looks for serverless functions under api/ —
this is a thin shim that imports the real FastAPI app from backend/app/main.py
so the actual application code has exactly one home, not a duplicate copy
here. Vercel's ASGI support auto-detects the `app` variable below."""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "backend"))

from app.main import app  # noqa: E402 (import must follow the sys.path insert)
