#!/usr/bin/env python3
from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SKIP_DIRS = {".git", "node_modules", ".venv", "venv", "dist", "static", "__pycache__", "web-next-backup"}
SKIP_SUFFIX = {".png", ".jpg", ".jpeg", ".gif", ".webp", ".ico", ".woff", ".woff2", ".pdf", ".db"}

# Order matters: longer / more specific first.
REPLACEMENTS = [
    ("getcasty.duckdns.org", "ogma.duckdns.org"),
    ("getcast.duckdns.org", "ogma.duckdns.org"),
    ("casty.duckdns.org", "ogma.duckdns.org"),
    ("https://github.com/lisss/casty", "https://github.com/lisss/ogma"),
    ("https://github.com/lisss/cast", "https://github.com/lisss/ogma"),
    ("ghcr.io/lisss/casty", "ghcr.io/lisss/ogma"),
    ("ghcr.io/lisss/cast", "ghcr.io/lisss/ogma"),
    ("lisss/casty", "lisss/ogma"),
    ("lisss/cast", "lisss/ogma"),
    ("/opt/casty", "/opt/ogma"),
    ("/opt/cast", "/opt/ogma"),
    ("DUCKDNS_SUBDOMAIN=getcasty", "DUCKDNS_SUBDOMAIN=ogma"),
    ("DUCKDNS_SUBDOMAIN=getcast", "DUCKDNS_SUBDOMAIN=ogma"),
    ("DUCKDNS_SUBDOMAIN=casty", "DUCKDNS_SUBDOMAIN=ogma"),
    ("CastyMark", "OgmaMark"),
    ("CastMark", "OgmaMark"),
    ("Casty mark (gap bridge)", "Ogma mark (gap bridge)"),
    ("casty-todo-changed", "ogma-todo-changed"),
    ("cast-todo-changed", "ogma-todo-changed"),
    ("casty_sid", "ogma_sid"),
    ("cast_sid", "ogma_sid"),
    ("casty.sections", "ogma.sections"),
    ("cast.sections", "ogma.sections"),
    ("casty.todo", "ogma.todo"),
    ("cast.todo", "ogma.todo"),
    ("casty.ui", "ogma.ui"),
    ("cast.ui", "ogma.ui"),
    ("casty.cv", "ogma.cv"),
    ("cast.cv", "ogma.cv"),
    ("casty-cv", "ogma-cv"),
    ("cast-cv", "ogma-cv"),
    ("container_name: casty-", "container_name: ogma-"),
    ("container_name: cast-", "container_name: ogma-"),
    ("sqlite:////data/casty.db", "sqlite:////data/ogma.db"),
    ("sqlite:////data/cast.db", "sqlite:////data/ogma.db"),
    ("sqlite:////tmp/casty.db", "sqlite:////tmp/ogma.db"),
    ("sqlite:////tmp/cast.db", "sqlite:////tmp/ogma.db"),
    ("sqlite:///./casty.db", "sqlite:///./ogma.db"),
    ("sqlite:///./cast.db", "sqlite:///./ogma.db"),
    ("**/casty.db", "**/ogma.db"),
    ("title=\"Casty API\"", "title=\"Ogma API\""),
    ("title=\"Cast API\"", "title=\"Ogma API\""),
    ("# Casty", "# Ogma"),
    ("# Cast", "# Ogma"),
    ("Deploy Casty", "Deploy Ogma"),
    ("Deploy Cast", "Deploy Ogma"),
    ("Casty is starting", "Ogma is starting"),
    ("Cast is starting", "Ogma is starting"),
    ("Casty is a free", "Ogma is a free"),
    ("Cast is a free", "Ogma is a free"),
    ("Casty shows", "Ogma shows"),
    ("Cast shows", "Ogma shows"),
    ("Casty helps", "Ogma helps"),
    ("Cast helps", "Ogma helps"),
    ("Casty maps", "Ogma maps"),
    ("Cast maps", "Ogma maps"),
    ("on Casty", "on Ogma"),
    ("on Cast", "on Ogma"),
    ("| Casty", "| Ogma"),
    ("| Cast", "| Ogma"),
    ("title = 'Casty'", "title = 'Ogma'"),
    ("title = 'Cast'", "title = 'Ogma'"),
    ("'Casty —", "'Ogma —"),
    ("'Cast —", "'Ogma —"),
    ('"Casty —', '"Ogma —'),
    ('"Cast —', '"Ogma —'),
    ('content="Casty"', 'content="Ogma"'),
    ('content="Cast"', 'content="Ogma"'),
    ('aria-label="Casty"', 'aria-label="Ogma"'),
    ('aria-label="Cast"', 'aria-label="Ogma"'),
    (">Casty</", ">Ogma</"),
    (">Cast</", ">Ogma</"),
    ('site_name" content="Casty"', 'site_name" content="Ogma"'),
    ('site_name" content="Cast"', 'site_name" content="Ogma"'),
    ('"name": "Casty"', '"name": "Ogma"'),
    ('"name": "Cast"', '"name": "Ogma"'),
    ("Learning list | Casty", "Learning list | Ogma"),
    ("Learning list | Cast", "Learning list | Ogma"),
    ("saved Casty study", "saved Ogma study"),
    ("saved Cast study", "saved Ogma study"),
    ("free on Casty", "free on Ogma"),
    ("free on Cast", "free on Ogma"),
    ("name: casty", "name: ogma"),
    ("--name casty", "--name ogma"),
    ("-t casty:latest", "-t ogma:latest"),
    (" casty:latest", " ogma:latest"),
]


def main() -> None:
    changed: list[str] = []
    for path in ROOT.rglob("*"):
        if not path.is_file():
            continue
        if any(p in SKIP_DIRS for p in path.parts):
            continue
        if path.name.startswith("rename-to-"):
            continue
        if path.suffix.lower() in SKIP_SUFFIX:
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except Exception:
            continue
        orig = text
        for old, new in REPLACEMENTS:
            text = text.replace(old, new)
        text = re.sub(r"\bCasty\b", "Ogma", text)
        text = re.sub(r"\bcasty\b", "ogma", text)
        # Word-boundary only, so an earlier replacement is not expanded again.
        text = re.sub(r"(?<![A-Za-z])Cast(?![A-Za-z])", "Ogma", text)
        text = re.sub(r"(?<![A-Za-z])cast(?![A-Za-z])", "ogma", text)
        if text != orig:
            path.write_text(text, encoding="utf-8")
            changed.append(str(path.relative_to(ROOT)))
    print(f"updated {len(changed)} files")
    for p in changed:
        print(p)


if __name__ == "__main__":
    main()
