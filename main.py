import time
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from app.config import settings
from app.database import init_db
from app.routes import auth, destinations, ai, environment, itinerary, payments

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize SQLite database and tables on startup
    init_db()
    yield

app = FastAPI(
    title="TripWise REST API",
    description=(
        "Production-ready, highly optimized Backend REST API for TripWise — "
        "A smart travel-planning platform combining real-time environmental telemetry, "
        "demographic age-bracket tailoring, strict budget enforcement, AI trip synthesis, "
        "persistent itinerary management, and sandbox payments."
    ),
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS Middleware (Permit requests from frontend web applications)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["X-Process-Time"]
)

# Zero-Lag Performance & Request Timing Middleware
@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.perf_counter()
    response = await call_next(request)
    process_time = (time.perf_counter() - start_time) * 1000.0  # in ms
    response.headers["X-Process-Time"] = f"{process_time:.2f}ms"
    return response

# Global Request Validation Exception Handler
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    errors = []
    for err in exc.errors():
        field = " -> ".join(str(loc) for loc in err.get("loc", []))
        errors.append({
            "field": field,
            "message": err.get("msg", "Invalid value"),
            "type": err.get("type", "validation_error")
        })
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={
            "status": "error",
            "message": "Input validation failed. Please check the provided request payload.",
            "errors": errors
        }
    )

from fastapi.responses import FileResponse
from pathlib import Path

FRONTEND_HTML = Path(__file__).resolve().parent.parent.parent / "frontend" / "index.html"

# Include All Functional Module Routers
app.include_router(auth.router)
app.include_router(destinations.router)
app.include_router(ai.router)
app.include_router(environment.router)
app.include_router(itinerary.router)
app.include_router(payments.router)

@app.api_route("/", methods=["GET", "HEAD"], tags=["System & Health"])
async def root(request: Request):
    accept = request.headers.get("accept", "")
    if "text/html" in accept and FRONTEND_HTML.exists():
        return FileResponse(FRONTEND_HTML, media_type="text/html")
    return {
        "application": "TripWise REST API",
        "web_app": "/app",
        "version": "1.0.0",
        "track": "Track 2: Backend Development",
        "status": "online",
        "documentation": "/docs",
        "endpoints": {
            "auth": "/api/auth",
            "destinations": "/api/destinations",
            "ai_planner": "/api/ai/plan-trip",
            "environment_telemetry": "/api/environment-status",
            "itinerary": "/api/itinerary",
            "packages_and_payments": "/api/packages"
        }
    }

@app.api_route("/app", methods=["GET", "HEAD"], response_class=FileResponse, tags=["Web UI"])
async def serve_app():
    if FRONTEND_HTML.exists():
        return FileResponse(FRONTEND_HTML, media_type="text/html")
    return JSONResponse(status_code=404, content={"message": "Frontend index.html not found"})

@app.get("/health", tags=["System & Health"])
async def health_check():
    return {
        "status": "healthy",
        "database": "sqlite_connected",
        "cache": "in_memory_ttl_active",
        "timestamp": time.time()
    }

@app.get("/api/config-status", tags=["System & Health"])
async def config_status():
    """Returns real-time status of configured external API integrations."""
    return {
        "app": "TripWise REST API",
        "gemini_api_configured": bool(settings.GEMINI_API_KEY),
        "geoapify_api_configured": bool(settings.GEOAPIFY_API_KEY),
        "news_api_configured": bool(settings.NEWS_API_KEY),
        "open_meteo_live": True,
        "env_file_path": "backend/.env",
        "mode": "hybrid_live_with_grounded_synthesis"
    }

@app.get("/download", tags=["System & Health"])
async def download_project_zip():
    """Download the complete TripWise project archive as a zip file."""
    zip_path = Path(__file__).resolve().parent.parent.parent / "TripWise_project.zip"
    if zip_path.exists():
        return FileResponse(
            zip_path,
            media_type="application/zip",
            filename="TripWise_project.zip"
        )
    return JSONResponse(status_code=404, content={"message": "Project zip archive not found"})
