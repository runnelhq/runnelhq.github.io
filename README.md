# runnelhq.github.io

Website von [Runnel](https://github.com/runnelhq/runnel) – **Leicht. Lokal. Im Fluss.**

Statische Seite für GitHub Pages, ohne Build-Schritt. Zweisprachig (Deutsch/Englisch), responsiv, heller und dunkler Modus.

```
index.html              # Startseite, deutsche Texte direkt im HTML
impressum.html          # Impressum (DE/EN, Platzhalter)
datenschutz.html        # Datenschutzerklärung (DE/EN, Platzhalter)
favicon.svg, favicon.ico
assets/
├─ css/runnel.css       # Design Tokens – Kopie aus runnel/design/tokens/runnel.css (nicht hier ändern)
├─ css/site.css         # Seitenlayout auf Basis der Tokens
├─ js/i18n.js           # englische Texte (Schlüssel = data-i18n im HTML)
├─ js/site.js           # Sprachumschaltung, mobiles Menü, Kopieren-Buttons
├─ fonts/               # Inter, JetBrains Mono (WOFF2, Latin, SIL OFL 1.1) – lokal, keine Google-Fonts-Abfrage
└─ img/                 # Logos, Apple-Touch-Icon, Social Card aus runnel/design
```

## Lokal ansehen

```bash
python3 -m http.server 8000
```

Dann <http://localhost:8000> öffnen. Sprache per Umschalter oben rechts oder `?lang=de` / `?lang=en`
(sonst nach Browsersprache, Auswahl wird im Browser gemerkt).

## Texte ändern

- **Deutsch:** direkt in `index.html`.
- **Englisch:** in `assets/js/i18n.js` unter demselben Schlüssel wie das `data-i18n`-Attribut im HTML.
- Attribute (z. B. `aria-label`, `meta description`) über `data-i18n-attr="attribut:schlüssel"`.

## Corporate Design

Farben, Schriften, Logos und Ton stammen aus [`runnel/design`](https://github.com/runnelhq/runnel/tree/main/design).
Ändern sich dort die Tokens, `runnel.css` hierher kopieren.

## Offen (Mockup)

- Impressum und Datenschutz enthalten Platzhalter (gelb gestrichelt markiert, Klasse `ph`). Vor dem Livegang ausfüllen,
  den Hinweiskasten `legal-notice` entfernen und die Texte rechtlich prüfen lassen.
- Header und Footer der Unterseiten sind Kopien aus `index.html` – Änderungen dort mit übernehmen.
- Rechtstexte stehen je Sprache in einem eigenen Block (`data-lang-block="de|en"`); die deutsche Fassung ist maßgeblich.
- Kennzahlen und Vergleich sind Zielwerte aus dem Konzept; die Terminal-Ausgabe zeigt das geplante `runnel run`.
