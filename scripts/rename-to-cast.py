#!/usr/bin/env python3
from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SKIP_DIRS = {
    ".git",
    "node_modules",
    ".venv",
    "venv",
    "dist",
    "static",
    "__pycache__",
    "web-next-backup",
    "AgentStores",
}
SKIP_SUFFIX = {
    ".png",
    ".jpg",
    ".jpeg",
    ".gif",
    ".webp",
    ".ico",
    ".woff",
    ".woff2",
    ".pdf",
    ".db",
}

REPLACEMENTS = [
    ("pathjbby.duckdns.org", "casty.duckdns.org"),
    ("pathjobby.duckdns.org", "casty.duckdns.org"),
    ("https://github.com/lisss/jbby", "https://github.com/lisss/casty"),
    ("https://github.com/lisss/jobify", "https://github.com/lisss/casty"),
    ("ghcr.io/lisss/jbby", "ghcr.io/lisss/casty"),
    ("ghcr.io/lisss/jobify", "ghcr.io/lisss/casty"),
    ("lisss/jbby", "lisss/casty"),
    ("lisss/jobify", "lisss/casty"),
    ("/opt/jbby", "/opt/casty"),
    ("/opt/jobify", "/opt/casty"),
    ("jbby.duckdns.org", "casty.duckdns.org"),
    ("DUCKDNS_SUBDOMAIN=pathjbby", "DUCKDNS_SUBDOMAIN=casty"),
    ("DUCKDNS_SUBDOMAIN=pathjobby", "DUCKDNS_SUBDOMAIN=casty"),
    ("DUCKDNS_SUBDOMAIN=jbby", "DUCKDNS_SUBDOMAIN=casty"),
    ("PathJMark", "CastyMark"),
    ("Path-J + gap-bridge", "Casty mark (gap bridge)"),
    ("Path-J + gap bridge", "Casty mark (gap bridge)"),
    ("jbby-todo-changed", "casty-todo-changed"),
    ("jobify-todo-changed", "casty-todo-changed"),
    ("jbby_sid", "casty_sid"),
    ("jbby.sections", "casty.sections"),
    ("jbby.todo", "casty.todo"),
    ("jbby.ui", "casty.ui"),
    ("jbby.cv", "casty.cv"),
    ("jbby-cv", "casty-cv"),
    ("jobify.sections", "casty.sections"),
    ("jobify.todo", "casty.todo"),
    ("jobify.ui", "casty.ui"),
    ("jobify.cv", "casty.cv"),
    ("container_name: jobify-", "container_name: casty-"),
    ("container_name: jbby-", "container_name: casty-"),
    ("sqlite:////data/jobify.db", "sqlite:////data/casty.db"),
    ("sqlite:////data/jbby.db", "sqlite:////data/casty.db"),
    ("sqlite:////tmp/jbby.db", "sqlite:////tmp/casty.db"),
    ("sqlite:////tmp/jobify.db", "sqlite:////tmp/casty.db"),
    ("sqlite:///./jbby.db", "sqlite:///./casty.db"),
    ("sqlite:///./jobify.db", "sqlite:///./casty.db"),
    ("**/jbby.db", "**/casty.db"),
    ("apps/api/jbby.db", "apps/api/casty.db"),
    ("POSTGRES_USER: jbby", "POSTGRES_USER: casty"),
    ("POSTGRES_PASSWORD: jbby", "POSTGRES_PASSWORD: casty"),
    ("POSTGRES_DB: jbby", "POSTGRES_DB: casty"),
    ("postgresql+psycopg://jbby:jbby@", "postgresql+psycopg://casty:casty@"),
    ("pg_isready -U jbby -d jbby", "pg_isready -U casty -d casty"),
    ("jbby_pgdata", "casty_pgdata"),
    ("jbby/1.0", "casty/1.0"),
    ("jbby/0.1", "casty/0.1"),
    ("title=\"jbby API\"", "title=\"Casty API\""),
    ("[jbby] DB", "[casty] DB"),
    ("KEY_NAME:-jbby", "KEY_NAME:-casty"),
    ('SG_NAME="jbby-web"', 'SG_NAME="casty-web"'),
    ("Value=jbby", "Value=casty"),
    ('description "jbby HTTP/SSH"', 'description "casty HTTP/SSH"'),
    ("~/jbby", "~/casty"),
    ("${HOME}/jbby", "${HOME}/casty"),
    ("e.g. jbby", "e.g. casty"),
    ("e.g. `pathjbby`", "e.g. `casty`"),
    ("# Jobify", "# Casty"),
    ("Jobify", "Casty"),
    ("jbby is starting", "Casty is starting"),
    ("jbby is a free", "Casty is a free"),
    ("jbby shows", "Casty shows"),
    ("jbby helps", "Casty helps"),
    ("jbby maps", "Casty maps"),
    ("on jbby", "on Casty"),
    ("| jbby", "| Casty"),
    ("title = 'jbby'", "title = 'Casty'"),
    ("'jbby —", "'Casty —"),
    ('"jbby —', '"Casty —'),
    ('content="jbby"', 'content="Casty"'),
    ('aria-label="jbby"', 'aria-label="Casty"'),
    (">jbby</", ">Casty</"),
    ('site_name" content="jbby"', 'site_name" content="Casty"'),
    ('"name": "jbby"', '"name": "Casty"'),
    ("Learning list | jbby", "Learning list | Casty"),
    ("saved jbby study", "saved Casty study"),
    ("Deploy jbby", "Deploy Casty"),
    ("free on jbby", "free on Casty"),
    ("name: jbby", "name: casty"),
    ("--name jbby", "--name casty"),
    ("-t jbby:latest", "-t casty:latest"),
    (" jbby:latest", " casty:latest"),
    ("~/.ssh/jbby-ec2", "~/.ssh/jobify-ec2"),  # keep existing key filename
    ("$HOME/.ssh/jbby-ec2", "$HOME/.ssh/jobify-ec2"),
]


def main() -> None:
    changed: list[str] = []
    for path in ROOT.rglob("*"):
        if not path.is_file():
            continue
        if any(p in SKIP_DIRS for p in path.parts):
            continue
        if path.name == "rename-to-casty.py":
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
        text = re.sub(r"\bjbby\b", "casty", text)
        text = re.sub(r"\bJbby\b", "Casty", text)
        text = re.sub(r"\bJBBY\b", "CASTY", text)
        if text != orig:
            path.write_text(text, encoding="utf-8")
            changed.append(str(path.relative_to(ROOT)))
    print(f"updated {len(changed)} files")
    for p in changed:
        print(p)


if __name__ == "__main__":
    main()
