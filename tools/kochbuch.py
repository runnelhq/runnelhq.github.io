#!/usr/bin/env python3
"""Erzeugt die Rezeptseiten des Kochbuchs (_src/guide-kochbuch-<rezept>.html) aus der Liste R.

Ein neues Rezept: Ordner _src/kochbuch/<rezept>/ anlegen, Eintrag in R ergänzen, dann
  python3 tools/kochbuch.py && python3 tools/build.py
"""
import json, html
import pathlib
OUT=str(pathlib.Path(__file__).resolve().parent.parent / '_src') + '/'
CHECK_DE='Runnel-seitig geprüft am 23.11.2026: <code>runnel validate</code> und Ausführung gegen einen Testserver, der die API nachbildet. Gegen die echte API noch nicht ausgeführt – Endpunkte und Felder nach der Dokumentation des Anbieters (Stand 11/2026).'
CHECK_EN='Checked on the Runnel side on 2026-11-23: <code>runnel validate</code> and runs against a test server that mimics the API. Not yet run against the real API – endpoints and fields per the provider\'s documentation (as of 11/2026).'
R=[
 dict(key='open-meteo', title=('Wetter (Open-Meteo)','Weather (Open-Meteo)'),
  lead=('Liest die aktuelle Temperatur und Windgeschwindigkeit für einen Ort. Ohne Anmeldung – das einfachste Rezept zum Ausprobieren.','Reads the current temperature and wind speed for a place. No sign-in – the simplest recipe to try things out.'),
  api=('<a href="https://open-meteo.com/en/docs">Open-Meteo Forecast API</a>, für nicht-kommerzielle Nutzung frei','<a href="https://open-meteo.com/en/docs">Open-Meteo Forecast API</a>, free for non-commercial use'),
  auth=('keine','none'),
  prereq=[],
  files=['project.yaml','connections/open-meteo.yaml','workflows/weather.workflow.yaml'],
  run=['runnel run workflows/weather.workflow.yaml','runnel run --param LAT=48.14 --param LON=11.58 --param PLACE=München workflows/weather.workflow.yaml'],
  adapt=[('<code>LAT</code>, <code>LON</code>, <code>PLACE</code> als Parameter oder Standardwerte setzen.','Set <code>LAT</code>, <code>LON</code>, <code>PLACE</code> as parameters or defaults.'),
         ('Weitere Werte unter <code>current</code> abfragen, z. B. <code>relative_humidity_2m</code>; sie stehen dann unter <code>body.current</code>.','Request more values under <code>current</code>, e.g. <code>relative_humidity_2m</code>; they appear under <code>body.current</code>.'),
         ('Für kommerzielle Nutzung die Bedingungen von Open-Meteo beachten.','For commercial use, observe Open-Meteo\'s terms.')],
  note=None),
 dict(key='teams', title=('Microsoft Teams','Microsoft Teams'),
  lead=('Schickt eine Nachricht als Karte in einen Teams-Kanal – über einen Workflow-Webhook. Der Workflow <code>notify</code> dient als Connector: Andere Workflows rufen ihn auf, z. B. auf einem Fehler-Link.','Posts a message as a card to a Teams channel – through a workflow webhook. The <code>notify</code> workflow acts as a connector: other workflows call it, e.g. on a failure link.'),
  api=('Microsoft Teams, Workflows-App: Vorlage „Post to a channel when a webhook request is received“','Microsoft Teams, Workflows app: template “Post to a channel when a webhook request is received”'),
  auth=('Signatur <code>sig</code> in der Adresse, als <code>apiKey</code> in der Query','Signature <code>sig</code> in the address, as <code>apiKey</code> in the query'),
  prereq=[('TEAMS_URL','Variable','Adresse des Webhooks aus Teams <strong>ohne</strong> den Teil <code>&amp;sig=…</code>','Webhook address from Teams <strong>without</strong> the part <code>&amp;sig=…</code>'),
          ('TEAMS_SIG','Secret','Wert von <code>sig</code> aus der Adresse – als Umgebungsvariable','Value of <code>sig</code> from the address – as an environment variable')],
  files=['project.yaml','connections/teams.yaml','workflows/notify.workflow.yaml','workflows/notify-on-failure.workflow.yaml'],
  run=['$env:TEAMS_SIG = "…"','runnel run --param TITLE="Import done" --param TEXT="1.234 rows" workflows/notify.workflow.yaml'],
  adapt=[('In Teams am Kanal „Workflows“ wählen, die Vorlage für Webhooks anlegen und die angezeigte Adresse kopieren. Alles bis vor <code>&amp;sig=</code> wird <code>TEAMS_URL</code>, der Wert danach <code>TEAMS_SIG</code>.','In Teams, choose “Workflows” on the channel, create the webhook template and copy the address shown. Everything up to <code>&amp;sig=</code> becomes <code>TEAMS_URL</code>, the value after it <code>TEAMS_SIG</code>.'),
         ('Die Karte ist eine <a href="https://adaptivecards.io/designer/">Adaptive Card</a>; weitere Elemente unter <code>content.body</code> ergänzen. Eine Nachricht darf höchstens 28 KB groß sein.','The card is an <a href="https://adaptivecards.io/designer/">Adaptive Card</a>; add elements under <code>content.body</code>. A message may be at most 28 KB.'),
         ('Die Signatur ist ein Zugangsdatum: Wer die vollständige Adresse kennt, kann in den Kanal schreiben. Deshalb steht sie als Secret in der Connection und nicht im Workflow.','The signature is a credential: anyone with the full address can post to the channel. That is why it is a secret in the connection, not in the workflow.')],
  note=('Die Action nennt die vollständige Adresse (<code>url: ${TEAMS_URL}</code>), weil die Query der Webhook-Adresse erhalten bleiben muss; die Connection hängt die Signatur an. Ein Aufruf aus einem anderen Workflow steht in <code>notify-on-failure.workflow.yaml</code>.','The action names the full address (<code>url: ${TEAMS_URL}</code>) because the query of the webhook address must be kept; the connection adds the signature. A call from another workflow is in <code>notify-on-failure.workflow.yaml</code>.')),
 dict(key='github', title=('GitHub','GitHub'),
  lead=('Liest alle offenen Issues eines Repositorys Seite für Seite und legt bei Bedarf ein neues Issue an – etwa wenn ein nächtlicher Import scheitert.','Reads all open issues of a repository page by page and creates a new issue when needed – e.g. when a nightly import fails.'),
  api=('<a href="https://docs.github.com/en/rest">GitHub REST API</a>, Version <code>2022-11-28</code>','<a href="https://docs.github.com/en/rest">GitHub REST API</a>, version <code>2022-11-28</code>'),
  auth=('Personal Access Token als <code>bearer</code>','Personal access token as <code>bearer</code>'),
  prereq=[('GITHUB_TOKEN','Secret','Fine-grained Personal Access Token mit Lesezugriff auf Issues (zum Anlegen: Schreibzugriff)','Fine-grained personal access token with read access to issues (to create: write access)')],
  files=['project.yaml','connections/github.yaml','workflows/open-issues.workflow.yaml','workflows/create-issue.workflow.yaml'],
  run=['$env:GITHUB_TOKEN = "github_pat_…"','runnel run --param REPO=owner/name workflows/open-issues.workflow.yaml','runnel run --param REPO=owner/name --param TITLE="Import failed" workflows/create-issue.workflow.yaml'],
  adapt=[('Andere Endpunkte wie <code>repos/${REPO}/pulls</code> oder <code>repos/${REPO}/releases</code> nutzen dieselbe Connection und dieselbe Paginierung.','Other endpoints such as <code>repos/${REPO}/pulls</code> or <code>repos/${REPO}/releases</code> use the same connection and pagination.'),
         ('Für GitHub Enterprise Server <code>GITHUB_URL</code> auf <code>https://&lt;host&gt;/api/v3/</code> setzen.','For GitHub Enterprise Server, set <code>GITHUB_URL</code> to <code>https://&lt;host&gt;/api/v3/</code>.'),
         ('<code>maxItems</code> (Standard 10.000) begrenzt die gelesenen Issues; mehr ist ein Fehler.','<code>maxItems</code> (default 10,000) limits the issues read; more is an error.')],
  note=('GitHub nennt die nächste Seite im Header <code>Link</code>, daher <code>style: link</code>. Ohne Token funktionieren öffentliche Repositories mit deutlich weniger Anfragen pro Stunde – dafür <code>auth</code> und <code>token</code> in der Connection weglassen.','GitHub names the next page in the <code>Link</code> header, hence <code>style: link</code>. Public repositories work without a token at far fewer requests per hour – then omit <code>auth</code> and <code>token</code> in the connection.')),
 dict(key='hubspot', title=('HubSpot','HubSpot'),
  lead=('Liest alle Kontakte aus dem HubSpot-CRM und legt neue Kontakte an. <code>create-contact</code> ist ein Connector mit Parametern und der ID als Output.','Reads all contacts from the HubSpot CRM and creates new contacts. <code>create-contact</code> is a connector with parameters and the ID as output.'),
  api=('<a href="https://developers.hubspot.com/docs/api/crm/contacts">HubSpot CRM API v3, Contacts</a>','<a href="https://developers.hubspot.com/docs/api/crm/contacts">HubSpot CRM API v3, Contacts</a>'),
  auth=('Access Token einer Private App als <code>bearer</code>','Private app access token as <code>bearer</code>'),
  prereq=[('HUBSPOT_TOKEN','Secret','Access Token einer Private App mit den Bereichen <code>crm.objects.contacts.read</code> und <code>.write</code>','Access token of a private app with the scopes <code>crm.objects.contacts.read</code> and <code>.write</code>')],
  files=['project.yaml','connections/hubspot.yaml','workflows/contacts.workflow.yaml','workflows/create-contact.workflow.yaml'],
  run=['$env:HUBSPOT_TOKEN = "pat-…"','runnel run workflows/contacts.workflow.yaml','runnel run --param EMAIL=ada@example.com --param FIRSTNAME=Ada workflows/create-contact.workflow.yaml'],
  adapt=[('Weitere Eigenschaften über <code>query.properties</code> lesen bzw. unter <code>body.properties</code> schreiben.','Read more properties via <code>query.properties</code> or write them under <code>body.properties</code>.'),
         ('Firmen und Deals funktionieren gleich: <code>crm/v3/objects/companies</code>, <code>crm/v3/objects/deals</code>.','Companies and deals work the same: <code>crm/v3/objects/companies</code>, <code>crm/v3/objects/deals</code>.'),
         ('Gibt es eine E-Mail schon, antwortet HubSpot mit <code>409</code>. Mit <code>failOnError: false</code> und einem Link mit Bedingung auf <code>result.output.status</code> lässt sich das abfangen.','If an e-mail already exists, HubSpot answers <code>409</code>. With <code>failOnError: false</code> and a link conditioned on <code>result.output.status</code> this can be handled.')],
  note=('HubSpot liefert den Cursor der nächsten Seite in <code>paging.next.after</code> und erwartet ihn als Query-Parameter <code>after</code>, daher <code>style: cursor</code>. Auf der letzten Seite fehlt <code>paging.next</code>.','HubSpot returns the next page\'s cursor in <code>paging.next.after</code> and expects it as the query parameter <code>after</code>, hence <code>style: cursor</code>. On the last page <code>paging.next</code> is missing.')),
 dict(key='lexware', title=('Lexware Office','Lexware Office'),
  lead=('Liest alle Kontakte aus Lexware Office (vormals lexoffice). Das Rezept zeigt Paginierung mit Seitennummern und den Umgang mit dem Rate-Limit der API.','Reads all contacts from Lexware Office (formerly lexoffice). The recipe shows page-number pagination and handling the API\'s rate limit.'),
  api=('Lexware Office Public API, <code>https://api.lexware.io/v1/</code> (der frühere Host <code>api.lexoffice.io</code> wird abgelöst)','Lexware Office public API, <code>https://api.lexware.io/v1/</code> (the former host <code>api.lexoffice.io</code> is being retired)'),
  auth=('API-Schlüssel als <code>bearer</code>','API key as <code>bearer</code>'),
  prereq=[('LEXWARE_API_KEY','Secret','API-Schlüssel aus den Einstellungen von Lexware Office („Öffentliche API“)','API key from the Lexware Office settings (“Public API”)')],
  files=['project.yaml','connections/lexware.yaml','workflows/contacts.workflow.yaml'],
  run=['$env:LEXWARE_API_KEY = "…"','runnel run workflows/contacts.workflow.yaml'],
  adapt=[('Die Kontakte stehen je Seite in <code>content</code>; Seiten zählen ab <code>0</code>, bis zu 250 Einträge je Seite.','Contacts are in <code>content</code> per page; pages count from <code>0</code>, up to 250 entries per page.'),
         ('Die API erlaubt etwa 2 Anfragen pro Sekunde und antwortet darüber mit <code>429</code>. Sendet sie <code>Retry-After</code>, wartet Runnel; sonst wiederholt <code>retry</code> die Anfrage mit wachsendem Abstand.','The API allows about 2 requests per second and answers <code>429</code> above that. If it sends <code>Retry-After</code>, Runnel waits; otherwise <code>retry</code> repeats the request with growing delays.'),
         ('Weitere Listen mit demselben Muster, z. B. Belege über <code>voucherlist</code>.','Other lists follow the same pattern, e.g. vouchers via <code>voucherlist</code>.')],
  note=('Die offizielle Dokumentation (developers.lexware.io) war beim Erstellen nicht erreichbar; Host, Paging und Rate-Limit stammen aus mehreren übereinstimmenden Quellen. Vor dem Einsatz bitte dort prüfen.','The official documentation (developers.lexware.io) could not be reached when this recipe was written; host, paging and rate limit come from several matching sources. Please check there before use.')),
]

OFF_DE='Geprüft am 24.11.2026 mit <code>runnel validate</code> und vollständig ausgeführt mit den Beispieldaten des Rezepts.'
OFF_EN='Checked on 2026-11-24 with <code>runnel validate</code> and run completely with the recipe\'s sample data.'
R += [
 dict(key='sharepoint', title=('SharePoint (Microsoft Graph)','SharePoint (Microsoft Graph)'),
  lead=('Lädt ZIP-Dateien aus einer SharePoint-Dokumentbibliothek herunter, entpackt sie und liest die enthaltenen CSV-Dateien in eine Datei. Das Rezept zeigt die Anmeldung mit OAuth2 (Client Credentials) und den Download mit <code>saveTo</code>.','Downloads ZIP files from a SharePoint document library, unpacks them and reads the CSV files inside into one file. The recipe shows OAuth2 sign-in (client credentials) and downloading with <code>saveTo</code>.'),
  api=('<a href="https://learn.microsoft.com/en-us/graph/api/driveitem-get-content">Microsoft Graph, Inhalt einer Datei herunterladen</a>','<a href="https://learn.microsoft.com/en-us/graph/api/driveitem-get-content">Microsoft Graph, download a file\'s content</a>'),
  auth=('OAuth2 Client Credentials einer in Microsoft Entra registrierten Anwendung','OAuth2 client credentials of an application registered in Microsoft Entra'),
  prereq=[('GRAPH_TENANT','Variable','Tenant, z. B. <code>contoso.onmicrosoft.com</code>','Tenant, e.g. <code>contoso.onmicrosoft.com</code>'),
          ('GRAPH_CLIENT_ID','Variable','Anwendungs-ID (Client-ID) der registrierten Anwendung','Application (client) ID of the registered application'),
          ('SHAREPOINT_SITE','Variable','Site als <code>host:/pfad:</code>, z. B. <code>contoso.sharepoint.com:/sites/Finance:</code>','Site as <code>host:/path:</code>, e.g. <code>contoso.sharepoint.com:/sites/Finance:</code>'),
          ('GRAPH_CLIENT_SECRET','Secret','Geheimer Clientschlüssel der Anwendung','Client secret of the application')],
  files=['project.yaml','connections/sharepoint.yaml','workflows/orders.workflow.yaml','workflows/file.workflow.yaml','pipelines/orders.pipeline.yaml'],
  run=['$env:GRAPH_CLIENT_SECRET = "…"','runnel run -v workflows/orders.workflow.yaml',"runnel run -v --param 'PATHS=[\"Exports/2026/orders-north.zip\"]' workflows/orders.workflow.yaml"],
  adapt=[('In Microsoft Entra eine Anwendung registrieren und ihr die Anwendungsberechtigung <code>Sites.Selected</code> geben (Zugriff je Site freigeben, empfohlen) oder <code>Files.Read.All</code>; einen geheimen Clientschlüssel anlegen.','Register an application in Microsoft Entra and give it the application permission <code>Sites.Selected</code> (access granted per site, recommended) or <code>Files.Read.All</code>; create a client secret.'),
         ('Die Pfade der Dateien stehen im Parameter <code>PATHS</code> (JSON-Liste), relativ zur Dokumentbibliothek der Site.','The file paths are in the parameter <code>PATHS</code> (JSON list), relative to the site\'s document library.'),
         ('Für andere Dateiarten den Schritt <code>unpack</code> weglassen und die Pipeline direkt mit <code>results.download.output.path</code> aufrufen.','For other file types, drop the <code>unpack</code> step and call the pipeline directly with <code>results.download.output.path</code>.'),
         ('Andere Graph-Endpunkte (Mail, Teams, Benutzer) nutzen dieselbe Connection; Listen mit <code>paginate: { style: url, next: "@odata.nextLink", items: value }</code>.','Other Graph endpoints (mail, Teams, users) use the same connection; lists with <code>paginate: { style: url, next: "@odata.nextLink", items: value }</code>.')],
  note=('Runnel holt das Token selbst und hält es bis kurz vor Ablauf im Speicher. Graph beantwortet <code>…:/content</code> mit einer Weiterleitung zum Download; zu einem anderen Host geht das Token dabei nicht mit. <code>saveTo</code> schreibt die Antwort direkt in eine Datei, ihr Pfad steht in <code>output.path</code>. Die Dateien werden nacheinander verarbeitet (<code>forEach</code> ohne <code>parallel</code>), weil alle an dieselbe CSV-Datei anhängen.','Runnel fetches the token itself and keeps it in memory until shortly before it expires. Graph answers <code>…:/content</code> with a redirect to the download; the token does not go along to another host. <code>saveTo</code> writes the response straight into a file, its path is in <code>output.path</code>. Files are processed one after the other (<code>forEach</code> without <code>parallel</code>) because all of them append to the same CSV file.'),
  check=('Runnel-seitig geprüft am 24.11.2026: <code>runnel validate</code> und Ausführung gegen einen Testserver mit Token-Abruf, Weiterleitung und ZIP-Download. Gegen Microsoft Graph noch nicht ausgeführt – nach der Dokumentation von Microsoft (Stand 11/2026).','Checked on the Runnel side on 2026-11-24: <code>runnel validate</code> and runs against a test server with token request, redirect and ZIP download. Not yet run against Microsoft Graph – per Microsoft\'s documentation (as of 11/2026).')),
 dict(key='excel', title=('Excel lesen und schreiben','Reading and writing Excel'),
  lead=('Liest Bestellungen aus einer Excel-Mappe, schreibt sie als CSV-Datei und als neue, formatierte Mappe. Fehlerhafte Zeilen gehen in eine eigene Datei.','Reads orders from an Excel workbook and writes them as a CSV file and as a new, formatted workbook. Faulty rows go into a separate file.'),
  apiLabel=('Bausteine','Components'),
  api=('<code>excel.input</code>, <code>excel.output</code>, <code>csv.output</code>','<code>excel.input</code>, <code>excel.output</code>, <code>csv.output</code>'),
  auth=('keine – nur Dateien','none – files only'),
  prereq=[],
  files=['project.yaml','pipelines/orders.pipeline.yaml','workflows/export.workflow.yaml'],
  run=['runnel run workflows/export.workflow.yaml'],
  adapt=[('<code>sheet</code> und <code>range</code> an die eigene Mappe anpassen: <code>range: A3</code> heißt, die Tabelle beginnt mit der Kopfzeile in A3; <code>emptyRows: stop</code> endet an der ersten leeren Zeile, etwa vor einer Summenzeile.','Adapt <code>sheet</code> and <code>range</code> to your workbook: <code>range: A3</code> means the table starts with its header in A3; <code>emptyRows: stop</code> ends at the first empty row, e.g. before a sum row.'),
         ('Zahlen, Daten und Wahrheitswerte kommen aus Excel bereits typisiert; <code>fields</code> wählt nur die Spalten und prüft die Typen. Spalten mit anderem Namen holt <code>from</code>.','Numbers, dates and booleans already come typed from Excel; <code>fields</code> only picks the columns and checks their types. Columns with another name are taken with <code>from</code>.'),
         ('Beim Schreiben bleibt eine Zahl eine Zahl: <code>format</code> nimmt ein Runnel-Muster wie <code>#.##0,00</code>, <code>excelFormat</code> einen eigenen Excel-Code wie <code>#,##0.00 "€"</code>. Mit <code>ifExists: sheet</code> ersetzt Runnel nur ein Blatt einer vorhandenen Mappe.','When writing, a number stays a number: <code>format</code> takes a Runnel pattern such as <code>#.##0,00</code>, <code>excelFormat</code> a custom Excel code such as <code>#,##0.00 "€"</code>. With <code>ifExists: sheet</code> Runnel replaces just one sheet of an existing workbook.')],
  note=('Die Beispielmappe <code>data/orders.xlsx</code> hat über der Tabelle einen Titel und darunter eine Summenzeile; Bestellung 1004 enthält <code>#N/A</code> im Betrag und landet über den Fehler-Link in <code>out/excel-rejected.csv</code>. Der Workflow legt den Ordner <code>out</code> an, weil die Ausgaben fehlende Ordner nicht erzeugen.','The sample workbook <code>data/orders.xlsx</code> has a title above the table and a sum row below it; order 1004 contains <code>#N/A</code> as amount and goes over the error link into <code>out/excel-rejected.csv</code>. The workflow creates the folder <code>out</code> because the outputs don\'t create missing folders.'),
  check=(OFF_DE,OFF_EN)),
 dict(key='xml', title=('XML-Austausch','XML exchange'),
  lead=('Liest Bestellungen aus einem XML-Export eines ERP-Systems, schreibt sie als CSV und als XML in der Struktur, die ein Partner erwartet.','Reads orders from an ERP system\'s XML export and writes them as CSV and as XML in the structure a partner expects.'),
  apiLabel=('Bausteine','Components'),
  api=('<code>xml.input</code>, <code>xml.output</code>, <code>csv.output</code>','<code>xml.input</code>, <code>xml.output</code>, <code>csv.output</code>'),
  auth=('keine – nur Dateien','none – files only'),
  prereq=[],
  files=['project.yaml','data/orders.xml','pipelines/orders.pipeline.yaml','workflows/export.workflow.yaml'],
  run=['runnel run workflows/export.workflow.yaml'],
  adapt=[('<code>records</code> ist der Pfad der Elemente, die Datensätze sind (<code>Bestellungen/Bestellung</code>); Präfixe von Namensräumen werden nicht geschrieben.','<code>records</code> is the path of the elements that are records (<code>Bestellungen/Bestellung</code>); namespace prefixes are not written.'),
         ('Beim Lesen holt <code>from</code> ein Attribut (<code>@nr</code>), ein verschachteltes Element (<code>Kunde/Name</code>) oder dessen Attribut (<code>Kunde/@id</code>).','When reading, <code>from</code> takes an attribute (<code>@nr</code>), a nested element (<code>Kunde/Name</code>) or its attribute (<code>Kunde/@id</code>).'),
         ('Beim Schreiben legt <code>as</code> fest, wohin ein Feld kommt: als Attribut (<code>@number</code>) oder verschachtelt (<code>customer/name</code>); <code>root</code> und <code>record</code> benennen Wurzel- und Datensatz-Element.','When writing, <code>as</code> decides where a field goes: as an attribute (<code>@number</code>) or nested (<code>customer/name</code>); <code>root</code> and <code>record</code> name the root and record elements.')],
  note=('Bestellung 1004 hat „k. A.“ als Betrag und geht über den Fehler-Link nach <code>out/xml-rejected.csv</code>, mit der Zeile der Bestellung in <code>_error</code>.','Order 1004 has “k. A.” as amount and goes over the error link to <code>out/xml-rejected.csv</code>, with the order\'s line in <code>_error</code>.'),
  check=(OFF_DE,OFF_EN)),
]
T={'de':dict(eyebrow='Handbuch · Kochbuch',purpose='Zweck',api='API',auth='Anmeldung',prereq='Voraussetzungen',name='Name',kind='Art',meaning='Bedeutung',none='Keine Konten oder Schlüssel nötig.',files='Dateien',run='Ausführen',adapt='Anpassen',status='Stand',src='Quellen auf GitHub',run_hint='Im Ordner des Rezepts (PowerShell):',sec_hint='Secrets kommen hier aus Umgebungsvariablen (<code>secretStore: env</code> in <code>project.yaml</code>). Für den Dienst die Variable beim Dienstkonto setzen.'),
   'en':dict(eyebrow='User guide · Cookbook',purpose='Purpose',api='API',auth='Sign-in',prereq='Prerequisites',name='Name',kind='Kind',meaning='Meaning',none='No accounts or keys needed.',files='Files',run='Running',adapt='Adapting',status='Status',src='Sources on GitHub',run_hint='In the recipe folder (PowerShell):',sec_hint='Secrets come from environment variables here (<code>secretStore: env</code> in <code>project.yaml</code>). For the service, set the variable for the service account.')}
def article(r,lang):
    t=T[lang]; i=0 if lang=='de' else 1; sfx='' if lang=='de' else '-en'
    o=[f'<article class="prose" data-lang-block="{lang}" lang="{lang}">',
       f'<p class="docs-eyebrow">{t["eyebrow"]}</p>',f'<h1>{r["title"][i]}</h1>',f'<p class="docs-lead">{r["lead"][i]}</p>',
       f'<dl class="recipe-meta"><dt>{r.get("apiLabel",(t["api"],t["api"]))[i]}</dt><dd>{r["api"][i]}</dd><dt>{t["auth"]}</dt><dd>{r["auth"][i]}</dd><dt>{t["status"]}</dt><dd>{r.get("check",(CHECK_DE,CHECK_EN))[i]}</dd></dl>',
       f'<h2 id="prereq{sfx}">{t["prereq"]}</h2>']
    if r['prereq']:
        rows=''.join(f'<tr><td><code>{n}</code></td><td>{k}</td><td>{(d if lang=="de" else e)}</td></tr>' for n,k,d,e in r['prereq'])
        o.append(f'<div class="table-scroll"><table class="doc-table"><thead><tr><th>{t["name"]}</th><th>{t["kind"]}</th><th>{t["meaning"]}</th></tr></thead><tbody>{rows}</tbody></table></div>')
        if any(k=='Secret' for _,k,_,_ in r['prereq']): o.append(f'<p>{t["sec_hint"]}</p>')
    else: o.append(f'<p>{t["none"]}</p>')
    o.append(f'<h2 id="files{sfx}">{t["files"]}</h2>')
    for f in r['files']:
        o.append('{{snippet:../kochbuch/'+r['key']+'/'+f+'|'+f+'}}')
    if r['note']: o.append(f'<p>{r["note"][i]}</p>')
    o.append(f'<h2 id="run{sfx}">{t["run"]}</h2><p>{t["run_hint"]}</p>')
    o.append('<pre><code class="lang-bash" data-caption="PowerShell">'+html.escape('\n'.join(r['run']))+'</code></pre>')
    o.append(f'<h2 id="adapt{sfx}">{t["adapt"]}</h2><ul>'+''.join(f'<li>{a[i]}</li>' for a in r['adapt'])+'</ul>')
    o.append(f'<p class="docs-source"><a href="https://github.com/runnelhq/runnelhq.github.io/tree/main/_src/kochbuch/{r["key"]}">{t["src"]}: <code>_src/kochbuch/{r["key"]}</code></a></p>')
    o.append('</article>')
    return '\n          '.join(o)
for r in R:
    meta={"out":f"handbuch/kochbuch-{r['key']}.html","section":"guide","title":{"de":f"Kochbuch: {r['title'][0]}","en":f"Cookbook: {r['title'][1]}"},
          "description":{"de":re.sub('<[^>]+>','',r['lead'][0]) if False else html.unescape(__import__('re').sub('<[^>]+>','',r['lead'][0])),"en":html.unescape(__import__('re').sub('<[^>]+>','',r['lead'][1]))},
          "nav":"handbuch/","main_class":"docs-page"}
    page=f'<!-- {json.dumps(meta,ensure_ascii=False,indent=2)} -->\n    <div class="wrap docs-layout">\n      {{{{sidebar}}}}\n\n      <div class="docs-content">\n          {article(r,"de")}\n\n          {article(r,"en")}\n      </div>\n    </div>\n'
    open(OUT+f'guide-kochbuch-{r["key"]}.html','w').write(page)
    print('wrote',r['key'])
