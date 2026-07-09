# Synora Digitals — Consult API

A small FastAPI backend that replaces the old third-party FormSubmit.co relay. It receives the consultation form's submission, validates it server-side (never trust the client alone), rejects spam via a honeypot field, rate-limits abuse, and sends the email through [Resend](https://resend.com).

This is a separate deployable unit from the static site (`index.html` etc.) — it does not need to live in the same webroot, and can be hosted independently.

**Requires Python 3.9+** (the code uses built-in generic type hints like `dict[str, str]`, which need 3.9). If a cPanel/Hostinger "Setup Python App" slot only offers something older, that's worth checking before picking that deployment path.

## Local setup

```bash
cd backend
python -m venv venv
source venv/bin/activate   # venv\Scripts\activate on Windows
pip install -r requirements.txt
cp .env.example .env
```

Fill in `.env`:
- `RESEND_API_KEY` — from your Resend dashboard. The sandbox sender (`onboarding@resend.dev`, the `.env.example` default) works for local testing without any domain setup, but only delivers to the email address on your own Resend account.
- `RESEND_FROM` / `RESEND_TO` — see the "Resend domain verification" note below before going to production.
- `ALLOWED_ORIGIN` — the exact origin the static site is served from. **Not** `file://` — browsers don't send a matching `Origin` header for local files, which is exactly the CORS failure the old FormSubmit integration hit. Serve the static site locally instead (e.g. VS Code's Live Server extension, or `npx http-server`) and use that URL, e.g. `http://127.0.0.1:5500`.

Run it:
```bash
uvicorn app.main:app --reload --port 8000
```

## Resend domain verification (read before production)

Resend requires the `RESEND_FROM` address's domain to be verified with SPF/DKIM records in *your* DNS. You cannot set `RESEND_FROM` to `synoradigitals@gmail.com` — Gmail's domain isn't yours to add DNS records to. Until the real domain is registered and added in the Resend dashboard, keep `RESEND_FROM` pointed at the sandbox sender for testing. Once the domain exists, verify it in Resend and switch `RESEND_FROM` to something like `Synora Digitals <consult@synoradigitals.com>`.

## Deploying

Two paths, depending on where the backend ends up — pick whichever matches the actual hosting decision.

### Path A — a generic ASGI host (Render, Railway, Fly.io)

The included `Procfile` is the start command:
```
web: uvicorn app.main:app --host 0.0.0.0 --port $PORT --proxy-headers
```
`--proxy-headers` is required — it's what makes uvicorn trust the platform's `X-Forwarded-For` header, which the rate limiter depends on to identify real client IPs behind the platform's edge proxy. Set the same environment variables from `.env` in the host's dashboard/secrets manager. Fly.io typically wants a Dockerfile instead of a Procfile — if that ends up being the choice, its `CMD` is the same command, just as a Docker `CMD` array.

### Path B — cPanel / Hostinger "Setup Python App"

`passenger_wsgi.py` is the entry point cPanel's tooling expects. A few things to know:
- cPanel's Python App feature creates its own isolated app root and virtualenv **outside** `public_html` — upload this `backend/` folder there, not alongside the static HTML files.
- FastAPI is ASGI; Passenger is WSGI. `passenger_wsgi.py` bridges the two via `a2wsgi`'s `ASGIMiddleware` — this is already wired up, nothing extra to configure.
- **Before committing to this path**: some hosts restrict Python-app support (even WSGI-wrapped ASGI apps like this one) to VPS/dedicated tiers rather than entry-level shared hosting plans. Confirm the specific Hostinger/Namecheap plan actually includes "Setup Python App" before assuming this works.
- Set the same `.env` variables via cPanel's Python App environment-variable UI (or by keeping the `.env` file itself in the app root — `passenger_wsgi.py` already loads it via `python-dotenv`).

## Testing end-to-end

1. With the backend running locally (`uvicorn app.main:app --reload --port 8000`):
   ```bash
   curl -X POST http://127.0.0.1:8000/api/consult \
     -F "name=Jane Doe" -F "email=jane@example.com" -F "country_code=+92" \
     -F "phone=3001234567" -F "message=Need help automating invoicing." \
     -F "website=" -F "attachment=@sample.pdf"
   ```
   Expect `{"ok": true}` and a real email arriving (at `RESEND_TO`, or your Resend account's own address if using the sandbox sender), attachment intact.
2. Honeypot: repeat with `-F "website=bot-filled-this"` — still `{"ok": true}` HTTP 200, but confirm via the Resend dashboard that no email was actually sent for that request.
3. Oversize file: attach a file over 10MB directly via `curl` (bypassing the client-side JS check entirely) and confirm the server rejects it with a 422 — this is the "never trust the client alone" check in practice.
4. Rate limit: fire 6 requests in quick succession from the same IP, confirm the 6th returns HTTP 429.
5. From the actual browser, serve the static site (not `file://`) and submit the real form, including a file attachment, and confirm the success pop-up fires and the email arrives. Then try calling the endpoint from a different origin in the browser console and confirm CORS blocks it.
6. Only after all of the above pass locally, repeat step 5 against the real deployed backend URL, with `consult.html`'s fetch URL and `ALLOWED_ORIGIN` both updated to the real production values.
