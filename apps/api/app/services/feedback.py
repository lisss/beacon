from __future__ import annotations

import uuid
from datetime import datetime

from sqlmodel import Session, col, select

from app.models.resource_feedback import ResourceFeedback


def normalize_url(url: str) -> str:
    return (url or "").strip().rstrip("/")


def list_by_verdict(
    db: Session, session_id: str, verdict: str
) -> list[ResourceFeedback]:
    return list(
        db.exec(
            select(ResourceFeedback)
            .where(ResourceFeedback.session_id == session_id)
            .where(ResourceFeedback.verdict == verdict)
            .order_by(col(ResourceFeedback.created_at).desc())
        ).all()
    )


def irrelevant_urls(db: Session, session_id: str | None) -> set[str]:
    if not session_id:
        return set()
    rows = list_by_verdict(db, session_id, "irrelevant")
    return {normalize_url(r.url) for r in rows if r.url}


def upsert_feedback(
    db: Session,
    *,
    session_id: str,
    url: str,
    title: str,
    provider: str,
    kind: str,
    verdict: str,
) -> ResourceFeedback:
    url = normalize_url(url)
    if not url:
        raise ValueError("url is required")
    if verdict not in {"useful", "irrelevant"}:
        raise ValueError("verdict must be useful or irrelevant")

    existing = db.exec(
        select(ResourceFeedback)
        .where(ResourceFeedback.session_id == session_id)
        .where(ResourceFeedback.url == url)
    ).first()

    if existing:
        existing.verdict = verdict
        existing.title = title or existing.title
        existing.provider = provider or existing.provider
        existing.kind = kind or existing.kind
        existing.created_at = datetime.utcnow()
        db.add(existing)
        db.commit()
        db.refresh(existing)
        return existing

    row = ResourceFeedback(
        id=uuid.uuid4().hex,
        session_id=session_id,
        url=url,
        title=title or url,
        provider=provider or "",
        kind=kind or "",
        verdict=verdict,
        created_at=datetime.utcnow(),
    )
    db.add(row)
    db.commit()
    db.refresh(row)
    return row


def delete_feedback(db: Session, session_id: str, url: str) -> bool:
    url = normalize_url(url)
    row = db.exec(
        select(ResourceFeedback)
        .where(ResourceFeedback.session_id == session_id)
        .where(ResourceFeedback.url == url)
    ).first()
    if not row:
        return False
    db.delete(row)
    db.commit()
    return True


def feedback_public(row: ResourceFeedback) -> dict:
    return {
        "id": row.id,
        "url": row.url,
        "title": row.title,
        "provider": row.provider,
        "kind": row.kind,
        "verdict": row.verdict,
        "created_at": row.created_at.isoformat() + "Z",
    }
