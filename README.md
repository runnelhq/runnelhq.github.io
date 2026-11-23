# runnelhq.github.io

Website von [Runnel](https://github.com/runnelhq/runnel) – **Leicht. Lokal. Im Fluss.**

Statische Seite für GitHub Pages, ohne Build-Schritt. Zweisprachig (Deutsch/Englisch), responsiv, heller und dunkler Modus.

```
index.html              # Startseite; zugleich Vorlage für Kopf, Header und Footer aller Seiten
impressum.html          # erzeugt aus _src/ (nicht von Hand bearbeiten)
datenschutz.html        # erzeugt
docs/index.html         # Entwicklerdoku: Übersicht (erzeugt)
docs/actions.html       # Entwicklerdoku: Actions entwickeln (erzeugt)
docs/transforms.html    # Entwicklerdoku: Transforms entwickeln (erzeugt)
docs/editor.html        # Entwicklerdoku: Editor entwickeln (erzeugt)
docs/api.html           # Entwicklerdoku: Server-API (erzeugt)
handbuch/*.html         # Anwenderdoku: Installation, Betrieb, Konfiguration, Workflows, Pipelines, Trigger,
                        # Ausdrücke, Bausteine (erzeugt)
_src/                   # Quellen der Unterseiten (von GitHub Pages nicht veröffentlicht)
├─ *.html               # Inhalt von <main> mit JSON-Kopf (Ausgabepfad, Titel, Beschreibung)
├─ catalog.json         # `runnel catalog --json`: Bausteine der Startseite und Referenz im Handbuch
├─ expressions.json     # `GET /api/v1/expressions` von `runnel serve`: Ausdrucks-Referenz im Handbuch
└─ snippets/            # Codebeispiele, z. B. Kopien aus runnel/internal/actions
tools/build.py          # erzeugt die Unterseiten (Python 3.9+, keine Abhängigkeiten)
favicon.svg, favicon.ico
assets/
├─ css/runnel.css       # Design Tokens – Kopie aus runnel/design/tokens/runnel.css (nicht hier ändern)
├─ css/site.css         # Seitenlayout auf Basis der Tokens
├─ js/i18n.js           # englische Texte (Schlüssel = data-i18n im HTML)
├─ js/site.js           # Sprachumschaltung, mobiles Menü, Kopieren-Buttons
├─ fonts/               # Inter, JetBrains Mono (WOFF2, Latin, SIL OFL 1.1) – lokal, keine Google-Fonts-Abfrage
└─ img/                 # Logos, Apple-Touch-Icon, Social Card aus runnel/design
```

## Unterseiten erzeugen

Header, Footer und `<head>` stehen nur in `index.html` (zwischen den Markern `<!-- layout:… -->`). Nach Änderungen
daran oder an `_src/` die Unterseiten neu erzeugen und mit committen:

```bash
python3 tools/build.py
```

Das Skript passt relative Links an die Ordnertiefe an, setzt Codeblöcke (`{{snippet:datei|Beschriftung}}` oder
`<pre><code class="lang-go">`) mit Hervorhebung und Kopieren-Button und erzeugt die Seitenleiste der Doku aus den
`<h2 id="…">` jeder Sprache. Neue Doku-Seiten in `DOCS_NAV` in `tools/build.py` eintragen.

Der Abschnitt „Bausteine“ der Startseite entsteht aus `_src/catalog.json`. Nach neuen Actions oder Transforms im
Runnel-Repository:

```bash
runnel catalog --json > _src/catalog.json
runnel serve --port 7391 . &            # in einem beliebigen Projekt
curl -s http://127.0.0.1:7391/api/v1/expressions > _src/expressions.json
python3 tools/build.py
```

Die Seiten im Handbuch nutzen dafür die Platzhalter `{{blocks:de}}`/`{{blocks:en}}` und
`{{expressions:de}}`/`{{expressions:en}}`. Die Beispiel-Dateien unter `_src/snippets/guide-*` sind mit
`runnel validate` geprüft; bei Formatänderungen in Runnel dort zuerst nachziehen.

## Lokal ansehen

```bash
python3 -m http.server 8000
```

Dann <http://localhost:8000> öffnen. Sprache per Umschalter oben rechts oder `?lang=de` / `?lang=en`
(sonst nach Browsersprache, Auswahl wird im Browser gemerkt).

## Texte ändern

- **Deutsch:** direkt in `index.html`.
- **Englisch:** in `assets/js/i18n.js` unter demselben Schlüssel wie das `data-i18n`-Attribut im HTML.
- **Längere Texte** (Doku, Rechtstexte) stehen je Sprache in einem eigenen Block `data-lang-block="de|en"` in `_src/`.
- Attribute (z. B. `aria-label`, `meta description`) über `data-i18n-attr="attribut:schlüssel"`.

## Corporate Design

Farben, Schriften, Logos und Ton stammen aus [`runnel/design`](https://github.com/runnelhq/runnel/tree/main/design).
Ändern sich dort die Tokens, `runnel.css` hierher kopieren.

## Handbuch (Anwenderdoku)

Die Seiten unter `handbuch/` beschreiben Installation, Betrieb und Konfiguration für Anwender. Grundlage sind README,
`docs/KONZEPT.md` (Kap. 2, 5, 13), die Schemas (`runnel schema …`) und die Beispiele des Runnel-Repositorys;
Bausteine und Ausdrücke sind aus dem Programm erzeugt. Neue Seiten in `GUIDE_NAV` in `tools/build.py` eintragen.

## Entwicklerdoku

Die Seiten unter `docs/` fassen die Anleitungen aus dem Runnel-Repository zusammen (`AGENTS.md`, `CONTRIBUTING.md`,
`docs/dev/ACTIONS.md`, `TRANSFORMS.md`, `EDITOR.md`, `API.md`); maßgeblich bleibt das Repository. Ändert sich dort eine Anleitung, die betroffene
Datei in `_src/` und ggf. die Codebeispiele in `_src/snippets/` nachziehen und `tools/build.py` ausführen.

## Offen (Mockup)

- Impressum und Datenschutz enthalten Platzhalter (gelb gestrichelt markiert, Klasse `ph`). Vor dem Livegang ausfüllen,
  den Hinweiskasten `legal-notice` entfernen und die Texte rechtlich prüfen lassen.
- Rechtstexte stehen je Sprache in einem eigenen Block (`data-lang-block="de|en"`); die deutsche Fassung ist maßgeblich.
- Kennzahlen und Vergleich sind Zielwerte aus dem Konzept; die Terminal-Ausgabe zeigt das geplante `runnel run`.
