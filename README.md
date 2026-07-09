# Synora Digitals — Website

Marketing website for Synora Digitals, an AI automation company.

## Stack

Zero dependencies, no build step. Five static HTML pages share one stylesheet (`shared.css`) and one script (`assets/js/shared.js`). Open any `.html` file directly in a browser.

## Files

```
Synora web/
├── index.html          ← homepage
├── services.html        ← services / industries / popular requests
├── consult.html         ← consultation form
├── policies.html        ← data & security / privacy policy / service terms
├── about.html           ← studio bio
├── shared.css           ← design tokens, nav, footer, shared layout system
├── assets/
│   ├── fonts/            ← Quera.otf, Arha Regular.otf (required, loaded by shared.css)
│   ├── img/               ← logo, icon, favicon SVGs/PNGs
│   └── js/shared.js       ← toggleDark() / mobile menu open-close
├── icons/                ← source icon exports (design reference, not used directly by the site)
├── docs/                 ← design spec docs
├── CLAUDE.md             ← full project reference (design tokens, layout, animation details)
└── README.md             ← this file
```

For details on the color system, responsive sizing, hero animation, and per-page content, see **`CLAUDE.md`** — it's kept up to date with the code and is the authoritative reference.
