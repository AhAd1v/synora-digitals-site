from slowapi import Limiter
from starlette.requests import Request


def client_ip_key(request: Request) -> str:
    """Both candidate hosts (a generic ASGI host behind Render/Railway's edge
    proxy, or cPanel/Passenger behind Apache) sit behind a reverse proxy, so
    request.client.host alone would just be the proxy's own IP for every
    request — that collapses every real visitor into one rate-limit bucket.
    Read X-Forwarded-For's first hop when present instead."""
    forwarded = request.headers.get("x-forwarded-for")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.client.host if request.client else "unknown"


# In-memory, not Redis-backed — the right trade-off for a single low-traffic
# consultation form. Known limitation (documented in README.md): state is
# per-process, so it resets on redeploy and isn't shared across multiple
# worker processes. Only worth revisiting if traffic grows enough to need
# multiple uvicorn workers.
limiter = Limiter(key_func=client_ip_key)
