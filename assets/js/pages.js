// pages.js — interactions for the four inner pages. No dependencies.
// Everything is readable without it: rows start open-able, the Monday list
// shows its "before" state, and the first policy tab is visible.
(function () {
  document.documentElement.classList.add("js");

  // Service rows: one open at a time, like the homepage accordion.
  document.querySelectorAll(".svc-list").forEach(function (list) {
    list.querySelectorAll(".svc-r > button").forEach(function (btn) {
      btn.addEventListener("click", function () {
        var row = btn.parentElement, open = !row.classList.contains("open");
        list.querySelectorAll(".svc-r.open").forEach(function (r) {
          r.classList.remove("open"); r.querySelector("button").setAttribute("aria-expanded", "false");
        });
        if (open) { row.classList.add("open"); btn.setAttribute("aria-expanded", "true"); }
      });
    });
  });

  // Segmented switches (the Monday toggle and the policy tabs share one knob).
  function seg(el, onPick) {
    var btns = [].slice.call(el.querySelectorAll("button")), knob = el.querySelector(".knob");
    function place(b) {
      knob.style.width = b.offsetWidth + "px";
      knob.style.transform = "translateX(" + (b.offsetLeft - 4) + "px)";
    }
    function pick(b) {
      btns.forEach(function (x) { x.setAttribute("aria-pressed", x === b ? "true" : "false"); });
      place(b); onPick(btns.indexOf(b));
    }
    btns.forEach(function (b) { b.addEventListener("click", function () { pick(b); }); });
    var first = btns.filter(function (b) { return b.getAttribute("aria-pressed") === "true"; })[0] || btns[0];
    (document.fonts ? document.fonts.ready : Promise.resolve()).then(function () { place(first); });
    addEventListener("resize", function () {
      place(btns.filter(function (b) { return b.getAttribute("aria-pressed") === "true"; })[0]);
    });
  }

  var mon = document.querySelector(".mon");
  if (mon) seg(mon.querySelector(".seg"), function (i) {
    mon.classList.toggle("after", i === 1);
    var v = mon.querySelector(".mon-sum .val");
    v.textContent = i === 1 ? v.dataset.after : v.dataset.before;
    mon.querySelector(".mon-sum .lbl").textContent = i === 1 ? "Your time, with Synora" : "Your time, by hand";
  });

  var tabs = document.querySelector(".tabs .seg");
  if (tabs) seg(tabs, function (i) {
    document.querySelectorAll(".tab-p").forEach(function (p, j) { p.hidden = j !== i; });
  });
})();
