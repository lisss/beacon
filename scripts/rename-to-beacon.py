#!/usr/bin/env python3
"""Rename Medeina → Beacon (host: getbeacon.duckdns.org)."""
from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SKIP_DIRS = {".git", "node_modules", ".venv", "venv", "dist", "static", "__pycache__", "web-next-backup"}
SKIP_SUFFIX = {".png", ".jpg", ".jpeg", ".gif", ".webp", ".ico", ".woff", ".woff2", ".pdf", ".db"}

REPLACEMENTS = [
    ("medeina.duckdns.org", "getbeacon.duckdns.org"),
    ("https://github.com/lisss/medeina", "https://github.com/lisss/beacon"),
    ("ghcr.io/lisss/medeina", "ghcr.io/lisss/beacon"),
    ("lisss/medeina", "lisss/beacon"),
    ("/opt/medeina", "/opt/beacon"),
    ("/opt/pathquire", "/opt/beacon"),
    ("/opt/casty", "/opt/beacon"),
    ("/opt/cast", "/opt/beacon"),
    ("DUCKDNS_SUBDOMAIN=medeina", "DUCKDNS_SUBDOMAIN=getbeacon"),
    ("MedeinaMark", "BeaconMark"),
    ("PathquireMark", "BeaconMark"),
    ("medeina-todo-changed", "beacon-todo-changed"),
    ("medeina_sid", "beacon_sid"),
    ("medeina.sections", "beacon.sections"),
    ("medeina.todo", "beacon.todo"),
    ("medeina.ui", "beacon.ui"),
    ("medeina.cv", "beacon.cv"),
    ("medeina-cv", "beacon-cv"),
    ("container_name: medeina-", "container_name: beacon-"),
    ("sqlite:////data/medeina.db", "sqlite:////data/beacon.db"),
    ("sqlite:////tmp/medeina.db", "sqlite:////tmp/beacon.db"),
    ("sqlite:///./medeina.db", "sqlite:///./beacon.db"),
    ("**/medeina.db", "**/beacon.db"),
    ("title=\"Medeina API\"", "title=\"Beacon API\""),
    ("# Medeina", "# Beacon"),
    ("Deploy Medeina", "Deploy Beacon"),
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
        text = re.sub(r"\bMedeina\b", "Beacon", text)
        text = re.sub(r"\bmedeina\b", "beacon", text)
        if text != orig:
            path.write_text(text, encoding="utf-8")
            changed.append(str(path.relative_to(ROOT)))
    print(f"updated {len(changed)} files")
    for p in changed:
        print(p)


if __name__ == "__main__":
    main()
