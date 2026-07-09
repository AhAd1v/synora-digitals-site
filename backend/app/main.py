from typing import Optional

from fastapi import FastAPI, Request, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from slowapi.errors import RateLimitExceeded

from .config import settings
from .rate_limit import limiter, client_ip_key
from .validation import (
    is_valid_email,
    looks_like_real_name,
    is_valid_phone,
    file_extension,
    ALLOWED_EXTENSIONS,
    MAX_ATTACHMENT_BYTES,
)
from .email_service import send_consult_email, UpstreamError
from .schemas import SuccessResponse, ValidationErrorResponse, GenericErrorResponse

app = FastAPI(title="Synora Digitals — Consult API")
app.state.limiter = limiter


@app.exception_handler(RateLimitExceeded)
async def rate_limit_handler(request: Request, exc: RateLimitExceeded):
    return JSONResponse(
        status_code=429,
        content=GenericErrorResponse(
            error="rate_limited",
            message="Too many attempts — please try again later.",
        ).model_dump(),
    )


app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.ALLOWED_ORIGIN],
    allow_methods=["POST"],
    allow_headers=["*"],
    allow_credentials=False,
)


@app.post("/api/consult")
@limiter.limit("5/hour")
@limiter.limit("60/hour", key_func=lambda request: "global")
async def submit_consult(
    request: Request,
    name: str = Form(...),
    business: str = Form(""),
    email: str = Form(...),
    country_code: str = Form(...),
    phone: str = Form(""),
    message: str = Form(...),
    client_time: str = Form(""),
    website: str = Form(""),  # honeypot — must stay empty
    attachment: Optional[UploadFile] = File(None),
):
    # Honeypot: a real visitor never sees or fills this field (see the CSS
    # in consult.html — it's off-screen, not display:none, since some bots
    # specifically skip fields hidden that way). If it's filled, this was a
    # bot. Return the exact same success response a real submission would
    # get — an explicit rejection is a signal a bot's retry logic could key
    # off; silently pretending success gives it nothing to learn from.
    if website.strip():
        return SuccessResponse()

    fields: dict[str, str] = {}
    if not is_valid_email(email):
        fields["email"] = "Please enter a valid email address."
    if not looks_like_real_name(name):
        fields["name"] = "Please enter a valid name."
    if not message.strip():
        fields["message"] = "Please describe what you'd like to automate."
    if phone.strip() and not is_valid_phone(phone, country_code):
        fields["phone"] = "Please enter a valid phone number for the selected country."

    attachment_bytes: Optional[bytes] = None
    if attachment is not None and attachment.filename:
        ext = file_extension(attachment.filename)
        if ext not in ALLOWED_EXTENSIONS:
            fields["attachment"] = "Please attach a PDF, Word, Excel, CSV, or text file."
        else:
            # Read with a hard cap rather than trusting Content-Length (a
            # client can lie about that header) — this is the "never trust
            # client JS alone" requirement in practice for the file size
            # rule, which the browser already enforces but a raw request
            # bypassing the page entirely would not.
            attachment_bytes = await attachment.read(MAX_ATTACHMENT_BYTES + 1)
            if len(attachment_bytes) > MAX_ATTACHMENT_BYTES:
                fields["attachment"] = "That file is over 4MB — please attach something smaller."

    if fields:
        return JSONResponse(
            status_code=422,
            content=ValidationErrorResponse(fields=fields).model_dump(),
        )

    payload = {
        "name": name,
        "business": business,
        "email": email,
        "country_code": country_code,
        "phone": phone,
        "message": message,
        "client_time": client_time,
        "ip": client_ip_key(request),
    }
    attachment_tuple = (
        (attachment.filename, attachment_bytes)
        if attachment is not None and attachment_bytes
        else None
    )

    try:
        await send_consult_email(payload, attachment_tuple)
    except UpstreamError:
        return JSONResponse(
            status_code=502,
            content=GenericErrorResponse(
                error="upstream_error",
                message="Couldn't send right now — please try again shortly.",
            ).model_dump(),
        )

    return SuccessResponse()
