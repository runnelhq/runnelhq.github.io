#!/usr/bin/env python3
"""Erzeugt die Unterseiten der Website aus _src/ und dem Layout von index.html.

index.html ist die Vorlage für Kopf (<head>), Symbole, Header und Footer (Abschnitte
zwischen den Markern <!-- layout:… --> und <!-- /layout:… -->). Jede Datei _src/*.html
beginnt mit einem JSON-Kommentar (Ausgabepfad, Titel, Beschreibung …) und enthält den
Inhalt von <main>. Relative Links werden an die Ordnertiefe der Zielseite angepasst.

Platzhalter im Inhalt:
  {{root}}                        Pfad zur Website-Wurzel ("" oder "../")
  {{snippet:datei|Beschriftung}}  Codeblock aus _src/snippets/datei, hervorgehoben, mit Kopieren-Button
  {{sidebar}}                     Doku-Navigation (nur bei "docs": true)
  <pre><code class="lang-go|yaml|bash|text">…</code></pre>   wird hervorgehoben und erhält einen Kopf

Referenz: _src/catalog.json und _src/expressions.json sind runnel-catalog.json und
runnel-expressions.json eines Runnel-Releases, geholt mit tools/fetch-reference.py. Daraus entstehen
der Abschnitt zwischen <!-- catalog --> und <!-- /catalog --> in index.html und die Platzhalter
{{blocks:de|en}} und {{expressions:de|en}} im Handbuch.

Aufruf (ohne Abhängigkeiten, Python 3.9+):  python3 tools/build.py
"""
import html
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "_src"

# Navigation je Bereich: (Ausgabepfad, Titel DE, Titel EN, Status) – Status None = vorhanden
DOCS_NAV = [
    ("docs/index.html", "Übersicht", "Overview", None),
    ("docs/actions.html", "Actions entwickeln", "Developing actions", None),
    ("docs/transforms.html", "Transforms entwickeln", "Developing transforms", None),
    ("docs/editor.html", "Editor entwickeln", "Developing the editor", None),
    ("docs/api.html", "Server-API", "Server API", None),
    ("docs/plugins.html", "Plugins entwickeln", "Developing plugins", None),
]
GUIDE_NAV = [
    ("handbuch/index.html", "Überblick", "Overview", None),
    ("handbuch/installation.html", "Installation", "Installation", None),
    ("handbuch/betrieb.html", "Betrieb", "Operation", None),
    ("handbuch/projekt.html", "Projekt und Konfiguration", "Project and configuration", None),
    ("handbuch/workflows.html", "Workflows", "Workflows", None),
    ("handbuch/pipelines.html", "Pipelines", "Pipelines", None),
    ("handbuch/trigger.html", "Trigger", "Triggers", None),
    ("handbuch/plugins.html", "Plugins", "Plugins", None),
    ("handbuch/ausdruecke.html", "Ausdrücke", "Expressions", None),
    ("handbuch/bausteine.html", "Bausteine (Referenz)", "Components (reference)", None),
    (None, "Kochbuch", "Cookbook", "group"),
    ("handbuch/kochbuch.html", "Grundlagen", "Basics", None),
    ("handbuch/kochbuch-open-meteo.html", "Wetter (Open-Meteo)", "Weather (Open-Meteo)", None),
    ("handbuch/kochbuch-teams.html", "Microsoft Teams", "Microsoft Teams", None),
    ("handbuch/kochbuch-github.html", "GitHub", "GitHub", None),
    ("handbuch/kochbuch-hubspot.html", "HubSpot", "HubSpot", None),
    ("handbuch/kochbuch-lexware.html", "Lexware Office", "Lexware Office", None),
    ("handbuch/kochbuch-sharepoint.html", "SharePoint (Microsoft Graph)", "SharePoint (Microsoft Graph)", None),
    ("handbuch/kochbuch-excel.html", "Excel lesen und schreiben", "Reading and writing Excel", None),
    ("handbuch/kochbuch-xml.html", "XML-Austausch", "XML exchange", None),
    ("handbuch/kochbuch-iban.html", "IBANs prüfen (Plugin)", "Validating IBANs (plugin)", None),
    ("handbuch/kochbuch-ldap.html", "Active Directory (Plugin)", "Active Directory (plugin)", None),
    ("handbuch/kochbuch-testdaten.html", "Testdaten (Plugin)", "Test data (plugin)", None),
]
SECTIONS = {
    "docs": (DOCS_NAV, "Entwicklerdoku", "Developer docs"),
    "guide": (GUIDE_NAV, "Handbuch", "User guide"),
}


def section(text, name):
    m = re.search(rf"<!-- layout:{name} -->\n(.*?)<!-- /layout:{name} -->\n", text, re.S)
    if not m:
        sys.exit(f"index.html: Marker layout:{name} fehlt")
    return m.group(1)


def rebase(fragment, root):
    """Passt relative href/src an die Tiefe der Zielseite an."""
    def fix(m):
        attr, url = m.group(1), m.group(2)
        if re.match(r"^(https?:|mailto:|data:|/|\{\{)", url):
            return m.group(0)
        if url.startswith("#"):
            if url == "#main":
                return m.group(0)
            if url.startswith("#i-") or url in ("#logo", "#flow"):
                return m.group(0)  # SVG-Symbole der eigenen Seite
            url = "index.html" + url
        return f'{attr}="{root}{url}"'
    return re.sub(r'\b(href|src)="([^"]*)"', fix, fragment)


# ---------- Syntaxhervorhebung ----------
GO_KW = r"\b(package|import|func|return|if|else|for|range|var|const|type|struct|interface|map|select|case|default|go|defer|nil|true|false|chan|break|continue|switch)\b"
LANGS = {
    "go": [("c", r"//[^\n]*"), ("s", r'"(?:\\.|[^"\\\n])*"|`[^`]*`'), ("k", GO_KW), ("n", r"\b\d+(?:\.\d+)?\b")],
    "yaml": [("c", r"(?<!\S)#[^\n]*"), ("s", r'"(?:\\.|[^"\\\n])*"'), ("t", r"^\s*-?\s*[\w.-]+(?=:)|(?<=[{,]\s)[\w.-]+(?=:)")],
    "bash": [("c", r"(?<!\S)#[^\n]*"), ("s", r'"(?:\\.|[^"\\\n])*"')],
    "text": [],
}


def highlight(code, lang):
    rules = LANGS.get(lang, [])
    if not rules:
        return html.escape(code, quote=False)
    pattern = "|".join(f"(?P<{name}{i}>{rx})" for i, (name, rx) in enumerate(rules))
    out, pos = [], 0
    for m in re.finditer(pattern, code, re.M):
        if m.start() < pos or m.end() == m.start():
            continue
        out.append(html.escape(code[pos:m.start()], quote=False))
        kind = re.sub(r"\d+$", "", m.lastgroup)
        tok = m.group(0)
        if kind == "t":  # YAML-Schlüssel: führende Einrückung/Spiegelstrich nicht einfärben
            lead = re.match(r"\s*-?\s*", tok).group(0)
            out.append(html.escape(lead, quote=False))
            tok = tok[len(lead):]
        out.append(f'<span class="tok-{kind}">{html.escape(tok, quote=False)}</span>')
        pos = m.end()
    out.append(html.escape(code[pos:], quote=False))
    return "".join(out)


_code_id = 0


def code_block(code, lang, caption=None):
    global _code_id
    _code_id += 1
    cid = f"code-{_code_id}"
    label = caption or {"go": "Go", "yaml": "YAML", "bash": "Shell", "text": ""}.get(lang, lang)
    code = code.strip("\n")
    return (
        f'<div class="code">\n'
        f'  <div class="code-head"><span>{html.escape(label)}</span>'
        f'<button class="copy-btn" type="button" data-copy-from="{cid}"><svg aria-hidden="true"><use href="#i-copy"/></svg>'
        f'<span data-i18n="ui.copy">Kopieren</span></button></div>\n'
        f'<pre id="{cid}"><code class="lang-{lang}">{highlight(code, lang)}</code></pre>\n</div>'
    )


def expand_code(content):
    def snippet(m):
        name, caption = m.group(1), m.group(2)
        path = SRC / "snippets" / name
        lang = {".go": "go", ".yaml": "yaml", ".sh": "bash", ".txt": "bash", ".json": "bash"}.get(path.suffix, "text")
        return code_block(path.read_text(encoding="utf-8"), lang, caption)
    content = re.sub(r"\{\{snippet:([^|}]+)(?:\|([^}]*))?\}\}", snippet, content)

    def pre(m):
        lang, caption, body = m.group(1), m.group(2), html.unescape(m.group(3))
        return code_block(body, lang, caption)
    return re.sub(r'<pre><code class="lang-(\w+)"(?: data-caption="([^"]*)")?>(.*?)</code></pre>', pre, content, flags=re.S)


# ---------- Referenzen aus den Daten des Programms ----------
L10N = {
    "de": {"field": "Feld", "type": "Typ", "desc": "Beschreibung", "required": "Pflicht", "default": "Standard",
           "example": "Beispiel", "values": "Werte", "none": "Keine Konfiguration.", "fn": "Funktion",
           "ctx": "Name", "actions": "Actions", "transforms": "Transforms", "connections": "Connection-Typen",
           "eg": "z. B.", "only": "Nur mit", "fields": "Felder", "under_with": "unter <code>with:</code>",
           "output": "Ergebnis", "output_sub": "in <code>result.output</code> des Schritts", "path": "Pfad",
           "set": "Gesetzte Felder", "set_sub": "an jedem weitergegebenen Datensatz",
           "placeholder": "<code>&lt;…&gt;</code> ein Name aus der Konfiguration",
           "records": "Datensätze", "errors": "Fehler", "limits": "Grenzen",
           "conn_sub": "unter <code>with:</code> der Connection-Datei", "group": "Abschnitt im Formular",
           "version": "Stand der Referenz: Runnel", "version_main": "erzeugt aus <code>main</code>, noch kein Release",
           "error_link": "Fehler-Link"},
    "en": {"field": "Field", "type": "Type", "desc": "Description", "required": "required", "default": "default",
           "example": "Example", "values": "values", "none": "No configuration.", "fn": "Function",
           "ctx": "Name", "actions": "Actions", "transforms": "Transforms", "connections": "Connection types",
           "eg": "e.g.", "only": "Only with", "fields": "Fields", "under_with": "under <code>with:</code>",
           "output": "Output", "output_sub": "in <code>result.output</code> of the step", "path": "Path",
           "set": "Fields set", "set_sub": "on every record passed on",
           "placeholder": "<code>&lt;…&gt;</code> a name from the configuration",
           "records": "Records", "errors": "Errors", "limits": "Limits",
           "conn_sub": "under <code>with:</code> of the connection file", "group": "section in the form",
           "version": "Reference as of Runnel", "version_main": "built from <code>main</code>, not yet released",
           "error_link": "error link"},
}
GROUP_DE = {"Date": "Datum", "Empty values": "Leere Werte", "Numbers and lists": "Zahlen und Listen", "Text": "Text",
            "Lists with a condition": "Listen mit Bedingung", "Conversion": "Umwandeln", "Paths": "Pfade"}

# Lesbare Typen wie helpType in runnel/web/src/help.ts (Hilfe des Editors, Mockup E15c)
HELP_FORMAT_TYPES = {"runnel-field": "field", "runnel-info-field": "field", "runnel-connection": "connection",
                     "runnel-duration": "duration"}


def help_type(s):
    if s.get("format") in HELP_FORMAT_TYPES:
        return HELP_FORMAT_TYPES[s["format"]]
    typ = s.get("type")
    if typ == "array":
        item = help_type(s["items"]) if s.get("items") else "any"
        return "list" if item == "any" else "list of " + ("lists" if item.startswith("list") else item + "s")
    if typ == "object":
        return "object" if s.get("properties") else "map"
    if typ is None:
        return "any"
    return typ


def show_value(v):
    """Ein Wert, wie er in YAML steht – wie showValue im Editor."""
    if isinstance(v, str):
        return json.dumps(v, ensure_ascii=False) if v == "" or v.strip() != v else v
    return json.dumps(v, ensure_ascii=False)


def _fields(schema, prefix=""):
    """Felder eines JSON Schemas als flache Liste (Name, Eigenschaften, Pflicht)."""
    out = []
    req = set(schema.get("required", []))
    for name, prop in (schema.get("properties") or {}).items():
        full = prefix + name
        out.append((full, prop, name in req))
        items = prop.get("items") if prop.get("type") == "array" else None
        if items and items.get("properties"):
            out += _fields(items, full + "[].")
        elif prop.get("type") == "object" and prop.get("properties"):
            out += _fields(prop, full + ".")
    return out


def _name(n):
    """Feldname mit Umbruchstellen nach jedem Punkt und an Wortgrenzen (schmale Bildschirme)."""
    return re.sub(r"(?<=[a-z0-9])(?=[A-Z])", "<wbr>", html.escape(n)).replace(".", ".<wbr>")


def _sub(title, sub, body):
    sub_html = f' <span>{sub}</span>' if sub else ""
    return f'<div class="ref-sub"><h5>{title}{sub_html}</h5>{body}</div>'


def _fields_table(schema, t, lang, conn=False):
    rows = []
    for name, prop, req in _fields(schema or {}):
        bits = []
        if req:
            bits.append(f'<span class="ref-req">{t["required"]}</span>')
        if "default" in prop:
            bits.append(f'{t["default"]}: <code>{html.escape(show_value(prop["default"]))}</code>')
        if prop.get("enum"):
            bits.append(f'{t["values"]}: ' + ", ".join(f"<code>{html.escape(show_value(v))}</code>" for v in prop["enum"]))
        if prop.get("examples"):
            bits.append(f'{t["eg"]} <code>{html.escape(show_value(prop["examples"][0]))}</code>')
        only = prop.get("x-runnel-only") or {}
        if only:
            bits.append(f'{t["only"]} <code>' + html.escape("; ".join(f'{k}: {", ".join(show_value(v) for v in vs)}' for k, vs in only.items())) + "</code>")
        if conn and prop.get("x-runnel-group"):
            bits.append(f'{t["group"]}: {html.escape(prop["x-runnel-group"])}')
        meta_html = f'<div class="ref-meta">{" · ".join(bits)}</div>' if bits else ""
        typ = html.escape(help_type(prop))
        rows.append(f'<tr><td><code>{_name(name)}</code><span class="ref-type-m">{typ}</span></td><td><code class="ref-type">{typ}</code></td>'
                    f'<td>{html.escape(prop.get("description", ""))}{meta_html}</td></tr>')
    if not rows:
        return f'<p class="legal-hint">{t["none"]}</p>'
    return (f'<div class="table-scroll"><table class="doc-table ref-table ref-table--typed"><thead><tr><th>{t["field"]}</th><th>{t["type"]}</th>'
            f'<th>{t["desc"]}</th></tr></thead><tbody>{"".join(rows)}</tbody></table></div>')


def _outputs(d, kind, t):
    outs = d.get("outputs") or []
    if not outs:
        return ""
    action = kind == "action"
    rows = "".join(f'<tr><td><code>{_name(o["name"])}</code><span class="ref-type-m">{html.escape(o.get("type", "any"))}</span></td>'
                   f'<td><code class="ref-type">{html.escape(o.get("type", "any"))}</code></td>'
                   f'<td>{html.escape(o.get("description", ""))}</td></tr>' for o in outs)
    table = (f'<div class="table-scroll"><table class="doc-table ref-table ref-table--typed"><thead><tr><th>{t["path"] if action else t["field"]}</th>'
             f'<th>{t["type"]}</th><th>{t["desc"]}</th></tr></thead><tbody>{rows}</tbody></table></div>')
    if not action and any("<" in o["name"] for o in outs):
        table += f'<p class="ref-note">{t["placeholder"]}</p>'
    return _sub(t["output"] if action else t["set"], t["output_sub"] if action else t["set_sub"], table)


def _version_line(doc, t):
    v = doc.get("version")
    if not v:
        return ""
    main = f' <span>({t["version_main"]})</span>' if re.search(r"-\d+-g[0-9a-f]+$", v) else ""
    return f'<p class="ref-version">{t["version"]} <code>{html.escape(v)}</code>{main}</p>'


def blocks_reference(lang):
    t = L10N[lang]
    path = SRC / "catalog.json"
    if not path.exists():
        return ""
    catalog = json.loads(path.read_text(encoding="utf-8"))
    both = dual_types(catalog)
    conns = sorted(catalog.get("connectionTypes") or [], key=lambda c: c["type"])
    parts = [_version_line(catalog, t)]
    jump = []
    for kind, key in (("action", "actions"), ("transform", "transforms")):
        links = "".join(f'<li{" class=\"is-dual\"" if d["type"] in both else ""}><a href="#{kind[0]}-{d["type"].replace(".", "-")}-{lang}"><code>{html.escape(d["type"])}</code>'
                        + ('<span class="dual">A+T</span>' if d["type"] in both else "") + '</a></li>'
                        for d in sorted(catalog[key], key=lambda d: d["type"]))
        jump.append(f'<p class="chips-label">{t[key]}</p><ul class="ns-list ref-jump">{links}</ul>')
    if conns:
        links = "".join(f'<li><a href="#c-{c["type"]}-{lang}"><code>{html.escape(c["type"])}</code></a></li>' for c in conns)
        jump.append(f'<p class="chips-label">{t["connections"]}</p><ul class="ns-list ref-jump">{links}</ul>')
    parts.append("".join(jump))
    for kind, key in (("action", "actions"), ("transform", "transforms")):
        parts.append(f'<h2 id="{key}-{lang}">{t[key]}</h2>')
        items = catalog[key]
        for cat in CATEGORIES[kind] + sorted({i["category"] for i in items} - set(CATEGORIES[kind])):
            members = sorted((i for i in items if i["category"] == cat), key=lambda i: i["type"])
            if not members:
                continue
            cat_name = CATEGORY_DE.get(cat, cat) if lang == "de" else cat.capitalize()
            color = CATEGORY_COLOR.get(cat, "allgemein")
            parts.append(f'<h3 class="ref-cat"><span class="tile" style="background:var(--rn-kategorie-{color})"></span>{html.escape(cat_name)}</h3>')
            for d in members:
                anchor = f'{kind[0]}-{d["type"].replace(".", "-")}-{lang}'
                body = _sub(t["fields"], t["under_with"], _fields_table(d.get("schema"), t, lang))
                body += _outputs(d, kind, t)
                if kind == "transform" and d.get("records"):
                    body += _sub(t["records"], "", f'<p>{html.escape(d["records"])}</p>')
                if d.get("errors"):
                    body += _sub(t["errors"], "", f'<p>{html.escape(d["errors"])}</p>')
                if d.get("limits"):
                    body += _sub(t["limits"], "", "<ul>" + "".join(f"<li>{html.escape(x)}</li>" for x in d["limits"]) + "</ul>")
                if d.get("example"):
                    yaml_ex = f'- id: {d["type"].split(".")[-1]}\n  type: {d["type"]}\n  with:\n' + "".join(
                        "    " + line + "\n" for line in d["example"].rstrip("\n").split("\n"))
                    body += code_block(yaml_ex, "yaml", t["example"])
                badges = ""
                if d["type"] in both:
                    other = "transform" if kind == "action" else "action"
                    other_anchor = f'{other[0]}-{d["type"].replace(".", "-")}-{lang}'
                    label = ("auch als Transform" if other == "transform" else "auch als Action") if lang == "de" \
                        else ("also a transform" if other == "transform" else "also an action")
                    badges += f'<a class="ref-badge ref-badge--dual" href="#{other_anchor}">A+T · {label}</a>'
                if d.get("recordErrors"):
                    badges += f'<span class="ref-badge">{t["error_link"]}</span>'
                if d.get("parallel"):
                    badges += '<span class="ref-badge">copies</span>'
                parts.append(f'<section class="ref-item" id="{anchor}"><h4><code>{html.escape(d["type"])}</code> '
                             f'<span>{html.escape(d["label"])}</span>{badges}</h4><p>{html.escape(d["description"])}</p>{body}</section>')
    if conns:
        parts.append(f'<h2 id="connections-{lang}">{t["connections"]}</h2>')
        for c in conns:
            body = _sub(t["fields"], t["conn_sub"], _fields_table(c.get("schema"), t, lang, conn=True))
            parts.append(f'<section class="ref-item" id="c-{c["type"]}-{lang}"><h4><code>{html.escape(c["type"])}</code> '
                         f'<span>{html.escape(c.get("label", ""))}</span></h4><p>{html.escape(c.get("description", ""))}</p>{body}</section>')
    return "\n".join(parts)


def expressions_reference(lang):
    t = L10N[lang]
    path = SRC / "expressions.json"
    if not path.exists():
        return ""
    ref = json.loads(path.read_text(encoding="utf-8"))
    def row(d, sig):
        ex = f'<div class="ref-meta"><code>{html.escape(d["example"])}</code></div>' if d.get("example") else ""
        return (f'<tr><td><code>{html.escape(sig)}</code></td><td><code>{html.escape(d.get("type", ""))}</code></td>'
                f'<td>{html.escape(d.get("description", ""))}{ex}</td></tr>')
    def table(rows, first):
        return (f'<div class="table-scroll"><table class="doc-table ref-table"><thead><tr><th>{first}</th><th>{t["type"]}</th>'
                f'<th>{t["desc"]}</th></tr></thead><tbody>{"".join(rows)}</tbody></table></div>')
    parts = [_version_line(ref, t), table([row(r, r["name"]) for r in ref["roots"]], t["ctx"])]
    groups = []
    for f in ref["functions"]:
        if f.get("group") not in groups:
            groups.append(f.get("group"))
    for g in groups:
        name = GROUP_DE.get(g, g) if lang == "de" else g
        parts.append(f'<h3>{html.escape(name)}</h3>')
        parts.append(table([row(f, f.get("signature", f["name"])) for f in ref["functions"] if f.get("group") == g], t["fn"]))
    return "\n".join(parts)


def sidebar(out_path, content, root, section="docs"):
    """Navigation des Bereichs plus „Auf dieser Seite“ aus den h2 mit id je Sprachblock."""
    nav, title_de, title_en = SECTIONS[section]
    items = []
    for path, de, en, status in nav:
        label = f'<span data-lang-block="de">{de}</span><span data-lang-block="en" hidden>{en}</span>'
        if status == "group":
            items.append(f'<li class="docs-nav-group">{label}</li>')
            continue
        if path is None:
            sde, sen = status
            items.append(f'<li><span class="docs-nav-soon">{label}'
                         f'<small><span data-lang-block="de">{sde}</span><span data-lang-block="en" hidden>{sen}</span></small></span></li>')
        else:
            href = root + path.replace("index.html", "")
            cur = ' aria-current="page"' if path == out_path else ""
            items.append(f'<li><a href="{href}"{cur}>{label}</a></li>')
    toc = []
    for lang in ("de", "en"):
        block = re.search(rf'<article[^>]*data-lang-block="{lang}"[^>]*>(.*?)</article>', content, re.S)
        if not block:
            continue
        links = "".join(f'<li><a href="#{i}">{re.sub(r"<[^>]+>", "", t)}</a></li>'
                        for i, t in re.findall(r'<h2 id="([^"]+)">(.*?)</h2>', block.group(1)))
        hidden = " hidden" if lang == "en" else ""
        toc.append(f'<ul class="docs-toc" data-lang-block="{lang}"{hidden}>{links}</ul>')
    toc_title = ('<p class="docs-side-title"><span data-lang-block="de">Auf dieser Seite</span>'
                 '<span data-lang-block="en" hidden>On this page</span></p>')
    nav_title = (f'<p class="docs-side-title"><span data-lang-block="de">{title_de}</span>'
                 f'<span data-lang-block="en" hidden>{title_en}</span></p>')
    inner = f'{nav_title}<ul class="docs-nav">{"".join(items)}</ul>{toc_title}{"".join(toc)}'
    return (
        f'<details class="docs-side docs-side--mobile"><summary><span data-lang-block="de">Inhalt</span>'
        f'<span data-lang-block="en" hidden>Contents</span></summary>{inner}</details>\n'
        f'<aside class="docs-side docs-side--desktop" aria-label="Dokumentation">{inner}</aside>'
    )


def build_page(src, layout):
    text = src.read_text(encoding="utf-8")
    m = re.match(r"\s*<!--\s*(\{.*?\})\s*-->\s*", text, re.S)
    if not m:
        sys.exit(f"{src}: JSON-Kopf fehlt")
    meta = json.loads(m.group(1))
    content = text[m.end():]
    out = meta["out"]
    root = "../" * out.count("/")

    head = layout["head"]
    head = re.sub(r"<title[^>]*>.*?</title>", f'<title>{html.escape(meta["title"]["de"])} – Runnel</title>', head)
    head = re.sub(r'<meta name="description"[^>]*>',
                  f'<meta name="description" content="{html.escape(meta["description"]["de"])}">\n'
                  f'  <meta name="title-en" content="{html.escape(meta["title"]["en"])} – Runnel">\n'
                  f'  <meta name="description-en" content="{html.escape(meta["description"]["en"])}">'
                  + ('\n  <meta name="robots" content="noindex">' if meta.get("noindex") else ""), head)
    head = re.sub(r'\s*<link rel="alternate"[^>]*>', "", head)
    head = re.sub(r'\s*<meta (?:property|name)="(?:og|twitter):[^>]*>', "", head)
    head = re.sub(r'\s*<link rel="preload" href="assets/fonts/inter-latin-700[^>]*>', "", head)
    head = rebase(head, root)

    header = rebase(layout["header"], root)
    if meta.get("nav"):
        header = header.replace(f'href="{root}{meta["nav"]}"', f'href="{root}{meta["nav"]}" aria-current="page"')
    footer = rebase(layout["footer"], root)
    sprite = rebase(layout["sprite"], root)

    content = content.replace("{{root}}", root)
    for lang in ("de", "en"):
        if "{{blocks:" + lang + "}}" in content:
            content = content.replace("{{blocks:" + lang + "}}", blocks_reference(lang))
        if "{{expressions:" + lang + "}}" in content:
            content = content.replace("{{expressions:" + lang + "}}", expressions_reference(lang))
    content = expand_code(content)
    if "{{sidebar}}" in content:
        content = content.replace("{{sidebar}}", sidebar(out, content, root, meta.get("section", "docs")))
    # Englische Blöcke bis zum Umschalten verbergen (kein Aufblitzen)
    content = re.sub(r'(data-lang-block="en")(?![^>]*\shidden)', r"\1 hidden", content)

    page = (
        f'<!doctype html>\n<html lang="de" data-theme="system">\n<head>{head}</head>\n<body>\n\n'
        f"<!-- Erzeugt von tools/build.py aus {src.relative_to(ROOT)} – nicht von Hand bearbeiten. -->\n"
        f"{sprite}\n{header}\n"
        f'<main id="main" class="{meta.get("main_class", "")}">\n{content.rstrip()}\n</main>\n\n'
        f"{footer}</body>\n</html>\n"
    )
    target = ROOT / out
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(page, encoding="utf-8")
    print(f"  {out}")


# Kategorien aus runnel catalog: (Schlüssel für i18n, CSS-Farbe der Kategorie-Kachel aus den Tokens)
CATEGORIES = {
    "action": ["general", "execution", "files", "network", "database"],
    "transform": ["input", "transform", "flow", "execution", "combine", "output"],
}
CATEGORY_DE = {
    "general": "Allgemein", "execution": "Ausführung", "files": "Dateien", "network": "Netzwerk",
    "database": "Datenbank", "input": "Eingabe", "transform": "Umformen", "flow": "Fluss",
    "combine": "Zusammenfassen", "output": "Ausgabe",
}
CATEGORY_COLOR = {
    "general": "allgemein", "execution": "ausfuehrung", "files": "dateien", "network": "netzwerk",
    "database": "datenbank", "input": "eingabe", "transform": "transformation", "flow": "fluss",
    "combine": "transformation", "output": "ausgabe",
}


def dual_types(catalog):
    """Typnamen, die es als Action und als Transform gibt (ADR 0013)."""
    return {i["type"] for i in catalog["actions"]} & {i["type"] for i in catalog["transforms"]}


def catalog_block(catalog):
    both = dual_types(catalog)
    cols = []
    for kind, key in (("action", "actions"), ("transform", "transforms")):
        items = catalog[key]
        groups = []
        known = CATEGORIES[kind] + sorted({i["category"] for i in items} - set(CATEGORIES[kind]))
        for cat in known:
            members = sorted((i for i in items if i["category"] == cat), key=lambda i: i["type"])
            if not members:
                continue
            color = CATEGORY_COLOR.get(cat, "allgemein")
            chips = "".join(
                f'<li{" class=\"is-dual\"" if i["type"] in both else ""} title="{html.escape(i["label"])}: {html.escape(i["description"])}">'
                f'<span class="tile" style="background:var(--rn-kategorie-{color})"></span>'
                f'<code>{html.escape(i["type"])}</code>'
                + ('<span class="dual" aria-label="Action und Transform" data-i18n-attr="aria-label:blocks.dualLabel">A+T</span>' if i["type"] in both else "")
                + '</li>' for i in members)
            groups.append(f'<div class="blocks-group"><h4 data-i18n="cat.{cat}">{CATEGORY_DE.get(cat, cat)}</h4><ul class="blocks-list">{chips}</ul></div>')
        title = "Actions" if kind == "action" else "Transforms"
        sub = "blocks.actions" if kind == "action" else "blocks.transforms"
        sub_de = "Schritte in Workflows" if kind == "action" else "Datensätze verarbeiten in Pipelines"
        cols.append(f'<div class="blocks-col"><h3>{title} <span class="count tnum">{len(items)}</span></h3>'
                    f'<p class="blocks-sub" data-i18n="{sub}">{sub_de}</p>{"".join(groups)}</div>')
    legend = ""
    if both:
        names = ", ".join(f"<code>{html.escape(t)}</code>" for t in sorted(both))
        legend = (f'<p class="blocks-legend"><span class="dual">A+T</span> <span data-i18n="blocks.dual">'
                  f'Gibt es als Action und als Transform – mit eigenen Feldern je Art:</span> {names}</p>')
    return '<div class="blocks">' + "".join(cols) + "</div>" + legend


def update_catalog(index):
    path = SRC / "catalog.json"
    if not path.exists() or "<!-- catalog -->" not in index:
        return index
    block = catalog_block(json.loads(path.read_text(encoding="utf-8")))
    new = re.sub(r"<!-- catalog -->.*?<!-- /catalog -->", lambda m: f"<!-- catalog -->\n{block}\n<!-- /catalog -->", index, flags=re.S)
    if new != index:
        (ROOT / "index.html").write_text(new, encoding="utf-8")
        print("  index.html (Bausteine)")
    return new


def main():
    index = (ROOT / "index.html").read_text(encoding="utf-8")
    print("tools/build.py:")
    index = update_catalog(index)
    layout = {
        "head": re.search(r"<head>(.*?)</head>", index, re.S).group(1),
        "sprite": section(index, "sprite"),
        "header": section(index, "header"),
        "footer": section(index, "footer"),
    }
    for src in sorted(SRC.glob("*.html")):
        build_page(src, layout)


if __name__ == "__main__":
    main()
