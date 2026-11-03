#!/usr/bin/env python3
"""Rename Casty/Cast/getcast brand strings to Pathquire."""
from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SKIP_DIRS = {".git", "node_modules", ".venv", "venv", "dist", "static", "__pycache__", "web-next-backup"}
SKIP_SUFFIX = {".png", ".jpg", ".jpeg", ".gif", ".webp", ".ico", ".woff", ".woff2", ".pdf", ".db"}

# Order matters: longer / more specific first.
REPLACEMENTS = [
    ("getcasty.duckdns.org", "pathquire.duckdns.org"),
    ("getcast.duckdns.org", "pathquire.duckdns.org"),
    ("casty.duckdns.org", "pathquire.duckdns.org"),
    ("https://github.com/lisss/casty", "https://github.com/lisss/pathquire"),
    ("https://github.com/lisss/cast", "https://github.com/lisss/pathquire"),
    ("ghcr.io/lisss/casty", "ghcr.io/lisss/pathquire"),
    ("ghcr.io/lisss/cast", "ghcr.io/lisss/pathquire"),
    ("lisss/casty", "lisss/pathquire"),
    ("lisss/cast", "lisss/pathquire"),
    ("/opt/casty", "/opt/pathquire"),
    ("/opt/cast", "/opt/pathquire"),
    ("DUCKDNS_SUBDOMAIN=getcasty", "DUCKDNS_SUBDOMAIN=pathquire"),
    ("DUCKDNS_SUBDOMAIN=getcast", "DUCKDNS_SUBDOMAIN=pathquire"),
    ("DUCKDNS_SUBDOMAIN=casty", "DUCKDNS_SUBDOMAIN=pathquire"),
    ("CastyMark", "PathquireMark"),
    ("CastMark", "PathquireMark"),
    ("Casty mark (gap bridge)", "Pathquire mark (gap bridge)"),
    ("casty-todo-changed", "pathquire-todo-changed"),
    ("cast-todo-changed", "pathquire-todo-changed"),
    ("casty_sid", "pathquire_sid"),
    ("cast_sid", "pathquire_sid"),
    ("casty.sections", "pathquire.sections"),
    ("cast.sections", "pathquire.sections"),
    ("casty.todo", "pathquire.todo"),
    ("cast.todo", "pathquire.todo"),
    ("casty.ui", "pathquire.ui"),
    ("cast.ui", "pathquire.ui"),
    ("casty.cv", "pathquire.cv"),
    ("cast.cv", "pathquire.cv"),
    ("casty-cv", "pathquire-cv"),
    ("cast-cv", "pathquire-cv"),
    ("container_name: casty-", "container_name: pathquire-"),
    ("container_name: cast-", "container_name: pathquire-"),
    ("sqlite:////data/casty.db", "sqlite:////data/pathquire.db"),
    ("sqlite:////data/cast.db", "sqlite:////data/pathquire.db"),
    ("sqlite:////tmp/casty.db", "sqlite:////tmp/pathquire.db"),
    ("sqlite:////tmp/cast.db", "sqlite:////tmp/pathquire.db"),
    ("sqlite:///./casty.db", "sqlite:///./pathquire.db"),
    ("sqlite:///./cast.db", "sqlite:///./pathquire.db"),
    ("**/casty.db", "**/pathquire.db"),
    ("title=\"Casty API\"", "title=\"Pathquire API\""),
    ("title=\"Cast API\"", "title=\"Pathquire API\""),
    ("# Casty", "# Pathquire"),
    ("# Cast", "# Pathquire"),
    ("Deploy Casty", "Deploy Pathquire"),
    ("Deploy Cast", "Deploy Pathquire"),
    ("Casty is starting", "Pathquire is starting"),
    ("Cast is starting", "Pathquire is starting"),
    ("Casty is a free", "Pathquire is a free"),
    ("Cast is a free", "Pathquire is a free"),
    ("Casty shows", "Pathquire shows"),
    ("Cast shows", "Pathquire shows"),
    ("Casty helps", "Pathquire helps"),
    ("Cast helps", "Pathquire helps"),
    ("Casty maps", "Pathquire maps"),
    ("Cast maps", "Pathquire maps"),
    ("on Casty", "on Pathquire"),
    ("on Cast", "on Pathquire"),
    ("| Casty", "| Pathquire"),
    ("| Cast", "| Pathquire"),
    ("title = 'Casty'", "title = 'Pathquire'"),
    ("title = 'Cast'", "title = 'Pathquire'"),
    ("'Casty —", "'Pathquire —"),
    ("'Cast —", "'Pathquire —"),
    ('"Casty —', '"Pathquire —'),
    ('"Cast —', '"Pathquire —'),
    ('content="Casty"', 'content="Pathquire"'),
    ('content="Cast"', 'content="Pathquire"'),
    ('aria-label="Casty"', 'aria-label="Pathquire"'),
    ('aria-label="Cast"', 'aria-label="Pathquire"'),
    (">Casty</", ">Pathquire</"),
    (">Cast</", ">Pathquire</"),
    ('site_name" content="Casty"', 'site_name" content="Pathquire"'),
    ('site_name" content="Cast"', 'site_name" content="Pathquire"'),
    ('"name": "Casty"', '"name": "Pathquire"'),
    ('"name": "Cast"', '"name": "Pathquire"'),
    ("Learning list | Casty", "Learning list | Pathquire"),
    ("Learning list | Cast", "Learning list | Pathquire"),
    ("saved Casty study", "saved Pathquire study"),
    ("saved Cast study", "saved Pathquire study"),
    ("free on Casty", "free on Pathquire"),
    ("free on Cast", "free on Pathquire"),
    ("name: casty", "name: pathquire"),
    ("--name casty", "--name pathquire"),
    ("-t casty:latest", "-t pathquire:latest"),
    (" casty:latest", " pathquire:latest"),
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
        text = re.sub(r"\bCasty\b", "Pathquire", text)
        text = re.sub(r"\bcasty\b", "pathquire", text)
        # Avoid turning Pathquire into Pathquirequire if Cast already replaced
        text = re.sub(r"(?<![A-Za-z])Cast(?![A-Za-z])", "Pathquire", text)
        text = re.sub(r"(?<![A-Za-z])cast(?![A-Za-z])", "pathquire", text)
        if text != orig:
            path.write_text(text, encoding="utf-8")
            changed.append(str(path.relative_to(ROOT)))
    print(f"updated {len(changed)} files")
    for p in changed:
        print(p)


if __name__ == "__main__":
    main()
