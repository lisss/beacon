from __future__ import annotations

from app.models.schemas import CurriculumItem, ResourceOut, RoadmapStep
from app.services.online_resources import (
    fetch_learning_bundle,
    fetch_resources_for_topics,
    rank_resources,
)
from app.services.skills import canonicalize_cv_skill, missing_skills


def _unique(skills: list[str]) -> list[str]:
    seen: set[str] = set()
    out: list[str] = []
    for skill in skills:
        key = skill.lower()
        if key in seen:
            continue
        seen.add(key)
        out.append(skill)
    return out


def learning_topics(
    role_skills: list[str],
    gap_skills: list[str],
    stack_skills: list[str],
) -> list[str]:
    topics: list[str] = []
    for skill in stack_skills:
        topics.append(skill)
    for skill in gap_skills:
        topics.append(skill)
    if not topics:
        topics.extend(role_skills)
    return _unique(topics)


def gather_online_resources(
    role: str,
    stack_skills: list[str],
    gap_skills: list[str],
    *,
    blocked_urls: set[str] | None = None,
) -> dict[str, list[ResourceOut]]:
    return fetch_learning_bundle(
        role, stack_skills, gap_skills, blocked_urls=blocked_urls
    )


def _resources_for_chunk(
    chunk: list[str],
    role: str,
    bundle: dict[str, list[ResourceOut]] | None,
) -> list[ResourceOut]:
    needles = [c.lower() for c in chunk]
    picked: list[ResourceOut] = []
    if bundle:
        for kind in ("books", "courses", "interview_questions", "certifications"):
            for item in bundle.get(kind, []):
                hay = f"{item.title} {item.description} {' '.join(item.skills)}".lower()
                if any(n in hay for n in needles):
                    picked.append(item)
        picked = rank_resources(_dedupe_resources(picked))
        if len(picked) >= 2:
            return picked[:4]
    # Live top-up only when the shared bundle didn't cover this step.
    return fetch_resources_for_topics(
        chunk, role, kinds={"book", "course"}, limit_per_topic=2
    )[:4]


def _dedupe_resources(items: list[ResourceOut]) -> list[ResourceOut]:
    seen: set[str] = set()
    out: list[ResourceOut] = []
    for item in items:
        key = (item.url or item.title).lower()
        if key in seen:
            continue
        seen.add(key)
        out.append(item)
    return out


def _step_how_to(chunk: list[str], related: list[ResourceOut], hours: float) -> str:
    titles = [r.title for r in related[:2]]
    material = f" using {', '.join(titles)}" if titles else ""
    weeks = max(1, round(hours / 6))
    return (
        f"Spend ~{hours:.0f}h over ~{weeks} week(s) on {', '.join(chunk)}. "
        f"Start with the highest-rated material{material}; "
        "do one hands-on exercise after each session; end with a short write-up or demo."
    )


def build_roadmap(
    role: str,
    top_skills: list[tuple[str, int, float]],
    cv_skills: list[str],
    bundle: dict[str, list[ResourceOut]] | None = None,
) -> tuple[list[RoadmapStep], float]:
    role_skills = [skill for skill, _, _ in top_skills]
    stack = _unique(
        [s for s in (canonicalize_cv_skill(x) for x in cv_skills) if s]
    )[:8]
    gap_rows = missing_skills(top_skills, cv_skills, min_percentage=15.0)[:10]
    gap_names = [skill for skill, _, _ in gap_rows]
    stack_lower = {s.lower() for s in stack}
    gap_lower = {s.lower() for s in gap_names}

    focus_skills: list[str] = []
    for skill in gap_names:
        focus_skills.append(skill)
    for skill in role_skills:
        key = skill.lower()
        if key in stack_lower or key in {s.lower() for s in focus_skills}:
            continue
        focus_skills.append(skill)

    if not stack and not focus_skills:
        focus_skills = role_skills[:10]

    # CV covers most of the role → still offer Deepen steps so the roadmap
    # doesn't collapse to only "Strengthen" + interview polish.
    if len(focus_skills) < 8:
        for skill in role_skills:
            if len(focus_skills) >= 10:
                break
            if skill.lower() in {s.lower() for s in focus_skills}:
                continue
            if skill.lower() in stack_lower:
                focus_skills.append(skill)

    steps: list[RoadmapStep] = []
    total_hours = 0.0
    order = 1

    # One combined stack section — avoid repeating "Strengthen your stack" per skill.
    if stack:
        related = _resources_for_chunk(stack, role, bundle)
        hours = sum((r.estimated_hours or 6) for r in related[:3]) or 12.0
        hours = min(max(hours, 8.0), 36.0)
        total_hours += hours
        steps.append(
            RoadmapStep(
                order=order,
                title="Strengthen your stack",
                skills=stack,
                estimated_hours=round(hours, 1),
                how_to=_step_how_to(stack, related, hours),
                resources=related,
            )
        )
        order += 1

    for skill in focus_skills:
        if order > 14:
            break
        chunk = [skill]
        related = _resources_for_chunk(chunk, role, bundle)
        hours = sum((r.estimated_hours or 8) for r in related[:2]) or 10.0
        hours = min(hours, 28.0)
        total_hours += hours
        if skill.lower() in gap_lower or skill.lower() not in stack_lower:
            title = f"Focus: {skill}"
        else:
            title = f"Deepen: {skill}"
        steps.append(
            RoadmapStep(
                order=order,
                title=title,
                skills=chunk,
                estimated_hours=round(hours, 1),
                how_to=_step_how_to(chunk, related, hours),
                resources=related,
            )
        )
        order += 1

    polish: list[ResourceOut] = []
    if bundle:
        polish.extend(bundle.get("interview_questions", [])[:2])
        polish.extend(bundle.get("courses", [])[:1])
        polish = rank_resources(_dedupe_resources(polish))
    steps.append(
        RoadmapStep(
            order=order,
            title="Interview polish & portfolio",
            skills=_unique([*stack[:2], *focus_skills[:2], "System Design"]),
            estimated_hours=12,
            how_to=(
                "In the final ~12h: answer 6–8 interview prompts under a timer, "
                "revise weak answers, and ship a small portfolio piece that uses your new skills."
            ),
            resources=polish[:3],
        )
    )
    total_hours += 12
    return steps[:15], round(total_hours, 1)


def build_curriculum(
    role: str,
    bundle: dict[str, list[ResourceOut]],
    roadmap: list[RoadmapStep],
) -> list[CurriculumItem]:
    spine = rank_resources(
        _dedupe_resources([*(bundle.get("books") or []), *(bundle.get("courses") or [])])
    )[:12]
    certs = rank_resources(bundle.get("certifications") or [])[:2]
    interviews = rank_resources(bundle.get("interview_questions") or [])[:3]

    items: list[CurriculumItem] = []
    order = 1
    cumulative = 0.0

    if roadmap:
        first = roadmap[0]
        hours = min(first.estimated_hours, 10)
        cumulative += hours
        items.append(
            CurriculumItem(
                order=order,
                phase="Week 1 — Orient",
                focus=f"Map the role ({role}) and pick your primary materials",
                hours=hours,
                structure=(
                    "Skim role requirements, pick 1 book + 1 course from the top of the lists "
                    "(highest value first), and schedule recurring study blocks."
                ),
                resource_titles=[r.title for r in first.resources[:2]],
            )
        )
        order += 1

    week = 2
    for res in spine:
        hours = float(res.estimated_hours or (28 if res.kind == "book" else 12))
        # Curriculum shows a realistic weekly slice when a resource is long.
        phase_hours = min(hours, 16.0) if res.kind == "book" else min(hours, 12.0)
        cumulative += phase_hours
        if res.kind == "book":
            structure = (
                f"Read ~{max(20, int((res.estimated_hours or 25) * 2))} pages equivalent "
                f"this phase (~{phase_hours:.0f}h). {res.study_tip or ''} "
                "After each chapter, write 3 bullets you can apply on a real task."
            )
            phase = f"Weeks {week}–{week + 1} — Deep read"
            week += 2
        else:
            structure = (
                f"Complete the course path in ~{phase_hours:.0f}h of focused work. "
                f"{res.study_tip or ''} Reproduce one demo project without looking at solutions."
            )
            phase = f"Week {week} — Guided practice"
            week += 1
        items.append(
            CurriculumItem(
                order=order,
                phase=phase,
                focus=res.title,
                hours=round(phase_hours, 1),
                structure=structure.strip(),
                resource_titles=[res.title],
            )
        )
        order += 1
        if order > 13:
            break

    if certs and order <= 14:
        c = certs[0]
        hours = float(c.estimated_hours or 20)
        phase_hours = min(hours, 14)
        cumulative += phase_hours
        items.append(
            CurriculumItem(
                order=order,
                phase=f"Week {week} — Credential check",
                focus=c.title,
                hours=round(phase_hours, 1),
                structure=(
                    "Only if the role lists a cert: outline domains, drill weak areas, "
                    "then 2 timed practice exams. Skip if not required."
                ),
                resource_titles=[c.title],
            )
        )
        order += 1
        week += 1

    if interviews:
        hours = round(sum((i.estimated_hours or 1.5) for i in interviews[:3]), 1)
        hours = max(6.0, min(hours * 2, 12.0))
        cumulative += hours
        items.append(
            CurriculumItem(
                order=order,
                phase=f"Week {week} — Interview drill",
                focus="Timed Q&A + storytelling",
                hours=hours,
                structure=(
                    "Answer top interview prompts cold, then refine. "
                    "Record one mock round; fix the weakest answer each day."
                ),
                resource_titles=[i.title for i in interviews[:3]],
            )
        )

    return items[:15]
