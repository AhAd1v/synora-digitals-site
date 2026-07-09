# Synora Digitals — Consult API

A small FastAPI backend that replaces the old third-party FormSubmit.co relay. It receives the consultation form's submission, validates it server-side (never trust the client alone), rejects spam via a honeypot field, rate-limits abuse, and sends the email through [Resend](https://resend.com).

This app itself doesn't know or care where it's hosted — it can live in the same deployment as the static site (Vercel, via `api/index.py` at the project root) or run completely independently (a generic ASGI host, or cPanel).

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

Three paths — pick whichever matches the actual hosting decision. The project is currently set up for Path A (Vercel); see the root `README.md` for the exact click-by-click steps.

### Path A — Vercel (same deployment as the static site)

`api/index.py` (project root) imports this app directly — Vercel's Python runtime auto-detects the `app` ASGI variable, and `vercel.json` routes all `/api/*` requests to it. Nothing in `backend/` needs to change for this path; the root `requirements.txt` (a trimmed copy of this directory's own, see its comment) is what Vercel actually installs from.

**Known trade-off**: the rate limiter (`app/rate_limit.py`) uses in-memory state, which assumes a long-running process. Vercel serverless functions don't guarantee that — each invocation can hit a fresh, stateless instance, so the 5/hour-per-IP and 60/hour-global limits won't be perfectly enforced across cold starts. For a low-traffic consultation form this is an acceptable trade-off (the honeypot still catches most spam regardless), not a functional break — just don't expect the rate limit to be airtight on this path. If it ever needs to be airtight, that means swapping the in-memory store for something external like Upstash Redis.

### Path B — a generic ASGI host (Render, Railway, Fly.io)

The included `Procfile` is the start command:
```
web: uvicorn app.main:app --host 0.0.0.0 --port $PORT --proxy-headers
```
`--proxy-headers` is required — it's what makes uvicorn trust the platform's `X-Forwarded-For` header, which the rate limiter depends on to identify real client IPs behind the platform's edge proxy. Set the same environment variables from `.env` in the host's dashboard/secrets manager. Fly.io typically wants a Dockerfile instead of a Procfile — if that ends up being the choice, its `CMD` is the same command, just as a Docker `CMD` array.

### Path C — cPanel / Hostinger "Setup Python App"

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
3. Oversize file: attach a file over 4MB directly via `curl` (bypassing the client-side JS check entirely) and confirm the server rejects it with a 422 — this is the "never trust the client alone" check in practice.
4. Rate limit: fire 6 requests in quick succession from the same IP, confirm the 6th returns HTTP 429.
5. From the actual browser, serve the static site (not `file://`) and submit the real form, including a file attachment, and confirm the success pop-up fires and the email arrives. Then try calling the endpoint from a different origin in the browser console and confirm CORS blocks it.
6. Only after all of the above pass locally, repeat step 5 against the real deployment. On Path A (Vercel), `consult.html`'s `CONSULT_API_URL` is already a same-origin relative path (`/api/consult`) and needs no change — just update `ALLOWED_ORIGIN` to the deployed domain. On Paths B/C, both `CONSULT_API_URL` and `ALLOWED_ORIGIN` need to point at the real, separately-hosted backend URL.
