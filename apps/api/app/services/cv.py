from __future__ import annotations

import re
from pathlib import Path

from pypdf import PdfReader

from app.services.skills import SKILL_ALIASES, extract_skills, normalize_skill


def extract_text_from_pdf(path: Path) -> str:
    reader = PdfReader(str(path))
    chunks: list[str] = []
    for page in reader.pages:
        chunks.append(page.extract_text() or "")
    return "\n".join(chunks)


def extract_skills_from_cv_text(text: str) -> list[str]:
    found: dict[str, str] = {}

    def add(raw: str) -> None:
        token = raw.strip().strip("•-*·|")
        token = re.sub(r"\s+", " ", token).strip(" .;:")
        if not token or len(token) < 2 or len(token) > 48:
            return
        if re.search(r"\d{4}|@|http|www\.|curriculum|vitae|resume", token, re.I):
            return
        if token.lower() in {"and", "or", "skills", "technologies", "tools", "proficient"}:
            return

        canonical = normalize_skill(token)
        if canonical:
            found[canonical.lower()] = canonical
            return

        if re.fullmatch(r"[A-Za-z][A-Za-z0-9.+#/\- ]{1,46}", token):
            key = token.lower()
            if key in SKILL_ALIASES:
                found[key] = SKILL_ALIASES[key]
            else:
                display = token if token.isupper() and len(token) <= 5 else token.title() if token.islower() else token
                found[key] = display

    for skill in extract_skills(text):
        found[skill.lower()] = skill

    section = _skills_section(text)
    if section:
        for part in re.split(r"[,;|/•·\n]+", section):
            part = re.sub(r"\([^)]*\)", "", part)
            add(part)

    return sorted(found.values(), key=lambda s: s.lower())


def _skills_section(text: str) -> str | None:
    match = re.search(
        r"(?is)(?:skills|technical skills|tech stack|technologies|tools)\s*[:\-]?\s*\n?(.+?)(?:\n\s*\n|\n(?=[A-Z][A-Za-z ]{2,30}\s*$)|\n(?:experience|education|projects|work history|employment|summary|profile)\b|$)",
        text,
    )
    if not match:
        return None
    return match.group(1)
