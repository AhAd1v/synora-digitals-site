import base64
import html
from typing import Optional

import httpx

from .config import settings

RESEND_URL = "https://api.resend.com/emails"


class UpstreamError(Exception):
    pass


def _row(label: str, value: str) -> str:
    return (
        f"<tr><td style='padding:4px 12px;color:#7171a7;white-space:nowrap;"
        f"vertical-align:top'>{html.escape(label)}</td>"
        f"<td style='padding:4px 12px'>{html.escape(value)}</td></tr>"
    )


def render_html(payload: dict) -> str:
    phone_val = f"{payload['country_code']} {payload['phone']}" if payload.get("phone") else "-"
    rows = "".join([
        _row("Name", payload["name"]),
        _row("Business", payload.get("business") or "-"),
        _row("Email", payload["email"]),
        _row("Phone / WhatsApp", phone_val),
        _row("What to automate", payload["message"]),
        _row("Client local time", payload.get("client_time") or "-"),
        _row("Sender IP", payload.get("ip") or "-"),
    ])
    return f"<table style='border-collapse:collapse;font-family:sans-serif'>{rows}</table>"


async def send_consult_email(
    payload: dict, attachment: Optional[tuple[str, bytes]] = None
) -> None:
    body: dict = {
        "from": settings.RESEND_FROM,
        "to": [settings.RESEND_TO],
        "reply_to": payload["email"],
        "subject": "New consultation request",
        "html": render_html(payload),
    }
    if attachment:
        filename, raw = attachment
        body["attachments"] = [
            {"filename": filename, "content": base64.b64encode(raw).decode()}
        ]

    # Explicit, bulletproof timeout — never rely on httpx's implicit default,
    # the same lesson learned from the old FormSubmit fetch() having none at
    # all and hanging indefinitely on a slow/unreachable relay.
    async with httpx.AsyncClient(timeout=10.0) as client:
        r = await client.post(
            RESEND_URL,
            headers={"Authorization": f"Bearer {settings.RESEND_API_KEY}"},
            json=body,
        )
    if r.status_code >= 400:
        raise UpstreamError(r.text)
