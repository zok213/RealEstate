"""FastAPI application entry point."""

import logging
from pathlib import Path
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from api.schemas.response_schemas import HealthResponse
from api.routes import optim_router, dxf_router, estate_router

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Land Redistribution Algorithm API",
    description="API for testing land subdivision and redistribution algorithms",
    version="2.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Detect static file path
# In Docker, volume mounted to /app/static
# Locally, use ../static
static_path = Path("/app/static") if Path("/app/static").exists() else Path(__file__).parent.parent.parent / "static"

# Mount static files
app.mount("/static", StaticFiles(directory=str(static_path)), name="static")
logger.info(f"[STATIC] Serving static files from: {static_path}")

# Include routes
app.include_router(optim_router, prefix="/api")
app.include_router(dxf_router, prefix="/api")
app.include_router(estate_router, prefix="/api")


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint."""
    return HealthResponse(status="healthy", version="2.0.0")


@app.get("/")
async def root():
    """Serve the main index page."""
    return FileResponse(str(static_path / "index.html"))


@app.get("/upload")
async def upload_page():
    """Serve the upload page."""
    return FileResponse(str(static_path / "upload.html"))


@app.get("/estate/{estate_id}")
async def estate_detail(estate_id: str):
    """Serve the estate detail page."""
    return FileResponse(str(static_path / "estate-detail.html"))


@app.get("/map/{session_id}")
async def map_view(session_id: str):
    """Serve the full-screen map view."""
    return FileResponse(str(static_path / "full-screen-map-view.html"))


@app.get("/plots/{session_id}")
async def plots_list(session_id: str):
    """Serve the estate plots list page."""
    return FileResponse(str(static_path / "estate-plot-list.html"))


@app.get("/fullscreen-map/{session_id}")
async def fullscreen_map(session_id: str):
    """Serve the fullscreen map view (same as map view)."""
    return FileResponse(str(static_path / "full-screen-map-view.html"))


# @app.on_event("startup")
# async def startup_event():
#     """Log startup information."""
#     logger.info("Land Redistribution API started (v2.0.0 - Modular Architecture)")

# Startup logged directly
logger.info("Land Redistribution API initialized (v2.0.0)")
