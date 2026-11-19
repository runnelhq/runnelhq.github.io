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

Aufruf (ohne Abhängigkeiten, Python 3.9+):  python3 tools/build.py
"""
import html
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "_src"

# Doku-Navigation: (Ausgabepfad, Titel DE, Titel EN, Status) – Status None = vorhanden
DOCS_NAV = [
    ("docs/index.html", "Übersicht", "Overview", None),
    ("docs/actions.html", "Actions entwickeln", "Developing actions", None),
    (None, "Transforms entwickeln", "Developing transforms", ("folgt mit S12/S13", "coming with S12/S13")),
    (None, "Plugins entwickeln", "Developing plugins", ("folgt mit S49–S51", "coming with S49–S51")),
]


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
        lang = {".go": "go", ".yaml": "yaml", ".sh": "bash", ".txt": "bash"}.get(path.suffix, "text")
        return code_block(path.read_text(encoding="utf-8"), lang, caption)
    content = re.sub(r"\{\{snippet:([^|}]+)(?:\|([^}]*))?\}\}", snippet, content)

    def pre(m):
        lang, caption, body = m.group(1), m.group(2), html.unescape(m.group(3))
        return code_block(body, lang, caption)
    return re.sub(r'<pre><code class="lang-(\w+)"(?: data-caption="([^"]*)")?>(.*?)</code></pre>', pre, content, flags=re.S)


def sidebar(out_path, content, root):
    """Doku-Navigation plus „Auf dieser Seite“ aus den h2 mit id je Sprachblock."""
    items = []
    for path, de, en, status in DOCS_NAV:
        label = f'<span data-lang-block="de">{de}</span><span data-lang-block="en" hidden>{en}</span>'
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
    nav_title = ('<p class="docs-side-title"><span data-lang-block="de">Entwicklerdoku</span>'
                 '<span data-lang-block="en" hidden>Developer docs</span></p>')
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
    content = expand_code(content)
    if "{{sidebar}}" in content:
        content = content.replace("{{sidebar}}", sidebar(out, content, root))
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


def main():
    index = (ROOT / "index.html").read_text(encoding="utf-8")
    layout = {
        "head": re.search(r"<head>(.*?)</head>", index, re.S).group(1),
        "sprite": section(index, "sprite"),
        "header": section(index, "header"),
        "footer": section(index, "footer"),
    }
    print("tools/build.py:")
    for src in sorted(SRC.glob("*.html")):
        build_page(src, layout)


if __name__ == "__main__":
    main()
