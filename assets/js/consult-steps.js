// consult-steps.js — the consultation form, one question at a time.
// Loaded after consult.html's own script, whose globals it reuses:
// looksLikeRealName, looksLikeValidEmail, looksLikeValidPhone,
// showFieldToast, sendConsult, attachmentInput. The backend is unchanged:
// the extra answers (site, areas, hours) are folded into `message`.
(function () {
  var form = document.querySelector(".qf");
  if (!form) return;
  var steps = [].slice.call(form.querySelectorAll(".st"));
  var count = form.querySelector(".qf-count b");
  var wave = form.querySelector(".qf-wave");
  var back = form.querySelector(".qf-back");
  var next = form.querySelector(".qf-next");
  var send = form.querySelector(".submit-btn");
  var at = 0, started = false, editing = false;
  var REVIEW = steps.length - 1;

  function pad(n) { return (n < 10 ? "0" : "") + n; }
  function val(n) { return (form[n] && form[n].value || "").trim(); }
  function first() { return val("name").split(/\s+/)[0] || ""; }
  function picked(key) {
    return [].slice.call(form.querySelectorAll('[data-' + (key === "hours" ? "one" : "multi") + '="' + key + '"] [aria-pressed="true"]'))
      .map(function (b) { return b.textContent.trim(); });
  }

  // Fill the visitor's own words into later headings.
  function personalise() {
    form.querySelectorAll('[data-fill="first"]').forEach(function (el) {
      if (!el.dataset.def) el.dataset.def = el.textContent;
      el.textContent = first() || el.dataset.def;
    });
    form.querySelectorAll('[data-fill="biz"]').forEach(function (el) {
      if (!el.dataset.def) el.dataset.def = el.textContent;
      el.textContent = val("biz") || el.dataset.def;
    });
  }

  function focusStep(st) {
    var el = st.querySelector("input:not([type=file]):not([type=hidden]), textarea, .chip-q");
    if (el && matchMedia("(pointer: fine)").matches) setTimeout(function () { el.focus({ preventScroll: true }); }, 60);
  }

  function show(i, dir) {
    steps[at].classList.remove("on", "back");
    at = Math.max(0, Math.min(steps.length - 1, i));
    var st = steps[at];
    st.classList.toggle("back", dir < 0);
    st.classList.add("on");
    count.textContent = pad(at + 1);
    wave.style.setProperty("--p", ((at + 1) / steps.length) * 100 + "%");
    back.hidden = at === 0;
    var last = at === steps.length - 1;
    next.hidden = last; send.hidden = !last;
    if (last) editing = false;
    next.textContent = editing ? "Save" : "Continue";
    if (editing) back.hidden = true;
    personalise();
    if (st.dataset.k === "review") buildReview();
    if (typeof syncFiledropAnts === "function") setTimeout(syncFiledropAnts, 30);
    var top = form.getBoundingClientRect().top;
    if (started && (top < 0 || top > innerHeight * .6)) form.scrollIntoView({ behavior: "smooth", block: "start" });
    if (started) focusStep(st);
    started = true;
  }

  // Each step's own check; a toast points at the field, as before.
  function ok(st) {
    var k = st.dataset.k;
    if (k === "name" && !looksLikeRealName(form.name.value)) { showFieldToast(form.name, "Just your name is fine, letters only."); return false; }
    if (k === "task" && !val("task")) { showFieldToast(form.task, "A sentence or two is enough."); return false; }
    if (k === "contact") {
      if (!looksLikeValidEmail(form.email.value)) { showFieldToast(form.email, "That email doesn’t look quite right."); return false; }
      if (val("phone") && !looksLikeValidPhone(form.phone.value, form.countryCode.value)) {
        showFieldToast(form.phone.closest(".phone-field") || form.phone, "Please check the number for the selected country."); return false;
      }
    }
    return true;
  }

  // Editing from the review screen: one step only, then straight back.
  function go(d) {
    if (d > 0 && !ok(steps[at])) return;
    show(editing ? REVIEW : at + d, d);
  }
  function edit(i) { editing = i !== REVIEW; show(i, -1); }
  next.addEventListener("click", function () { go(1); });
  back.addEventListener("click", function () { go(-1); });
  form.querySelectorAll("[data-skip]").forEach(function (b) {
    b.addEventListener("click", function () {
      var inp = b.closest(".st").querySelector(".big-in"); if (inp) inp.value = "";
      go(1);
    });
  });

  // Enter moves on; in the task box it needs Cmd/Ctrl.
  form.addEventListener("keydown", function (e) {
    if (e.key !== "Enter" || e.isComposing) return;
    var t = e.target;
    if (t.tagName === "TEXTAREA" && !(e.metaKey || e.ctrlKey)) return;
    if (t.tagName === "BUTTON" && t.type !== "submit" && !t.classList.contains("chip-q")) return;
    if (t.classList.contains("chip-q")) return;
    e.preventDefault();
    if (at === steps.length - 1) send.click(); else go(1);
  });

  // Chips: many for areas, one for hours, and a line that does the sum.
  form.querySelectorAll("[data-multi] .chip-q").forEach(function (b) {
    b.addEventListener("click", function () { b.setAttribute("aria-pressed", b.getAttribute("aria-pressed") === "true" ? "false" : "true"); });
  });
  var say = form.querySelector(".hours-say");
  form.querySelectorAll("[data-one] .chip-q").forEach(function (b) {
    b.addEventListener("click", function () {
      b.parentElement.querySelectorAll(".chip-q").forEach(function (x) { x.setAttribute("aria-pressed", x === b ? "true" : "false"); });
      var h = +b.dataset.h;
      say.innerHTML = h ? "That&rsquo;s about <b>" + Math.round(h * 4.3) + " hours a month</b> we could look at handing back."
                        : "No problem. Finding out is part of the first call.";
    });
  });

  function esc(s) { var d = document.createElement("div"); d.textContent = s; return d.innerHTML; }
  function buildReview() {
    var file = attachmentInput && attachmentInput.files[0];
    var rows = [
      ["Name", val("name"), 0],
      ["Business", val("biz"), 1],
      ["Online", val("site"), 2],
      ["Where the week goes", picked("areas").join(", "), 3],
      ["Hours a week", picked("hours").join(""), 3],
      ["The task", val("task") + (file ? "\n+ " + file.name : ""), 4],
      ["Reply to", [val("email"), val("phone") ? form.countryCode.value + " " + val("phone") : ""].filter(Boolean).join("\n"), 5]
    ];
    form.querySelector(".rev").innerHTML = rows.map(function (r) {
      return "<li><b>" + r[0] + "</b>" + (r[1] ? "<span>" + esc(r[1]) + "</span>" : '<span class="none">Skipped</span>') +
        '<button type="button" data-to="' + r[2] + '">Edit</button></li>';
    }).join("");
  }
  form.querySelector(".rev").addEventListener("click", function (e) {
    var b = e.target.closest("[data-to]"); if (b) edit(+b.dataset.to);
  });

  // A server-side complaint about a field on an earlier step: go there first.
  var toast = window.showFieldToast;
  window.showFieldToast = function (el, msg) {
    var st = el && el.closest && el.closest(".st");
    if (st && !st.classList.contains("on")) { edit(steps.indexOf(st)); setTimeout(function () { toast(el, msg); }, 350); }
    else toast(el, msg);
  };

  // Fold the extra answers into the one message the backend reads.
  window.qfSubmit = function (f) {
    for (var i = 0; i < steps.length - 1; i++) if (!ok(steps[i])) { edit(i); return false; }
    var extra = [];
    if (val("site")) extra.push("Online: " + val("site"));
    if (picked("areas").length) extra.push("Where the week goes: " + picked("areas").join(", "));
    if (picked("hours").length) extra.push("Hours a week: " + picked("hours")[0]);
    f.msg.value = val("task") + (extra.length ? "\n\n—\n" + extra.join("\n") : "");
    return sendConsult(f);
  };

  // After a successful send the page script resets the form: start over.
  var reset = form.reset.bind(form);
  form.reset = function () {
    reset();
    form.querySelectorAll(".chip-q[aria-pressed]").forEach(function (b) { b.setAttribute("aria-pressed", "false"); });
    say.textContent = "";
    editing = false;
    show(0, -1);
  };

  show(0, 1);
})();
