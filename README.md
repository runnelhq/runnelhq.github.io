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
docs/plugins.html       # Entwicklerdoku: Plugins entwickeln (erzeugt)
handbuch/*.html         # Anwenderdoku: Installation, Betrieb, Konfiguration, Workflows, Pipelines, Trigger,
                        # Ausdrücke, Bausteine, Plugins, Kochbuch (erzeugt)
_src/                   # Quellen der Unterseiten (von GitHub Pages nicht veröffentlicht)
├─ *.html               # Inhalt von <main> mit JSON-Kopf (Ausgabepfad, Titel, Beschreibung)
├─ catalog.json         # runnel-catalog.json eines Releases: Bausteine der Startseite und Referenz im Handbuch
├─ expressions.json     # runnel-expressions.json eines Releases: Ausdrucks-Referenz im Handbuch
├─ kochbuch/            # Rezepte des Kochbuchs als lauffähige Mini-Projekte (je Ordner ein Rezept)
└─ snippets/            # Codebeispiele, z. B. Kopien aus runnel/internal/actions
tools/build.py          # erzeugt die Unterseiten (Python 3.9+, keine Abhängigkeiten)
tools/fetch-reference.py  # holt catalog.json und expressions.json aus einem Runnel-Release
tools/kochbuch.py       # erzeugt die Rezeptseiten des Kochbuchs
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

## Referenz der Bausteine und Ausdrücke

Der Abschnitt „Bausteine“ der Startseite und die Referenzen im Handbuch entstehen aus `_src/catalog.json` und
`_src/expressions.json`. Beide stammen aus einem Runnel-Release: Jedes Release (seit E15a) hängt
`runnel-catalog.json` (`runnel catalog --json`: Actions, Transforms, Connection-Typen) und `runnel-expressions.json`
(`runnel catalog --expressions --json`) an. Nach einem neuen Release:

```bash
python3 tools/fetch-reference.py          # neuestes Release, auch Vorabversionen; oder z. B. v0.1.0
python3 tools/build.py
```

Das Skript lädt beide Dateien und `SHA256SUMS`, prüft die Prüfsummen und dass `version` in beiden Dateien zum Release
passt, und schreibt erst dann. Bei einem Fehler bleiben die vorhandenen Dateien unverändert. Die Website zeigt damit
immer den Stand eines Releases, nicht den von `main`.

Hat ein Release die Dateien noch nicht (alle Releases vor E15a), nimmt `--local` sie aus einem Runnel-Programm,
z. B. aus `main` gebaut. Den Commit dann im PR vermerken:

```bash
python3 tools/fetch-reference.py --local ../runnel/bin/runnel
```

Fehlt in den Dateien etwas, das die Website braucht, gehört das als Issue oder PR ins Runnel-Repository – nicht als
Ergänzung von Hand in die JSON-Dateien.

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

## Kochbuch

Die Rezepte unter `handbuch/kochbuch-*.html` zeigen Dateien aus `_src/kochbuch/<rezept>/`. Jeder Ordner ist ein
vollständiges kleines Projekt. Vor dem Commit prüfen (Secrets mit Platzhalterwerten):

```bash
for r in _src/kochbuch/*; do GITHUB_TOKEN=x HUBSPOT_TOKEN=x LEXWARE_API_KEY=x TEAMS_SIG=x GRAPH_CLIENT_SECRET=x runnel validate "$r"; done
```

Die Rezeptseiten erzeugt `tools/kochbuch.py` aus einer Liste (Titel, Texte DE/EN, Dateien, Voraussetzungen). Ein neues
Rezept: Ordner unter `_src/kochbuch/` anlegen, Eintrag in `tools/kochbuch.py` ergänzen, in `GUIDE_NAV` (Gruppe
„Kochbuch“) und in die Tabelle auf `_src/guide-kochbuch.html` eintragen, dann `python3 tools/kochbuch.py` und
`python3 tools/build.py`. Jede Seite nennt unter „Stand“, womit das Rezept geprüft ist.

## Entwicklerdoku

Die Seiten unter `docs/` fassen die Anleitungen aus dem Runnel-Repository zusammen (`AGENTS.md`, `CONTRIBUTING.md`,
`docs/dev/ACTIONS.md`, `TRANSFORMS.md`, `EDITOR.md`, `API.md`); maßgeblich bleibt das Repository. Ändert sich dort eine Anleitung, die betroffene
Datei in `_src/` und ggf. die Codebeispiele in `_src/snippets/` nachziehen und `tools/build.py` ausführen.

## Offen (Mockup)

- Impressum und Datenschutz enthalten Platzhalter (gelb gestrichelt markiert, Klasse `ph`). Vor dem Livegang ausfüllen,
  den Hinweiskasten `legal-notice` entfernen und die Texte rechtlich prüfen lassen.
- Rechtstexte stehen je Sprache in einem eigenen Block (`data-lang-block="de|en"`); die deutsche Fassung ist maßgeblich.
- Kennzahlen und Vergleich sind Zielwerte aus dem Konzept; die Terminal-Ausgabe zeigt das geplante `runnel run`.
