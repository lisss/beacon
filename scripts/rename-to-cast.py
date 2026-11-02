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
    ("pathjbby.duckdns.org", "cast.duckdns.org"),
    ("pathjobby.duckdns.org", "cast.duckdns.org"),
    ("https://github.com/lisss/jbby", "https://github.com/lisss/cast"),
    ("https://github.com/lisss/jobify", "https://github.com/lisss/cast"),
    ("ghcr.io/lisss/jbby", "ghcr.io/lisss/cast"),
    ("ghcr.io/lisss/jobify", "ghcr.io/lisss/cast"),
    ("lisss/jbby", "lisss/cast"),
    ("lisss/jobify", "lisss/cast"),
    ("/opt/jbby", "/opt/cast"),
    ("/opt/jobify", "/opt/cast"),
    ("jbby.duckdns.org", "cast.duckdns.org"),
    ("DUCKDNS_SUBDOMAIN=pathjbby", "DUCKDNS_SUBDOMAIN=cast"),
    ("DUCKDNS_SUBDOMAIN=pathjobby", "DUCKDNS_SUBDOMAIN=cast"),
    ("DUCKDNS_SUBDOMAIN=jbby", "DUCKDNS_SUBDOMAIN=cast"),
    ("PathJMark", "CastMark"),
    ("Path-J + gap-bridge", "Cast mark (gap bridge)"),
    ("Path-J + gap bridge", "Cast mark (gap bridge)"),
    ("jbby-todo-changed", "cast-todo-changed"),
    ("jobify-todo-changed", "cast-todo-changed"),
    ("jbby_sid", "cast_sid"),
    ("jbby.sections", "cast.sections"),
    ("jbby.todo", "cast.todo"),
    ("jbby.ui", "cast.ui"),
    ("jbby.cv", "cast.cv"),
    ("jbby-cv", "cast-cv"),
    ("jobify.sections", "cast.sections"),
    ("jobify.todo", "cast.todo"),
    ("jobify.ui", "cast.ui"),
    ("jobify.cv", "cast.cv"),
    ("container_name: jobify-", "container_name: cast-"),
    ("container_name: jbby-", "container_name: cast-"),
    ("sqlite:////data/jobify.db", "sqlite:////data/cast.db"),
    ("sqlite:////data/jbby.db", "sqlite:////data/cast.db"),
    ("sqlite:////tmp/jbby.db", "sqlite:////tmp/cast.db"),
    ("sqlite:////tmp/jobify.db", "sqlite:////tmp/cast.db"),
    ("sqlite:///./jbby.db", "sqlite:///./cast.db"),
    ("sqlite:///./jobify.db", "sqlite:///./cast.db"),
    ("**/jbby.db", "**/cast.db"),
    ("apps/api/jbby.db", "apps/api/cast.db"),
    ("POSTGRES_USER: jbby", "POSTGRES_USER: cast"),
    ("POSTGRES_PASSWORD: jbby", "POSTGRES_PASSWORD: cast"),
    ("POSTGRES_DB: jbby", "POSTGRES_DB: cast"),
    ("postgresql+psycopg://jbby:jbby@", "postgresql+psycopg://cast:cast@"),
    ("pg_isready -U jbby -d jbby", "pg_isready -U cast -d cast"),
    ("jbby_pgdata", "cast_pgdata"),
    ("jbby/1.0", "cast/1.0"),
    ("jbby/0.1", "cast/0.1"),
    ("title=\"jbby API\"", "title=\"Cast API\""),
    ("[jbby] DB", "[cast] DB"),
    ("KEY_NAME:-jbby", "KEY_NAME:-cast"),
    ('SG_NAME="jbby-web"', 'SG_NAME="cast-web"'),
    ("Value=jbby", "Value=cast"),
    ('description "jbby HTTP/SSH"', 'description "cast HTTP/SSH"'),
    ("~/jbby", "~/cast"),
    ("${HOME}/jbby", "${HOME}/cast"),
    ("e.g. jbby", "e.g. cast"),
    ("e.g. `pathjbby`", "e.g. `cast`"),
    ("# Jobify", "# Cast"),
    ("Jobify", "Cast"),
    ("jbby is starting", "Cast is starting"),
    ("jbby is a free", "Cast is a free"),
    ("jbby shows", "Cast shows"),
    ("jbby helps", "Cast helps"),
    ("jbby maps", "Cast maps"),
    ("on jbby", "on Cast"),
    ("| jbby", "| Cast"),
    ("title = 'jbby'", "title = 'Cast'"),
    ("'jbby —", "'Cast —"),
    ('"jbby —', '"Cast —'),
    ('content="jbby"', 'content="Cast"'),
    ('aria-label="jbby"', 'aria-label="Cast"'),
    (">jbby</", ">Cast</"),
    ('site_name" content="jbby"', 'site_name" content="Cast"'),
    ('"name": "jbby"', '"name": "Cast"'),
    ("Learning list | jbby", "Learning list | Cast"),
    ("saved jbby study", "saved Cast study"),
    ("Deploy jbby", "Deploy Cast"),
    ("free on jbby", "free on Cast"),
    ("name: jbby", "name: cast"),
    ("--name jbby", "--name cast"),
    ("-t jbby:latest", "-t cast:latest"),
    (" jbby:latest", " cast:latest"),
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
        if path.name == "rename-to-cast.py":
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
        text = re.sub(r"\bjbby\b", "cast", text)
        text = re.sub(r"\bJbby\b", "Cast", text)
        text = re.sub(r"\bJBBY\b", "CAST", text)
        if text != orig:
            path.write_text(text, encoding="utf-8")
            changed.append(str(path.relative_to(ROOT)))
    print(f"updated {len(changed)} files")
    for p in changed:
        print(p)


if __name__ == "__main__":
    main()
