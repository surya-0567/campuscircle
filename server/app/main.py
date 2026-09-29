from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.config import settings
from app.database import Base, engine
from app import models  # noqa: F401 - ensures models are registered on Base before create_all
from app.routers import auth, users, opportunities, applications, bookmarks, admin

# Create tables if they don't exist yet (simple approach suitable for a college prototype;
# for production, use a migration tool such as Alembic instead).
Base.metadata.create_all(bind=engine)

app = FastAPI(title="CampusCircle API", description="Hyperlocal Student Opportunity Network", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.client_origin] if settings.client_origin != "*" else ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(users.router)
app.include_router(opportunities.router)
app.include_router(applications.router)
app.include_router(bookmarks.router)
app.include_router(admin.router)


@app.get("/api/health")
def health():
    return {"status": "ok"}


# ---- Custom 404 handler for unknown /api/* routes (keeps JSON, not HTML) ----
# IMPORTANT: for any status code other than a genuine "route not found" 404,
# we must return the exception's own response, not re-raise it - raising
# from inside an exception handler turns it into an unhandled 500 error.
@app.exception_handler(StarletteHTTPException)
async def custom_404(request, exc):
    if request.url.path.startswith("/api") and exc.status_code == 404:
        return JSONResponse(status_code=404, content={"detail": f"Route not found: {request.url.path}"})
    return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail}, headers=getattr(exc, "headers", None))


# ---- Serve the frontend (client/) as static files, so the whole app runs from one server ----
CLIENT_DIR = Path(__file__).resolve().parent.parent.parent / "client"

if CLIENT_DIR.exists():
    app.mount("/css", StaticFiles(directory=CLIENT_DIR / "css"), name="css")
    app.mount("/js", StaticFiles(directory=CLIENT_DIR / "js"), name="js")

    @app.get("/", include_in_schema=False)
    async def serve_index():
        return FileResponse(CLIENT_DIR / "index.html")

    @app.get("/login", include_in_schema=False)
    async def serve_login():
        return FileResponse(CLIENT_DIR / "login.html")

    @app.get("/register", include_in_schema=False)
    async def serve_register():
        return FileResponse(CLIENT_DIR / "register.html")

    @app.get("/app", include_in_schema=False)
    async def serve_app():
        return FileResponse(CLIENT_DIR / "app.html")
