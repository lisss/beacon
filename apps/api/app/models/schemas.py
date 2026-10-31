from typing import Optional

from pydantic import BaseModel, Field


class SkillStat(BaseModel):
    skill: str
    count: int = 0
    percentage: float


class ResourceReview(BaseModel):
    author: str = ""
    rating: Optional[float] = None
    comment: str
    url: str = ""
    source: str = ""


class ResourceOut(BaseModel):
    kind: str
    title: str
    url: str
    provider: str = ""
    skills: list[str] = Field(default_factory=list)
    description: str = ""
    estimated_hours: Optional[float] = None
    # Higher = more valuable for this role/skill mix (used for ranking).
    value_score: float = 0.0
    rating: Optional[float] = None
    rating_count: Optional[int] = None
    reviews: list[ResourceReview] = Field(default_factory=list)
    # Short guidance for how to use this resource in a study plan.
    study_tip: str = ""


class RoadmapStep(BaseModel):
    order: int
    title: str
    skills: list[str]
    estimated_hours: float
    how_to: str = ""
    resources: list[ResourceOut] = Field(default_factory=list)


class CurriculumItem(BaseModel):
    order: int
    phase: str
    focus: str
    hours: float
    structure: str
    resource_titles: list[str] = Field(default_factory=list)


class InsightsRequest(BaseModel):
    query: str = Field(min_length=1, examples=["Python Backend Engineer"])
    location: str = ""
    cv_skills: list[str] = Field(default_factory=list)


class SkillsForRoleRequest(BaseModel):
    role: str = Field(min_length=1)
    skills: list[str] = Field(default_factory=list)


class InsightsResponse(BaseModel):
    query: str
    location: str
    # Position requirements (importance in `percentage`)
    requirements: list[SkillStat]
    matched_skills: list[str] = Field(default_factory=list)
    partial_skills: list[str] = Field(default_factory=list)
    missing_skills: list[SkillStat]
    unmatched_cv_skills: list[str] = Field(default_factory=list)
    interview_questions: list[ResourceOut]
    books: list[ResourceOut]
    courses: list[ResourceOut]
    certifications: list[ResourceOut]
    roadmap: list[RoadmapStep]
    curriculum: list[CurriculumItem] = Field(default_factory=list)
    # Full expandable lists (UI shows 5, then +10 more).
    roadmap_more: list[RoadmapStep] = Field(default_factory=list)
    curriculum_more: list[CurriculumItem] = Field(default_factory=list)
    estimated_study_hours: float


class ResourceFeedbackRequest(BaseModel):
    url: str = Field(min_length=1)
    title: str = ""
    provider: str = ""
    kind: str = ""
    verdict: str = Field(examples=["useful", "irrelevant"])


class HealthResponse(BaseModel):
    status: str
    database: str
