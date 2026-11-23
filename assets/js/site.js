(function () {
  "use strict";

  var dict = window.RUNNEL_I18N || {};
  var STORAGE_KEY = "runnel-lang";
  var SUPPORTED = ["de", "en"];
  var de = {}; // deutsche Originaltexte aus dem DOM
  var current = "de";

  function store(key, value) {
    try { localStorage.setItem(key, value); } catch (e) { /* privat/blockiert */ }
  }
  function load(key) {
    try { return localStorage.getItem(key); } catch (e) { return null; }
  }

  // Deutsche Texte einmalig sichern
  document.querySelectorAll("[data-i18n]").forEach(function (el) {
    de[el.getAttribute("data-i18n")] = el.innerHTML;
  });
  document.querySelectorAll("[data-i18n-attr]").forEach(function (el) {
    el.getAttribute("data-i18n-attr").split(";").forEach(function (pair) {
      var p = pair.split(":");
      de[p[1]] = el.getAttribute(p[0]);
    });
  });
  de["nav.open"] = de["nav.open"] || "Menü öffnen";
  de["nav.close"] = "Menü schließen";
  de["ui.copied"] = "Kopiert";

  function t(key) {
    if (current === "de") return de[key];
    return (dict[current] && dict[current][key]) || de[key];
  }

  // Unterseiten (tools/build.py): Titel und Beschreibung auf Englisch als <meta name="title-en"> usw.
  var titleEn = document.querySelector('meta[name="title-en"]');
  var descEn = document.querySelector('meta[name="description-en"]');
  var descMeta = document.querySelector('meta[name="description"]');
  var titleDe = document.title;
  var descDe = descMeta ? descMeta.getAttribute("content") : "";

  function apply(lang) {
    current = SUPPORTED.indexOf(lang) >= 0 ? lang : "de";
    document.documentElement.lang = current;
    if (titleEn) document.title = current === "en" ? titleEn.content : titleDe;
    if (descEn && descMeta) descMeta.setAttribute("content", current === "en" ? descEn.content : descDe);
    document.querySelectorAll("[data-i18n]").forEach(function (el) {
      var v = t(el.getAttribute("data-i18n"));
      if (v != null) el.innerHTML = v;
    });
    document.querySelectorAll("[data-i18n-attr]").forEach(function (el) {
      el.getAttribute("data-i18n-attr").split(";").forEach(function (pair) {
        var p = pair.split(":");
        var v = t(p[1]);
        if (v != null) el.setAttribute(p[0], v);
      });
    });
    document.querySelectorAll("[data-lang-block]").forEach(function (el) {
      el.hidden = el.getAttribute("data-lang-block") !== current;
    });
    document.querySelectorAll(".lang-switch button").forEach(function (b) {
      b.setAttribute("aria-pressed", String(b.dataset.lang === current));
    });
    var url = new URL(window.location.href);
    url.searchParams.set("lang", current);
    try { history.replaceState(null, "", url); } catch (e) { /* Sandbox */ }
  }

  function initialLang() {
    var q = new URLSearchParams(window.location.search).get("lang");
    if (q && SUPPORTED.indexOf(q) >= 0) return q;
    var saved = load(STORAGE_KEY);
    if (saved && SUPPORTED.indexOf(saved) >= 0) return saved;
    var nav = (navigator.languages && navigator.languages[0]) || navigator.language || "de";
    return nav.toLowerCase().indexOf("de") === 0 ? "de" : "en";
  }

  document.querySelectorAll(".lang-switch button").forEach(function (b) {
    b.addEventListener("click", function () {
      store(STORAGE_KEY, b.dataset.lang);
      apply(b.dataset.lang);
    });
  });

  apply(initialLang());

  // Mobile Navigation
  var toggle = document.querySelector(".menu-toggle");
  var mobile = document.getElementById("mobile-nav");
  function setMenu(open) {
    mobile.dataset.open = String(open);
    toggle.setAttribute("aria-expanded", String(open));
    toggle.setAttribute("aria-label", t(open ? "nav.close" : "nav.open"));
    toggle.querySelector("use").setAttribute("href", open ? "#i-close" : "#i-menu");
  }
  toggle.addEventListener("click", function () { setMenu(mobile.dataset.open !== "true"); });
  mobile.querySelectorAll("a").forEach(function (a) { a.addEventListener("click", function () { setMenu(false); }); });
  window.addEventListener("resize", function () { if (window.innerWidth > 1180) setMenu(false); });
  document.addEventListener("keydown", function (e) { if (e.key === "Escape") setMenu(false); });

  // Kopieren
  function copyText(text, btn) {
    var done = function () {
      btn.dataset.copied = "true";
      var label = btn.querySelector("[data-i18n]");
      var use = btn.querySelector("use");
      if (label) label.textContent = t("ui.copied");
      if (use) use.setAttribute("href", "#i-check");
      setTimeout(function () {
        btn.dataset.copied = "false";
        if (label) label.textContent = t("ui.copy");
        if (use) use.setAttribute("href", "#i-copy");
      }, 1600);
    };
    if (navigator.clipboard && navigator.clipboard.writeText) {
      navigator.clipboard.writeText(text).then(done, function () {});
    }
  }
  document.querySelectorAll("[data-copy], [data-copy-from]").forEach(function (btn) {
    btn.addEventListener("click", function () {
      var text = btn.dataset.copy;
      if (!text && btn.dataset.copyFrom) text = document.getElementById(btn.dataset.copyFrom).textContent;
      copyText(text, btn);
    });
  });
})();
