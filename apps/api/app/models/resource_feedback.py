from datetime import datetime
from typing import Optional

from sqlmodel import Field, SQLModel


class ResourceFeedback(SQLModel, table=True):
    """Per-session verdict on a learning resource."""

    __tablename__ = "resource_feedback"

    id: str = Field(primary_key=True)
    session_id: str = Field(index=True)
    url: str = Field(index=True)
    title: str = ""
    provider: str = ""
    kind: str = ""
    # useful → TODO list; irrelevant → hidden from future insights
    verdict: str = Field(index=True)  # "useful" | "irrelevant"
    created_at: datetime = Field(default_factory=datetime.utcnow)
    notes: Optional[str] = None
