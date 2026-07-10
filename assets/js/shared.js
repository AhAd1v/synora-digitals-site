// The two <meta name="theme-color" media="(prefers-color-scheme:...)"> tags
// in every page's <head> only react to the OS-level color scheme — they
// don't know about this site's own light/dark toggle. Setting both to the
// same value makes whichever one the browser currently honors match the
// theme the user actually picked, instead of the browser chrome color
// silently disagreeing with the page after a manual toggle.
function syncThemeColorMeta(dark) {
  var color = dark ? '#1e1e47' : '#d9d9d9';
  document.querySelectorAll('meta[name="theme-color"]').forEach(function (m) {
    m.setAttribute('content', color);
  });
}
function toggleDark() {
  const dark = document.documentElement.toggleAttribute('data-dark');
  localStorage.setItem('theme', dark ? 'dark' : 'light');
  syncThemeColorMeta(dark);
}
syncThemeColorMeta(document.documentElement.hasAttribute('data-dark'));
function openMenu()  { document.getElementById('mmask').classList.add('open'); }
function closeMenu() {
  var mask = document.getElementById('mmask');
  mask.classList.add('closing');
  setTimeout(function() { mask.classList.remove('open', 'closing'); }, 195);
}
function maskClick(e){ if (e.target === e.currentTarget) closeMenu(); }

// Chips (services.html's "Popular automation requests" / "Industries we
// serve") are purely decorative tags — clicking one toggles a highlighted
// state (see shared.css's .chip.active). Only one stays lit at a time per
// .chips group: picking a new one clears whichever was previously active
// in that same section; re-clicking the active one clears it.
document.addEventListener('click', function (e) {
  var chip = e.target.closest && e.target.closest('.chip');
  if (!chip) return;
  var wasActive = chip.classList.contains('active');
  var group = chip.closest('.chips');
  if (group) {
    var actives = group.querySelectorAll('.chip.active');
    for (var i = 0; i < actives.length; i++) actives[i].classList.remove('active');
  }
  if (!wasActive) chip.classList.add('active');
});

// Sizes the hover "sheen" sweep (see shared.css's "UNIVERSAL BUTTON HOVER
// GLOW") to each button's own rendered dimensions — a wide nav pill gets a
// proportionally wider light band than a small dialog button. Geometric
// mean of width/height so both dimensions matter, not just one; clamped so
// neither a tiny icon-sized button nor a huge CTA gets a silly value.
// Chips use the same factor as every other button/pill — they share the
// full universal sheen spec (opacity/speed/blur) now, so their band has to
// be sized for the same blur radius too, not the old narrower blur-less
// sizing they had when their shine was a separate quieter variant.
function sizeSweep(targets, factor, min, max) {
  for (var i = 0; i < targets.length; i++) {
    var el = targets[i];
    var w = el.offsetWidth, h = el.offsetHeight;
    if (!w || !h) continue;
    var sweep = Math.sqrt(w * h) * factor;
    sweep = Math.max(min, Math.min(max, sweep));
    el.style.setProperty('--sweep-w', sweep + 'px');
  }
}
function sizeButtonSweeps() {
  sizeSweep(document.querySelectorAll(
    '.nav-pill, .pill-btn, .cta-btn, .submit-btn, .filepick-btn, .confirm-cancel, .confirm-proceed, .svc-plus, .chip'
  ), 1.6, 64, 360);
}
// Run at every reliable checkpoint rather than betting on one — readyState
// timing right at this <script> tag's own execution point is inconsistent,
// and content-sized buttons (.pill-btn etc., no fixed width) can still
// reflow once the custom fonts finish swapping in (font-display:block).
sizeButtonSweeps();
document.addEventListener('DOMContentLoaded', sizeButtonSweeps);
window.addEventListener('load', sizeButtonSweeps);
if (document.fonts && document.fonts.ready) { document.fonts.ready.then(sizeButtonSweeps); }
window.addEventListener('resize', function () {
  clearTimeout(window._sweepResizeTimer);
  window._sweepResizeTimer = setTimeout(sizeButtonSweeps, 150);
});
