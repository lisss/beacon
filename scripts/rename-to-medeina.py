#!/usr/bin/env python3
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
    ("https://github.com/lisss/casty", "https://github.com/lisss/medeina"),
    ("https://github.com/lisss/cast", "https://github.com/lisss/medeina"),
    ("ghcr.io/lisss/casty", "ghcr.io/lisss/medeina"),
    ("ghcr.io/lisss/cast", "ghcr.io/lisss/medeina"),
    ("lisss/casty", "lisss/medeina"),
    ("lisss/cast", "lisss/medeina"),
    ("/opt/casty", "/opt/medeina"),
    ("/opt/cast", "/opt/medeina"),
    ("DUCKDNS_SUBDOMAIN=getcasty", "DUCKDNS_SUBDOMAIN=pathquire"),
    ("DUCKDNS_SUBDOMAIN=getcast", "DUCKDNS_SUBDOMAIN=pathquire"),
    ("DUCKDNS_SUBDOMAIN=casty", "DUCKDNS_SUBDOMAIN=pathquire"),
    ("CastyMark", "MedeinaMark"),
    ("CastMark", "MedeinaMark"),
    ("Casty mark (gap bridge)", "Medeina mark (gap bridge)"),
    ("casty-todo-changed", "medeina-todo-changed"),
    ("cast-todo-changed", "medeina-todo-changed"),
    ("casty_sid", "medeina_sid"),
    ("cast_sid", "medeina_sid"),
    ("casty.sections", "medeina.sections"),
    ("cast.sections", "medeina.sections"),
    ("casty.todo", "medeina.todo"),
    ("cast.todo", "medeina.todo"),
    ("casty.ui", "medeina.ui"),
    ("cast.ui", "medeina.ui"),
    ("casty.cv", "medeina.cv"),
    ("cast.cv", "medeina.cv"),
    ("casty-cv", "medeina-cv"),
    ("cast-cv", "medeina-cv"),
    ("container_name: casty-", "container_name: medeina-"),
    ("container_name: cast-", "container_name: medeina-"),
    ("sqlite:////data/casty.db", "sqlite:////data/medeina.db"),
    ("sqlite:////data/cast.db", "sqlite:////data/medeina.db"),
    ("sqlite:////tmp/casty.db", "sqlite:////tmp/medeina.db"),
    ("sqlite:////tmp/cast.db", "sqlite:////tmp/medeina.db"),
    ("sqlite:///./casty.db", "sqlite:///./medeina.db"),
    ("sqlite:///./cast.db", "sqlite:///./medeina.db"),
    ("**/casty.db", "**/medeina.db"),
    ("title=\"Casty API\"", "title=\"Medeina API\""),
    ("title=\"Cast API\"", "title=\"Medeina API\""),
    ("# Casty", "# Medeina"),
    ("# Cast", "# Medeina"),
    ("Deploy Casty", "Deploy Medeina"),
    ("Deploy Cast", "Deploy Medeina"),
    ("Casty is starting", "Medeina is starting"),
    ("Cast is starting", "Medeina is starting"),
    ("Casty is a free", "Medeina is a free"),
    ("Cast is a free", "Medeina is a free"),
    ("Casty shows", "Medeina shows"),
    ("Cast shows", "Medeina shows"),
    ("Casty helps", "Medeina helps"),
    ("Cast helps", "Medeina helps"),
    ("Casty maps", "Medeina maps"),
    ("Cast maps", "Medeina maps"),
    ("on Casty", "on Medeina"),
    ("on Cast", "on Medeina"),
    ("| Casty", "| Medeina"),
    ("| Cast", "| Medeina"),
    ("title = 'Casty'", "title = 'Medeina'"),
    ("title = 'Cast'", "title = 'Medeina'"),
    ("'Casty —", "'Medeina —"),
    ("'Cast —", "'Medeina —"),
    ('"Casty —', '"Medeina —'),
    ('"Cast —', '"Medeina —'),
    ('content="Casty"', 'content="Medeina"'),
    ('content="Cast"', 'content="Medeina"'),
    ('aria-label="Casty"', 'aria-label="Medeina"'),
    ('aria-label="Cast"', 'aria-label="Medeina"'),
    (">Casty</", ">Medeina</"),
    (">Cast</", ">Medeina</"),
    ('site_name" content="Casty"', 'site_name" content="Medeina"'),
    ('site_name" content="Cast"', 'site_name" content="Medeina"'),
    ('"name": "Casty"', '"name": "Medeina"'),
    ('"name": "Cast"', '"name": "Medeina"'),
    ("Learning list | Casty", "Learning list | Medeina"),
    ("Learning list | Cast", "Learning list | Medeina"),
    ("saved Casty study", "saved Medeina study"),
    ("saved Cast study", "saved Medeina study"),
    ("free on Casty", "free on Medeina"),
    ("free on Cast", "free on Medeina"),
    ("name: casty", "name: medeina"),
    ("--name casty", "--name medeina"),
    ("-t casty:latest", "-t medeina:latest"),
    (" casty:latest", " medeina:latest"),
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
        text = re.sub(r"\bCasty\b", "Medeina", text)
        text = re.sub(r"\bcasty\b", "medeina", text)
        # Word-boundary only, so an earlier replacement is not expanded again.
        text = re.sub(r"(?<![A-Za-z])Cast(?![A-Za-z])", "Medeina", text)
        text = re.sub(r"(?<![A-Za-z])cast(?![A-Za-z])", "medeina", text)
        if text != orig:
            path.write_text(text, encoding="utf-8")
            changed.append(str(path.relative_to(ROOT)))
    print(f"updated {len(changed)} files")
    for p in changed:
        print(p)


if __name__ == "__main__":
    main()
