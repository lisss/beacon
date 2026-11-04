from __future__ import annotations

import html
import json
import re
from datetime import date

from app.services.roles import ROLE_TITLES, requirements_for_role

_SLUG_RE = re.compile(r"[^a-z0-9]+")


def role_slug(title: str) -> str:
    slug = _SLUG_RE.sub("-", title.strip().lower()).strip("-")
    return slug or "role"


def title_from_slug(slug: str) -> str | None:
    needle = slug.strip().lower().strip("-")
    if not needle:
        return None
    for title in ROLE_TITLES:
        if role_slug(title) == needle:
            return title
    soft = needle.replace("-", " ")
    for title in ROLE_TITLES:
        if title.lower() == soft:
            return title
    return None


def sitemap_role_slugs() -> list[tuple[str, str]]:
    seen: set[str] = set()
    out: list[tuple[str, str]] = []
    for title in ROLE_TITLES:
        slug = role_slug(title)
        if slug in seen:
            continue
        seen.add(slug)
        out.append((slug, title))
    return out


def build_robots_txt(site: str) -> str:
    site = site.rstrip("/")
    return (
        "User-agent: *\n"
        "Allow: /\n"
        "Disallow: /api/\n"
        "Disallow: /learning-list\n"
        "\n"
        f"Sitemap: {site}/sitemap.xml\n"
    )


def build_sitemap_xml(site: str) -> str:
    site = site.rstrip("/")
    today = date.today().isoformat()
    urls = [
        ("/", "1.0", "weekly"),
    ]
    for slug, _title in sitemap_role_slugs():
        urls.append((f"/roles/{slug}", "0.8", "weekly"))

    parts = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">',
    ]
    for path, priority, freq in urls:
        parts.append("  <url>")
        parts.append(f"    <loc>{html.escape(site + path)}</loc>")
        parts.append(f"    <lastmod>{today}</lastmod>")
        parts.append(f"    <changefreq>{freq}</changefreq>")
        parts.append(f"    <priority>{priority}</priority>")
        parts.append("  </url>")
    parts.append("</urlset>")
    return "\n".join(parts) + "\n"


def build_role_page_html(site: str, title: str) -> str:
    site = site.rstrip("/")
    slug = role_slug(title)
    reqs = requirements_for_role(title)
    esc_title = html.escape(title)
    page_title = html.escape(f"{title} skills & learning path | Medeina")
    description = html.escape(
        f"See typical {title} role requirements, ranked skills, and a study plan "
        f"with books, courses, and interview prep on Medeina."
    )
    canonical = html.escape(f"{site}/roles/{slug}")
    app_link = html.escape(f"{site}/?q={title}")

    skill_items = "\n".join(
        f"      <li><strong>{html.escape(skill)}</strong>"
        f" — importance {int(pct)}%</li>"
        for skill, pct in reqs[:15]
    )
    if not skill_items:
        skill_items = "      <li>Typical skills for this role will appear after you open the planner.</li>"

    skill_names = ", ".join(s for s, _ in reqs[:8]) or title

    json_ld = {
        "@context": "https://schema.org",
        "@type": "WebPage",
        "name": f"{title} learning path",
        "description": (
            f"Typical requirements and learning resources for a {title} role."
        ),
        "url": f"{site}/roles/{slug}",
        "isPartOf": {
            "@type": "WebSite",
            "name": "Medeina",
            "url": site,
        },
        "about": {
            "@type": "Occupation",
            "name": title,
            "skills": skill_names,
        },
    }
    ld_raw = json.dumps(json_ld, ensure_ascii=True)

    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>{page_title}</title>
  <meta name="description" content="{description}" />
  <link rel="canonical" href="{canonical}" />
  <meta name="robots" content="index,follow,max-image-preview:large" />
  <meta property="og:type" content="website" />
  <meta property="og:site_name" content="Medeina" />
  <meta property="og:title" content="{page_title}" />
  <meta property="og:description" content="{description}" />
  <meta property="og:url" content="{canonical}" />
  <meta property="og:image" content="{html.escape(site)}/og.svg" />
  <meta name="twitter:card" content="summary_large_image" />
  <meta name="twitter:title" content="{page_title}" />
  <meta name="twitter:description" content="{description}" />
  <link rel="icon" href="/favicon.svg" type="image/svg+xml" />
  <script type="application/ld+json">{ld_raw}</script>
  <style>
    :root {{ color-scheme: light; --ink:#1c2422; --muted:#5f6d69; --brand:#1f4f4a; --line:rgba(28,36,34,.12); --bg:#f6f8f7; --card:#eef6f3; }}
    body {{ margin:0; font-family:"Plus Jakarta Sans",system-ui,sans-serif; color:var(--ink); background:var(--bg); line-height:1.55; }}
    main {{ max-width:42rem; margin:0 auto; padding:2.5rem 1.25rem 4rem; }}
    a {{ color:var(--brand); }}
    h1 {{ font-size:clamp(1.5rem,4vw,2rem); letter-spacing:-.03em; color:var(--brand); margin:0 0 .75rem; }}
    .card {{ background:var(--card); border:1px solid var(--line); border-radius:.5rem; padding:1.25rem 1.35rem; margin:1.5rem 0; }}
    .cta {{ display:inline-block; margin-top:1rem; padding:.7rem 1.1rem; background:var(--brand); color:#fff; text-decoration:none; border-radius:.375rem; font-weight:600; }}
    ul {{ padding-left:1.15rem; }}
    li {{ margin:.35rem 0; }}
    .muted {{ color:var(--muted); }}
    footer {{ margin-top:2.5rem; font-size:.875rem; color:var(--muted); }}
  </style>
</head>
<body>
  <main>
    <p class="muted"><a href="{html.escape(site)}/">Medeina</a> · Role guide</p>
    <h1>{esc_title}: skills &amp; learning path</h1>
    <p>
      Medeina maps what a <strong>{esc_title}</strong> role typically needs,
      then helps you plan books, courses, certifications, and interview prep
      against your own skills or CV.
    </p>
    <div class="card">
      <h2>Typical requirements</h2>
      <p class="muted">Ranked by how often they show up for this kind of role.</p>
      <ul>
{skill_items}
      </ul>
      <a class="cta" href="{app_link}">Plan your learning for {esc_title}</a>
    </div>
    <p>
      Upload a CV or paste skills to see gaps, a curriculum, trusted resources,
      and a personalised roadmap — free on Medeina.
    </p>
    <footer>
      <a href="{html.escape(site)}/sitemap.xml">Sitemap</a>
      · More roles on <a href="{html.escape(site)}/">Medeina</a>
    </footer>
  </main>
</body>
</html>
"""
