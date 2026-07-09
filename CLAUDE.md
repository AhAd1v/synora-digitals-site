# Synora Digitals — Project Reference

## What this is
Marketing website for Synora Digitals, an AI automation company.
Five static pages sharing one stylesheet and one script file — no build step, no framework, no npm dependencies:

```
index.html      ← homepage (hero, services accordion, CTA)
services.html   ← full services list + industries + popular requests
consult.html    ← consultation form + process steps
policies.html   ← data & security / privacy policy / service terms (one page, three sections)
about.html      ← studio bio + why-work-with-us + status
shared.css      ← tokens, nav, footer, page-card, zig-zag separator, content-page (.pg/.icard/.grid2/...) system
assets/js/shared.js ← toggleDark() / openMenu() / closeMenu() / maskClick(), used by every page
assets/fonts/   ← Quera.otf, Arha Regular.otf
assets/img/     ← logo/icon SVGs (PNG copies of the logo also exist in assets/img/ but aren't referenced — leftover exports)
```

Each page keeps a small page-specific `<style>` block in its own `<head>` for layout that doesn't belong in the shared system (e.g. the consultation form styles in `consult.html`). `index.html` and `services.html` each also inline their own `<svg><symbol id="i-*">` icon sprite (duplicated between the two, not deduped) since they're the only pages that render service icons.

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

**`services.html` / `consult.html` / `policies.html` / `about.html`** (content-page template) inside `.page-card`:
```
<div.page-head>                     ← centered h1 + .pg-sub intro paragraph
<div.pg><section.pg-sec>...</div>   ← one or more content blocks (repeated)
<div.sep>                           ← zig-zag separator between each .pg block
...
<div.pg-cta>                        ← closing "Book a consultation" / "Email us" prompt
```
Content blocks use the shared `.grid2`/`.icard`/`.icap`/`.plist`/`.chips`/`.steps` system from `shared.css` — see each page for which pattern it uses (card grids on services/policies/about, numbered `.steps` + a `<form class="cform">` on consult).

## Nav Header

- Pages: index, services, consult, policies, about (5 total). `policies.html` is a single page holding three sections — a data/security card grid (untitled `h1`, "Our Policies"), "Privacy Policy", and "Service Terms" — there are no separate `privacy-policy.html` / `service-terms.html` files. Sub-pages swap their own pill for an inverted `[Home]` pill.
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

Each uses the shared `.page-head` + `.pg`/`.sep`-repeating + `.pg-cta` template (see Layout Structure).

- **`services.html`** — h1 "Our Services". Sections: full 6-card `.icard`/`.icap` grid (same 6 categories as the homepage accordion, each with a `.plist` of 5 bullet points) → "Popular automation requests" (`.chips`, 12 items) → "Industries we serve" (`.chips`, 8 items) → CTA "Book a consultation".
- **`consult.html`** — h1 "Book a Consultation". Sections: `<form class="cform">` (name/business/email/phone/message, submits via `sendConsult()` to a FormSubmit.co AJAX endpoint with IP/country/timezone lookup, falls back to a `mailto:` draft if the relay fails) → "What happens after you send it" (5-step `.steps` list) → 2-card `.icard` grid ("About pricing", "Who you'll talk to") → CTA "Email us directly" (`mailto:synoradigitals@gmail.com`).
- **`policies.html`** — h1 "Our Policies". Three sections in one page: an 8-card `.icard` grid (data collection, access, storage, "what we never do", fine-tuning, NDA, offboarding, compliance) → "Privacy Policy" (4-card grid) → "Service Terms" (6-card grid) → CTA "Book a consultation".
- **`about.html`** — h1 "About Synora Digitals". Sections: `.about-lead` intro paragraphs (page-local class, styled in an inline `<style>` block) → "Why work with us" (6-card `.icard` grid) → "Where we are today" (single `.about-lead` paragraph) → CTA "Book a consultation".

Several `<span class="tbd">[...]</span>` placeholders remain across these pages (founder/year/location on `about.html`, jurisdiction/notice-period on `policies.html`, reply time on `consult.html`) marking real content that still needs to be filled in.

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
