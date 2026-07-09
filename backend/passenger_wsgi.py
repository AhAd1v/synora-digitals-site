"""cPanel/Hostinger "Setup Python App" entry point.

That feature runs apps under Phusion Passenger, which is WSGI-oriented —
FastAPI is ASGI. a2wsgi's ASGIMiddleware bridges the two; this is the exact
convention cPanel's tooling looks for (a passenger_wsgi.py exposing an
`application` callable). Not used at all when deploying to a generic ASGI
host (Render/Railway/Fly.io) — see Procfile for that path instead.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))

from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(__file__), ".env"))

from a2wsgi import ASGIMiddleware

from app.main import app as fastapi_app

application = ASGIMiddleware(fastapi_app)
