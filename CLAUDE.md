# Synora Digitals — Project Reference

## What this is
Marketing website for Synora Digitals, an AI automation company.
Five static pages — no build step, no framework, no npm dependencies. The inner four were redesigned on 6 November 2026 (shorter copy, the homepage's own look carried inward) and share a second stylesheet and script on top of the shared ones:

```
index.html      ← homepage (hero, services accordion, CTA) — untouched by the redesign
services.html   ← six service rows (accordion) + "Your Monday, before and after" toggle + CTA
consult.html    ← the consultation form, one question per screen (7 steps) + "What happens next"
policies.html   ← "never" chips + three tabs: Your data / This website / Working together
about.html      ← facts strip + "How we work" (5 principles) + the team + CTA
shared.css      ← tokens, nav, footer, page-card, zig-zag separator (+ the old .pg/.icard content-page system, no longer used by any page)
assets/css/pages.css        ← the inner pages' system: .v-hero, .v-sec, .svc-list, .mon, .seg, .v-cta, .v-steps, .facts, .prin, .team/.sign, .never, .tabs, the stepped form (.qf, .st, .chip-q, .rev)
assets/js/shared.js         ← toggleDark() / openMenu() / closeMenu() / maskClick(), used by every page
assets/js/pages.js          ← inner pages: service-row accordion, the .seg knob switch (Monday toggle, policy tabs)
assets/js/consult-steps.js  ← consult only: the stepped form (see Content Pages)
assets/fonts/   ← Quera.otf, Arha Regular.otf
assets/img/     ← logo/icon SVGs (PNG copies of the logo also exist in assets/img/ but aren't referenced — leftover exports)
```

A 6th page, **`coreadmin.html`**, exists alongside these but is deliberately not one of "the five" — it's the internal login for `/coreadmin` (company staff only, `noindex`, not in `sitemap.xml`, not linked from any nav), reusing `shared.css` tokens but with its own minimal page-local styles rather than the marketing-page templates above. Its backend lives in `backend/app/coreadmin/` — see `backend/README.md`'s "Core admin" section for what's built vs. not yet built (auth + OTP only; the actual dashboard content is future work).

Each page keeps a small page-specific `<style>` block in its own `<head>` (e.g. the original consultation-form, file-drop, toast and modal styles in `consult.html`, which the stepped form still uses). Every page inlines the same `<svg><symbol id="i-*">` icon sprite as `index.html` (copied, not deduped), so any page can use the service icons.

## Color Palette

| Token | Hex | Named role |
|---|---|---|
| `--header-bg` | `#d9d9d9` | Header / nav background |
| `--primary` | `#0c0c4a` | Primary — logo, headings, body text |
| `--main-bg` | `#eeeef0` | Main page background (page spacer) |
| `--phrase` | `#6666ff` | Rotating hero phrase color |
| `--surface` | `#f5f5f7` | Hero inner + surface sections |
| `--card` | `#ffffff` | Service / pricing / step cards |
| `--accent` | alias → `--phrase` | Button gradients, accents |
| `--accent-2` | `#9090ff` | Secondary accent |
| `--accent-3` | `#b8b8ff` | Tertiary accent |
| `--muted` | `#7171a7` | Subtext, descriptions (dark: `#d9d9d9`) |
| `--faint` | `#c0c0d8` | Footer copy, very low emphasis |
| `--pill` | `#eeeef0` | Nav pill background (matches main-bg) |
| `--card-shadow` | see below | Page card box-shadow (flips in dark mode) |

Dark mode overrides all tokens via `[data-dark]` attribute on `<html>`.

### Dark mode token overrides (`[data-dark]`)
| Token | Dark value | What changed |
|---|---|---|
| `--header-bg` | `#1e1e47` | `#d9d9d9` → `#1e1e47` |
| `--primary` | `#eeeef0` | `#0c0c4a` → `#eeeef0` |
| `--main-bg` | `#0c0c1e` | `#eeeef0` → `#0c0c1e` |
| `--surface` | `#0f0f26` | `#f5f5f7` → `#0f0f26` |
| `--card` | `#181832` | `#ffffff` → `#181832` |
| `--faint` | `#303060` | `#c0c0d8` → `#303060` |
| `--pill` | `#0c0c1e` | matches dark main-bg |
| `--card-shadow` | `rgba(0,0,0,.30)` both directions | `rgba(255,255,255,.30)` → black |
| `--phrase` | `#6666ff` | unchanged |

## Typography

| Role | Font | File |
|---|---|---|
| Headings | **Quera** | `assets/fonts/Quera.otf` |
| Body / UI | **Arha** | `assets/fonts/Arha Regular.otf` |

- Both fonts use `font-display: block` — page does not render until fonts are loaded.
- Both are preloaded with `<link rel="preload">` in every page's `<head>` (not just `index.html`).
- Quera's selector list in `shared.css` is `h1–h4`, `.hero-head`, `.logo-word`, `.step-n` (the numbered-step digits on `consult.html`) — previously included five more classes (`.sec-h`, `.svc-h`, `.step-h`, `.why-h`, `.price-name`) left over from an earlier layout that never existed in any page's markup; removed as dead CSS.
- `.mmlinks a` (mobile menu links) is **not** Quera — it has no font-family override, so it inherits Arha from `body`.
- Arha is the `body` default; everything else inherits unless overridden.

## Layout Structure

Every page shares this skeleton (`body` background is `--header-bg`, the full backdrop):

```
<body>
  <nav>                        ← position:relative (scrolls away), height: --nav-h
  <div.mmask>                  ← mobile menu overlay
  [<svg><symbol id="i-*">...] ← index.html and services.html only, inline icon sprite
  <div.page-card>              ← border-radius fluid clamp ALL corners, white shadow top+bottom
    ...page-specific content (see below)...
  <footer>                     ← OUTSIDE page-card, on --header-bg body background (mirrors nav)
```

**`index.html`** (homepage) content inside `.page-card`:
```
<div.hero-inner>                    ← height = content, NOT full viewport
<div.sep>                           ← zig-zag separator
<section.svc-sec #services>         ← 6-card services accordion
<div.sep>
<section.cta-sec #contact>          ← get-in-touch icon + heading + pill → consult.html
```

**`services.html` / `consult.html` / `policies.html` / `about.html`** (inner-page template, `assets/css/pages.css`) inside `.page-card`:
```
<header.v-hero>                     ← h1 (second line in .ac accent) + one short <p>   (consult has none: the form's first question is its h1)
<section.v-sec><div.v-wrap>...      ← one block per idea (repeated)
<div.sep>                           ← zig-zag separator between blocks
...
<section.v-cta>                     ← closing heading + .v-btn.solid "Book a free consultation" (+ a plain .v-btn)
```
`.v-hero + .v-sec` has no top padding so the first block sits under the heading. The old `.page-head`/`.pg`/`.icard` classes in `shared.css` are no longer used by any page. Writing rule for these pages: short and specific — no paragraph that doesn't earn its place.

## Nav Header

- Pages: index, services, consult, policies, about (5 total). `policies.html` is a single page holding data, website-privacy and service terms as three tabs — there are no separate `privacy-policy.html` / `service-terms.html` files. Sub-pages swap their own pill for an inverted `[Home]` pill.
- Desktop: `[Services][Consult]` · logo (absolute center) · `[Policies][About][🌙]`
- Mobile: `[☰]` · logo (absolute center, same as desktop) · `[🌙]`
- Logo uses `position:absolute; left:50%; transform:translateX(-50%)` on **both** breakpoints — never reverts to static
- Nav height: `--nav-h: max(56px, 14.5svh)` web format / `max(48px, 12svh)` mobile format (see Responsive System)
- Nav is `position: relative` — **scrolls away** with the page, not sticky/fixed
- No page-spacer div; the nav sits naturally above the page card in the document flow
- Pills: white bg, pill border-radius, box-shadow
- Dark toggle: always visible; circular button inside `.nav-right`
- Logo: SVG image — `assets/img/logo-light.svg` / `assets/img/logo-dark.svg` (swapped via `[data-dark] .logo-img { content: url(...) }`)
- Logo width: `--logo-w = min(calc(var(--nav-h) * 2.013), 40vw)` — 33% of header height × 6.1 logo aspect (web); `× 1.83` = 30% of header height, cap 46vw (mobile, upsized from the design's 26.5% for phone legibility). Header icons `--icon-s`: 28% of header height (web) / 30% (mobile), floors + `--u` caps. Pills: height 32% of header, width/font capped by `--u`.

## Hero Section

- Static text: "Automated systems<br> ready to"
- Animated span `#typed` cycles through (word-atomic fade, not a character typewriter):
  1. "Eliminate Repetitive Processes."
  2. "Deliver Instant Responses."
  3. "Operate Without Bottlenecks."
- No blinking cursor. Each phrase's words are wrapped in `.dc` spans and faded in/out as whole words — words are the atomic animation unit (chosen to dodge a Safari bug where partial words could vanish permanently mid-animation).
- Timing (in `index.html`'s inline script): `HOLD` 3800ms on-screen; fade-in stagger 90ms/word, 900ms duration, 100ms extra gap per line break; fade-out stagger 60ms/word, 200ms duration, 60ms line gap. Out-animation reverses both word order within a line and line order overall.
- Every phrase is forced onto the same number of lines (`targetLines`, computed from whichever phrase needs the most lines at the current viewport) so the subtext below never shifts as phrases rotate.
- The very first phrase on page load appears instantly (no fade), so there's no blank beat under the static heading; the animation chain only starts after fonts are ready (or a 3s timeout), driven by chained `setTimeout` (no `setInterval`).

## Page Card Shadow

```css
.page-card { box-shadow: var(--card-shadow) }
/* light: 0 -7px 8px rgba(255,255,255,.30), 0 7px 8px rgba(255,255,255,.30) */
/* dark:  0 -7px 8px rgba(0,0,0,.30),       0 7px 8px rgba(0,0,0,.30)       */
```
`--card-shadow` flips automatically with dark mode. Shadow applies on **all screen sizes** (no mobile removal). `position:relative` on `.page-card` is critical so it out-paints the positioned `<nav>` in stacking order, making the top shadow visible across the full edge.

## Responsive System (per `docs/SD Responsive Layout Specification.docx`, hardened)

Two formats, switched by **aspect ratio** with a small-landscape guard — NOT a pixel breakpoint:
- **Mobile Format**: `@media (orientation: portrait), (max-width: 700px)` — nav pills hidden, hamburger shown, dark btn stays visible
- **Web Format**: everything else (landscape/square, width > 700px)

Sizing methodology:
- `--u` = 1% of a design frame fitted inside the viewport: `min(1vw, 1.7778svh)` (16:9 frame, web) / `min(1vw, .4621svh)` (390×844 frame, mobile). Same aspect ratio → identical proportions at any resolution (720p…8K). Anchored so 1366×768 and 390×844 render the pre-existing tuned design.
- Header children derive from `--nav-h` (logo 33%/30%, icons 28%/30%, pills 32% of header height — web/mobile) with px floors for legibility/touch and `--u` caps so square/short viewports can't overflow. All in `:root` tokens: `--logo-w --icon-s --pill-h --pill-w --pill-f --gap-in --gap-logo --edge`.
- `svh` with `vh` fallback (`@supports` for custom props, double declaration for normal props) — no URL-bar jump.
- `env(safe-area-inset-*)` on nav/footer; `viewport-fit=cover` in all pages' meta.
- `prefers-reduced-motion` collapses dust/menu animations; `pointer: coarse` adds invisible ::after tap-area expansion on pills/icons.
- Mini logo swap stays at `max-width: 250px`; footer legal links wrap there instead of nowrap.
- Pre-tested by calculation across 36 viewports (fit/legibility/touch/proportion checks): scratchpad pretest scripts, all pass.

## Homepage Sections (per `icons/Full design additions/` SVG designs)

1. **Hero** — compact (height = content + 2×gap, NOT full viewport). Rotating-phrase headline (see Hero Section above) + subtext only — **no buttons**. Background = page-card bg (no --surface).

**Symmetric section rhythm:** `--gap` on `.page-card` (10.45u web / 24.6u mobile) is the identical top+bottom padding of all 3 sections — so header→hero, hero→zig1, zig1→services, services→zig2, zig2→CTA, CTA→footer distances are all equal. Value = half the largest (complete − content) whitespace, measured from the CTA section. Don't give sections individual paddings.
2. **Zig-zag separator** (`.sep`, shared.css) — dotted smooth wave, accent #6666ff, gradient-masked to fade at both edges. Tile data-URIs; finer wave in mobile format.
3. **Services** (`#services`) — centered "Our Services" title + circle-arrow link (→ services.html) at right. 6 cards, accordion: 1 expanded (pill capsule = icon + name, description below) + 5 collapsed (circle capsule = icon, plus button below). Mobile: free horizontal swipe (`overflow-x`, hidden scrollbar). Cards bg --header-bg, capsules --main-bg. `--su: max(var(--u), 3.65px)` floors card scale on tiny phones (row scrolls instead of shrinking).
4. **Zig-zag separator**
5. **CTA** (`#contact`) — get-in-touch icon, 2-line heading, "Get in touch" pill (→ consult.html).
6. **Footer** — logo + nav links + copyright (not in design SVGs; kept from previous build).

**Mobile sizing note:** the mobile design artboard's element sizes are authored small; the implementation upscales Mobile Format ~1.35× (containers/icons) with text set to readability targets (body 14–16px, card names 15px, section titles 22px, hero 36px @390w, buttons ≥44px, header icons ≥28px, logo 30% of header). Keep this calibration — don't revert to raw artboard sizes.

Icons: inlined as `<symbol id="i-*">` sprites with tokenized fills (`currentColor`, `var(--phrase)`, `var(--main-bg)`) — dark mode automatic; the standalone icon files in `icons/` have slightly-off export colors, don't use them directly. `index.html` embeds the full set (service icons + `i-plus`, `i-arrow`, `i-getintouch`); `services.html` embeds a duplicate copy of just the 6 service icons (not deduped between the two files).

Every `#6666ff`/`var(--phrase)` element is animated (implemented in `shared.css`): `.plist li::before` markers and `.step-n` digits breathe (opacity pulse, staggered per list item / step via `nth-child` delays); `.icap svg` icons pop on card hover/active; `.alink` text links grow an underline on hover.

## Content Pages

All four use the inner-page template above (`pages.css` + `pages.js`). Copy is deliberately short; keep it that way.

- **`services.html`** — h1 "Six kinds of busywork. / Handled for you." Six `.svc-r` rows (Communication, Sales, Admin, Operations, Marketing, AI — icon + name + one line; one open at a time, the open one shows its examples as chips) → "Your Monday, before and after." (`.mon`: five tasks with times; the `.seg` switch flips "By hand" ↔ "With Synora", striking the tasks and swapping the total 3 h 20 min → 10 min; the times are illustrative) → CTA "Not sure which one is yours?"
- **`consult.html`** — the form, one question per screen (`form.cform.qf`, driven by `assets/js/consult-steps.js`), then "What happens next" (3 `.v-steps`: a call → a fixed proposal → built, then live). The seven steps (`.st[data-k]`):
  1. `name` — "Hi. Who's on the other side?" (required)
  2. `biz` — "Nice to meet you, {first name}. What's the business called?" — skip chip "It's just me for now"
  3. `site` — "Can we take a look at {business} online?" — skip chip "Not online yet"
  4. `areas` — "Where does the week go?" multi-select chips + hours-a-week single chips; a live line does the sum ("about N hours a month", hours × 4.3)
  5. `task` — "Which task would you happily never do again?" textarea (required) + the original file drop (≤ 4 MB, PDF/Word/Excel/CSV/text)
  6. `contact` — "Where should we reply?" email (required) + optional phone with country code (default +353)
  7. `review` — every answer with an Edit button; Edit opens just that step (Continue reads "Save") and returns straight to the review. Submit is "Send it over".

  Progress is the zig-zag wave filling with accent (`.qf-wave`, `--p`) and an "NN / 07" counter. Enter continues (⌘/Ctrl+Enter in the textarea). Each step is checked on Continue with the page's original validators (`looksLikeRealName`, `looksLikeValidEmail`, `looksLikeValidPhone`, `showFieldToast`); the final send still goes through the original `sendConsult()`/`doSend()` unchanged (all checks again, "no file attached?" confirm, 10 s timeout, server field errors, success popup + reset). A server error about an earlier step opens that step in Save mode.

  **Backend contract is unchanged** (`/api/consult`: name, business, email, country_code, phone, message, client_time, website, attachment). The extra answers are folded into `message` under the task text: `—` / `Online: …` / `Where the week goes: …` / `Hours a week: …`. **Never name a form field `website`** — that name is the honeypot; the site question uses `site`, and the hidden textarea `msg` carries the composed message.
- **`policies.html`** — h1 "Your data, in plain words." A `.never` strip (never sold / never used to train models / never reused across clients / never kept in plain text) → `.tabs` with three panels of short Q&A (`.qa`): Your data (collection, access, storage, testing, NDA, privacy law) · This website (cookies, the consultation form, how we use it, your rights) · Working together (scope and price, your part, ownership, third-party tools, fixes, ending). Fine print: "The proposal you sign is the binding document. Last updated November 2026." → CTA.
- **`about.html`** — h1 "We don't sell AI. / We sell your hours back." `.facts` (2026 founded · PK · IE · 0 middlemen) → "How we work" (5 numbered `.prin` principles) → a short line + the team (`.team` of `.sign`: Abdul Ahad — Founder; Hassan, Fahad Sheikh, Ansab Rehman — Co-founders; initials avatars, no personal emails — info@ is a general inbox) → CTA.

No `[tbd]` placeholders remain on these pages.

## Mobile Menu

Overlay card (`.mmask` + `.mmcard`) with backdrop blur. Links: Services, Consult, Policies, About (own page → Home). Closes on outside click or ✕ button.

## Dark Mode

Toggle via `toggleDark()` JS function; sets/removes `data-dark` attribute on `<html>`. All color tokens re-map in `[data-dark]` block.

## Implementation Notes

- No build step, no dependencies, no framework. Pure HTML/CSS/JS across 5 pages sharing `shared.css` / `assets/js/shared.js`.
- Font paths are relative to each page — `assets/fonts/Quera.otf` and `assets/fonts/Arha Regular.otf` must stay at that path relative to every HTML file.
- `overflow: hidden` on `.page-card` clips section backgrounds to all rounded corners.
- `<footer>` sits outside `.page-card` in the `--header-bg` body background — mirrors the nav above the card.
- `.page-card { position: relative }` is required so it out-paints the positioned nav, making the top white shadow visible along the full top edge (not just corners).
- The hero phrase rotation does NOT use `setInterval` — it's a chained `setTimeout` (`animIn` → hold → `animOut` → next phrase → `animIn`), animating whole words via CSS classes rather than typing/deleting characters.
