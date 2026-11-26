#!/usr/bin/env python3
"""Holt die Referenz der Bausteine und Ausdrücke einer Runnel-Version für die Website.

Jedes Runnel-Release (ab E15a) hängt zwei Dateien an, die die Website übernimmt:

  runnel-catalog.json      runnel catalog --json                (Actions, Transforms, Connection-Typen)
  runnel-expressions.json  runnel catalog --expressions --json  (Namen und Funktionen der Ausdrücke)

Das Skript lädt beide Dateien und SHA256SUMS aus dem Release, prüft die Prüfsummen und dass
"version" in beiden Dateien zum Release passt, und schreibt sie erst dann nach
_src/catalog.json und _src/expressions.json. Schlägt eine Prüfung fehl, bleibt alles, wie es war.

Aufruf (ohne Abhängigkeiten, Python 3.9+):

  python3 tools/fetch-reference.py                     # neuestes Release (auch Vorabversionen)
  python3 tools/fetch-reference.py v0.1.0              # bestimmtes Release
  python3 tools/fetch-reference.py --local bin/runnel  # ohne Release: aus einem Runnel-Programm,
                                                        # z. B. aus main gebaut (im PR vermerken)
  python3 tools/build.py                               # danach die Seiten erzeugen

--base-url ersetzt https://github.com/<repo>/releases/download (Spiegel, Tests).
"""
import argparse
import hashlib
import json
import os
import re
import subprocess
import sys
import tempfile
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "_src"
REPO = "runnelhq/runnel"
# Name im Release → Datei der Website
FILES = {"runnel-catalog.json": SRC / "catalog.json", "runnel-expressions.json": SRC / "expressions.json"}
MAX_SIZE = 20 * 1024 * 1024
TIMEOUT = 60


class Fail(Exception):
    pass


def get(url):
    req = urllib.request.Request(url, headers={"User-Agent": "runnel-website-fetch-reference", "Accept": "*/*"})
    try:
        with urllib.request.urlopen(req, timeout=TIMEOUT) as r:
            data = r.read(MAX_SIZE + 1)
    except urllib.error.HTTPError as e:
        raise Fail(f"{url}: HTTP {e.code}") from None
    except urllib.error.URLError as e:
        raise Fail(f"{url}: {e.reason}") from None
    if len(data) > MAX_SIZE:
        raise Fail(f"{url}: larger than {MAX_SIZE // (1024 * 1024)} MiB")
    return data


def latest_tag(repo):
    """Neuestes Release, das kein Entwurf ist – auch eine Vorabversion (/releases/latest kennt die nicht)."""
    data = json.loads(get(f"https://api.github.com/repos/{repo}/releases?per_page=20"))
    for r in data:
        if not r.get("draft"):
            return r["tag_name"]
    raise Fail(f"{repo} has no release")


def parse_sums(text):
    sums = {}
    for line in text.splitlines():
        m = re.fullmatch(r"([0-9a-f]{64})\s+\*?(\S+)", line.strip())
        if m:
            sums[m.group(2)] = m.group(1)
    return sums


def check(name, data, version):
    """Gültiges JSON mit passender Version und den erwarteten Teilen."""
    try:
        doc = json.loads(data)
    except ValueError as e:
        raise Fail(f"{name}: not valid JSON ({e})") from None
    if not isinstance(doc, dict):
        raise Fail(f"{name}: not a JSON object")
    got = doc.get("version")
    if version is not None and got != version:
        raise Fail(f"{name}: version is {got!r}, expected {version!r}")
    need = ("actions", "transforms", "connectionTypes") if name == "runnel-catalog.json" else ("roots", "functions")
    missing = [k for k in need if not isinstance(doc.get(k), list)]
    if missing:
        raise Fail(f"{name}: missing {', '.join(missing)}")
    return doc


def from_release(tag, base):
    print(f"Release {tag}")
    sums = parse_sums(get(f"{base}/{tag}/SHA256SUMS").decode("utf-8", "replace"))
    absent = [n for n in FILES if n not in sums]
    if absent:
        raise Fail(f"release {tag} has no {' and '.join(absent)} in SHA256SUMS (release files exist since E15a); "
                   "use --local with a runnel built from main")
    out = {}
    for name in FILES:
        data = get(f"{base}/{tag}/{name}")
        digest = hashlib.sha256(data).hexdigest()
        if digest != sums[name]:
            raise Fail(f"{name}: SHA-256 {digest} does not match SHA256SUMS ({sums[name]})")
        check(name, data, tag)
        out[name] = data
        print(f"  {name}: {len(data)} bytes, SHA-256 ok")
    return out


def from_local(runnel):
    out = {}
    for name, args in (("runnel-catalog.json", ["catalog", "--json"]), ("runnel-expressions.json", ["catalog", "--expressions", "--json"])):
        try:
            data = subprocess.run([runnel, *args], check=True, capture_output=True, timeout=TIMEOUT).stdout
        except (OSError, subprocess.SubprocessError) as e:
            raise Fail(f"{runnel} {' '.join(args)}: {e}") from None
        out[name] = data
    versions = {check(n, d, None).get("version") for n, d in out.items()}
    if len(versions) != 1:
        raise Fail(f"versions differ: {sorted(map(str, versions))}")
    print(f"Local {runnel}: version {versions.pop()}")
    return out


def write(files):
    """Erst alles prüfen, dann schreiben – über eine temporäre Datei je Ziel."""
    for name, data in files.items():
        target = FILES[name]
        doc = json.loads(data)
        text = json.dumps(doc, indent=1, ensure_ascii=False) + "\n"
        fd, tmp = tempfile.mkstemp(dir=target.parent, prefix=target.name, suffix=".tmp")
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            f.write(text)
        os.replace(tmp, target)
        print(f"  wrote {target.relative_to(ROOT)}")


def main():
    p = argparse.ArgumentParser(description="Fetch runnel-catalog.json and runnel-expressions.json of a Runnel release.")
    p.add_argument("tag", nargs="?", help="release tag, e.g. v0.1.0; default: the newest release")
    p.add_argument("--local", metavar="RUNNEL", help="take the files from this runnel program instead of a release")
    p.add_argument("--repo", default=REPO, help=f"GitHub repository (default {REPO})")
    p.add_argument("--base-url", help="instead of https://github.com/<repo>/releases/download")
    a = p.parse_args()
    try:
        if a.local:
            if a.tag:
                raise Fail("give either a tag or --local")
            files = from_local(a.local)
        else:
            base = (a.base_url or f"https://github.com/{a.repo}/releases/download").rstrip("/")
            files = from_release(a.tag or latest_tag(a.repo), base)
        write(files)
    except Fail as e:
        print(f"fetch-reference: {e}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
