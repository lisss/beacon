#!/usr/bin/env python3
from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SKIP_DIRS = {".git", "node_modules", ".venv", "venv", "dist", "static", "__pycache__", "web-next-backup"}
SKIP_SUFFIX = {".png", ".jpg", ".jpeg", ".gif", ".webp", ".ico", ".woff", ".woff2", ".pdf", ".db"}

# Order matters: longer / more specific first.
REPLACEMENTS = [
    ("getcasty.duckdns.org", "shine.duckdns.org"),
    ("getcast.duckdns.org", "shine.duckdns.org"),
    ("casty.duckdns.org", "shine.duckdns.org"),
    ("https://github.com/lisss/casty", "https://github.com/lisss/shine"),
    ("https://github.com/lisss/cast", "https://github.com/lisss/shine"),
    ("ghcr.io/lisss/casty", "ghcr.io/lisss/shine"),
    ("ghcr.io/lisss/cast", "ghcr.io/lisss/shine"),
    ("lisss/casty", "lisss/shine"),
    ("lisss/cast", "lisss/shine"),
    ("/opt/casty", "/opt/shine"),
    ("/opt/cast", "/opt/shine"),
    ("DUCKDNS_SUBDOMAIN=getcasty", "DUCKDNS_SUBDOMAIN=shine"),
    ("DUCKDNS_SUBDOMAIN=getcast", "DUCKDNS_SUBDOMAIN=shine"),
    ("DUCKDNS_SUBDOMAIN=casty", "DUCKDNS_SUBDOMAIN=shine"),
    ("CastyMark", "ShineMark"),
    ("CastMark", "ShineMark"),
    ("Casty mark (gap bridge)", "Shine mark (gap bridge)"),
    ("casty-todo-changed", "shine-todo-changed"),
    ("cast-todo-changed", "shine-todo-changed"),
    ("casty_sid", "shine_sid"),
    ("cast_sid", "shine_sid"),
    ("casty.sections", "shine.sections"),
    ("cast.sections", "shine.sections"),
    ("casty.todo", "shine.todo"),
    ("cast.todo", "shine.todo"),
    ("casty.ui", "shine.ui"),
    ("cast.ui", "shine.ui"),
    ("casty.cv", "shine.cv"),
    ("cast.cv", "shine.cv"),
    ("casty-cv", "shine-cv"),
    ("cast-cv", "shine-cv"),
    ("container_name: casty-", "container_name: shine-"),
    ("container_name: cast-", "container_name: shine-"),
    ("sqlite:////data/casty.db", "sqlite:////data/shine.db"),
    ("sqlite:////data/cast.db", "sqlite:////data/shine.db"),
    ("sqlite:////tmp/casty.db", "sqlite:////tmp/shine.db"),
    ("sqlite:////tmp/cast.db", "sqlite:////tmp/shine.db"),
    ("sqlite:///./casty.db", "sqlite:///./shine.db"),
    ("sqlite:///./cast.db", "sqlite:///./shine.db"),
    ("**/casty.db", "**/shine.db"),
    ("title=\"Casty API\"", "title=\"Shine API\""),
    ("title=\"Cast API\"", "title=\"Shine API\""),
    ("# Casty", "# Shine"),
    ("# Cast", "# Shine"),
    ("Deploy Casty", "Deploy Shine"),
    ("Deploy Cast", "Deploy Shine"),
    ("Casty is starting", "Shine is starting"),
    ("Cast is starting", "Shine is starting"),
    ("Casty is a free", "Shine is a free"),
    ("Cast is a free", "Shine is a free"),
    ("Casty shows", "Shine shows"),
    ("Cast shows", "Shine shows"),
    ("Casty helps", "Shine helps"),
    ("Cast helps", "Shine helps"),
    ("Casty maps", "Shine maps"),
    ("Cast maps", "Shine maps"),
    ("on Casty", "on Shine"),
    ("on Cast", "on Shine"),
    ("| Casty", "| Shine"),
    ("| Cast", "| Shine"),
    ("title = 'Casty'", "title = 'Shine'"),
    ("title = 'Cast'", "title = 'Shine'"),
    ("'Casty —", "'Shine —"),
    ("'Cast —", "'Shine —"),
    ('"Casty —', '"Shine —'),
    ('"Cast —', '"Shine —'),
    ('content="Casty"', 'content="Shine"'),
    ('content="Cast"', 'content="Shine"'),
    ('aria-label="Casty"', 'aria-label="Shine"'),
    ('aria-label="Cast"', 'aria-label="Shine"'),
    (">Casty</", ">Shine</"),
    (">Cast</", ">Shine</"),
    ('site_name" content="Casty"', 'site_name" content="Shine"'),
    ('site_name" content="Cast"', 'site_name" content="Shine"'),
    ('"name": "Casty"', '"name": "Shine"'),
    ('"name": "Cast"', '"name": "Shine"'),
    ("Learning list | Casty", "Learning list | Shine"),
    ("Learning list | Cast", "Learning list | Shine"),
    ("saved Casty study", "saved Shine study"),
    ("saved Cast study", "saved Shine study"),
    ("free on Casty", "free on Shine"),
    ("free on Cast", "free on Shine"),
    ("name: casty", "name: shine"),
    ("--name casty", "--name shine"),
    ("-t casty:latest", "-t shine:latest"),
    (" casty:latest", " shine:latest"),
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
        text = re.sub(r"\bCasty\b", "Shine", text)
        text = re.sub(r"\bcasty\b", "shine", text)
        # Word-boundary only, so an earlier replacement is not expanded again.
        text = re.sub(r"(?<![A-Za-z])Cast(?![A-Za-z])", "Shine", text)
        text = re.sub(r"(?<![A-Za-z])cast(?![A-Za-z])", "shine", text)
        if text != orig:
            path.write_text(text, encoding="utf-8")
            changed.append(str(path.relative_to(ROOT)))
    print(f"updated {len(changed)} files")
    for p in changed:
        print(p)


if __name__ == "__main__":
    main()
