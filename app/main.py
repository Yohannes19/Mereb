import os
from pathlib import Path

from fastapi import Depends, FastAPI, Request, status
from fastapi.responses import HTMLResponse, RedirectResponse, PlainTextResponse, Response, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app import models, services
from app.database import Base, engine, get_db
from app.dependencies import get_current_profile_from_token
from app.routers import auth, dashboard, public, api, admin

BASE_DIR = Path(__file__).resolve().parent.parent
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))

from app.core import csrf

app = FastAPI(
    title="Mereb",
    description="Public proof profiles for Ethiopian creators and small businesses.",
    version="0.1.0",
)

# Custom Error Handlers
@app.exception_handler(404)
async def not_found_exception_handler(request: Request, exc: Exception):
    return templates.TemplateResponse(
        request, "error.html", {"status_code": 404}, status_code=404
    )

@app.exception_handler(500)
async def server_error_exception_handler(request: Request, exc: Exception):
    return templates.TemplateResponse(
        request, "error.html", {"status_code": 500}, status_code=500
    )

# CSRF Protection initialization
@app.middleware("http")
async def add_csrf_token_to_context(request: Request, call_next):
    # Determine session ID for CSRF (using access_token)
    session_id = request.cookies.get("access_token", "anonymous")
    token = csrf.generate_csrf_token(session_id)
    # Inject into templates context
    request.state.csrf_token = token
    response = await call_next(request)
    return response

# To make csrf_token available in all templates
@app.middleware("http")
async def inject_csrf_token(request: Request, call_next):
    session_id = request.cookies.get("access_token", "anonymous")
    csrf_token = csrf.generate_csrf_token(session_id)
    templates.env.globals["csrf_token"] = csrf_token
    response = await call_next(request)
    return response

static_dir = BASE_DIR / "static"
app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")

app.include_router(auth.router)
app.include_router(dashboard.router)
app.include_router(public.router)
app.include_router(api.router)
app.include_router(admin.router)

@app.on_event("startup")
def on_startup():
    Base.metadata.create_all(bind=engine)


import datetime

@app.get("/robots.txt", response_class=PlainTextResponse)
def robots_txt():
    # Force robots.txt as flat text to follow Google's standard
    return "User-agent: *\nAllow: /\nDisallow: /dashboard/\nDisallow: /admin/\nSitemap: https://mereb.info/sitemap.xml"

@app.get("/sitemap.xml")
def sitemap_xml(db: Session = Depends(get_db)):
    """
    Dynamically generates sitemap.xml listing all public profiles.
    Ensures 0 discovery errors in Google Search Console.
    """
    try:
        profiles = db.query(models.Profile).all()
        now_date = datetime.date.today().strftime('%Y-%m-%d')
        
        xml_items = []
        # 1. Main Landing Page
        xml_items.append(f'<url><loc>https://mereb.info/</loc><lastmod>{now_date}</lastmod><changefreq>daily</changefreq><priority>1.0</priority></url>')
        
        # 2. Dynamic Creator Profiles
        for p in profiles:
            if not p.slug: continue
            
            # Use profile.updated_at if it exists, otherwise use today's date (fixes 500 error)
            lmod = p.updated_at.strftime('%Y-%m-%d') if p.updated_at else now_date
            
            xml_items.append(f'<url><loc>https://mereb.info/p/{p.slug}</loc><lastmod>{lmod}</lastmod><changefreq>weekly</changefreq><priority>0.8</priority></url>')
            
        # Minified XML string (GSC prefers no whitespace/indents in sitemaps)
        xml_str = '<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">' + "".join(xml_items) + '</urlset>'
        
        return Response(content=xml_str.lstrip(), media_type="application/xml; charset=utf-8")
        
    except Exception as e:
        # Fallback to absolute bare minimum if DB fails for any reason
        return Response(content='<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"><url><loc>https://mereb.info/</loc></url></urlset>', media_type="application/xml")

@app.get("/", response_class=HTMLResponse)
def index(request: Request, db: Session = Depends(get_db)):
    demo_profile = services.get_or_create_demo_profile(db)
    profile = get_current_profile_from_token(request, db)
    if profile:
        return RedirectResponse(url="/dashboard", status_code=status.HTTP_303_SEE_OTHER)
        
    return templates.TemplateResponse(
        request,
        "landing.html",
        {
            "request": request,
            "demo_profile": demo_profile,
        },
    )