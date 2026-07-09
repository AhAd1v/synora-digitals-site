# Synora Digitals — Website

Marketing website for Synora Digitals, an AI automation company.

## Stack

Five static HTML pages sharing one stylesheet (`shared.css`) and one script (`assets/js/shared.js`) — zero build step for the site itself. The consultation form is handled by a small Python (FastAPI) backend in `backend/`, deployed alongside the static site as a Vercel serverless function.

## Files

```
Synora web/
├── index.html, services.html, consult.html, policies.html, about.html   ← the 5 pages
├── shared.css                    ← design tokens, nav, footer, shared layout system
├── assets/
│   ├── fonts/                     ← Quera.otf, Arha Regular.otf (required, loaded by shared.css)
│   ├── img/                        ← logo, icon, favicon SVGs/PNGs
│   └── js/shared.js                ← toggleDark() / mobile menu / hover-sweep sizing
├── robots.txt, sitemap.xml, site.webmanifest   ← SEO/PWA infrastructure
├── api/index.py                  ← Vercel's entry point — imports the real app from backend/
├── requirements.txt              ← Vercel-specific deps for api/index.py (see its own comment)
├── vercel.json                   ← routes /api/* to api/index.py
├── backend/                      ← the actual FastAPI app + its own deployment docs
│   └── README.md                  ← local setup + all 3 deployment paths (Vercel/generic ASGI/cPanel)
├── icons/, design/, docs/         ← design reference material, not used directly by the site
├── CLAUDE.md                     ← full project reference (design tokens, layout, animation details)
└── README.md                     ← this file
```

For details on the color system, responsive sizing, hero animation, and per-page content, see **`CLAUDE.md`** — it's kept up to date with the code and is the authoritative reference.

## Deploying (Vercel + a Hostinger domain)

1. **Import the repo into Vercel** — [vercel.com](https://vercel.com) → New Project → import `AhAd1v/synora-digitals-site` from GitHub. Vercel auto-detects the static site and `api/index.py`; no build command needed.
2. **Add environment variables** before the first deploy — Vercel project → Settings → Environment Variables:
   - `RESEND_API_KEY` — from your Resend account
   - `RESEND_FROM` — `Synora Digitals <onboarding@resend.dev>` until your domain is verified with Resend (see `backend/README.md`)
   - `RESEND_TO` — `synoradigitals@gmail.com`
   - `ALLOWED_ORIGIN` — your Vercel URL for now (e.g. `https://synora-digitals-site.vercel.app`); update to the real domain once step 3 is done
3. **Deploy.** Vercel gives you a `*.vercel.app` URL immediately — test the consult form there first.
4. **Connect the Hostinger domain**: Vercel project → Settings → Domains → add your domain. Vercel shows you exactly which DNS records to add. Go to Hostinger → your domain → DNS/Nameservers, and add those records (usually an `A` record for the root domain and a `CNAME` for `www`). This can take up to a few hours to propagate.
5. Once the custom domain is live, update `ALLOWED_ORIGIN` in Vercel's environment variables to match it exactly (e.g. `https://synoradigitals.com`), and redeploy.

Full details, other deployment paths (a generic host like Render/Railway, or cPanel), and local testing steps are in `backend/README.md`.
