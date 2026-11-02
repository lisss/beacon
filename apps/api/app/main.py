from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, HTMLResponse, PlainTextResponse, Response
from fastapi.staticfiles import StaticFiles

from app.api.routes import router
from app.core.config import get_settings
from app.core.db import engine, init_db
from app.models import cv_upload as _cv_upload  # noqa: F401 — register table
from app.models import job as _job  # noqa: F401 — register table
from app.models import resource_feedback as _resource_feedback  # noqa: F401
from app.services.jobs import seed_sample_jobs
from app.services.seo import (
    build_robots_txt,
    build_role_page_html,
    build_sitemap_xml,
    title_from_slug,
)
from sqlmodel import Session

# Built Vite app (copied next to the API in Docker / Render builds).
STATIC_DIR = Path(__file__).resolve().parent.parent / "static"


@asynccontextmanager
async def lifespan(_: FastAPI):
    try:
        init_db()
        with Session(engine) as session:
            seed_sample_jobs(session)
    except Exception as exc:
        # Allow API to boot even if DB is temporarily unavailable
        print(f"[jbby] DB init warning: {exc}")
    yield


settings = get_settings()

app = FastAPI(
    title="jbby API",
    description="Job + learning insights aggregator",
    version="0.1.0",
    lifespan=lifespan,
)

_cors_origins = settings.cors_origins or ["*"]
# Browsers reject Allow-Origin: * together with credentials.
_cors_credentials = _cors_origins != ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=_cors_origins,
    allow_credentials=_cors_credentials,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router, prefix="/api")


@app.get("/api")
def api_root() -> dict:
    return {"name": "jbby-api", "docs": "/docs"}


@app.get("/robots.txt", response_class=PlainTextResponse)
def robots_txt() -> str:
    return build_robots_txt(settings.site_url)


@app.get("/sitemap.xml")
def sitemap_xml() -> Response:
    return Response(
        content=build_sitemap_xml(settings.site_url),
        media_type="application/xml",
        headers={"Cache-Control": "public, max-age=3600"},
    )


@app.get("/roles/{slug}", response_class=HTMLResponse)
def role_seo_page(slug: str) -> str:
    title = title_from_slug(slug)
    if not title:
        raise HTTPException(status_code=404, detail="Role not found")
    return build_role_page_html(settings.site_url, title)


@app.get("/google{code}.html")
def google_site_verification_file(code: str) -> Response:
    """
    Google Search Console HTML-file verification.
    Must return the exact body Google expects — not the SPA shell.
    """
    import re

    if not re.fullmatch(r"[A-Za-z0-9_-]{6,128}", code):
        raise HTTPException(status_code=404, detail="Not found")
    body = f"google-site-verification: google{code}.html\n"
    return Response(
        content=body,
        media_type="text/html; charset=utf-8",
        headers={"Cache-Control": "no-store"},
    )


def _spa_html() -> Response:
    # Always revalidate HTML so deploys pick up new hashed JS/CSS immediately.
    index = STATIC_DIR / "index.html"
    headers = {
        "Cache-Control": "no-cache, no-store, must-revalidate",
        "Pragma": "no-cache",
    }
    token = (settings.google_site_verification or "").strip()
    if not token:
        return FileResponse(index, headers=headers)

    html = index.read_text(encoding="utf-8")
    meta = f'<meta name="google-site-verification" content="{token}" />'
    if 'name="google-site-verification"' not in html:
        html = html.replace("</head>", f"    {meta}\n  </head>", 1)
    return Response(content=html, media_type="text/html; charset=utf-8", headers=headers)


if STATIC_DIR.is_dir():
    assets_dir = STATIC_DIR / "assets"
    if assets_dir.is_dir():
        app.mount("/assets", StaticFiles(directory=str(assets_dir)), name="assets")

    @app.get("/")
    def spa_index() -> FileResponse:
        return _spa_html()

    @app.get("/{full_path:path}")
    def spa_fallback(full_path: str) -> FileResponse:
        """Serve built files when present; otherwise index.html for client routes."""
        candidate = (STATIC_DIR / full_path).resolve()
        # Prevent path traversal outside STATIC_DIR.
        if candidate.is_file() and str(candidate).startswith(str(STATIC_DIR.resolve())):
            # Fingerprinted /assets/* can be cached; other static files stay short-lived.
            headers = {}
            if "/assets/" in str(candidate) or candidate.parent == assets_dir:
                headers["Cache-Control"] = "public, max-age=31536000, immutable"
            return FileResponse(candidate, headers=headers)
        return _spa_html()
else:

    @app.get("/")
    def root() -> dict:
        return {"name": "jbby-api", "docs": "/docs", "hint": "UI not bundled"}
