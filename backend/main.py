"""
FlyerFlutter FastAPI Application
Canadian Grocery Flyer Comparison API

Production-ready FastAPI application with:
- Google Places API integration
- Unofficial Flipp API integration  
- SQLite database with SQLAlchemy
- Background scheduler
- CORS middleware
- Static file serving
"""

import logging
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, Response, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from .config import settings
from .database import init_db
from .api.routes import router
from .services import start_scheduler, shutdown_scheduler

# Configure logging
logging.basicConfig(
    level=logging.INFO if not settings.DEBUG else logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    FastAPI lifespan event handler.
    
    Manages application startup and shutdown:
    - Initialize database
    - Start background scheduler
    - Cleanup on shutdown
    """
    # Startup
    logger.info("🚀 Starting FlyerFlutter application")
    
    try:
        # Initialize database
        logger.info("📊 Initializing database...")
        init_db()
        
        # Start background scheduler
        logger.info("⏰ Starting background scheduler...")
        start_scheduler()
        
        # Log service status
        logger.info("✅ Application startup completed successfully")
        logger.info(f"🌍 Environment: {'Development' if settings.DEBUG else 'Production'}")
        logger.info(f"📍 Google Places API: {'Available' if settings.GOOGLE_API_KEY else 'Not configured'}")
        logger.info("🏪 Flipp Service: Available (unofficial API)")
        
    except Exception as e:
        logger.error(f"❌ Startup failed: {e}")
        raise
    
    yield  # Application runs here
    
    # Shutdown
    logger.info("🛑 Shutting down FlyerFlutter application")
    
    try:
        # Stop background scheduler
        logger.info("⏰ Stopping background scheduler...")
        shutdown_scheduler()
        
        logger.info("✅ Application shutdown completed successfully")
        
    except Exception as e:
        logger.error(f"❌ Shutdown error: {e}")


# Create FastAPI application  
app = FastAPI(
    title="FlyerFlutter API v1.1",
    description=(
        "🍎 **Canadian Grocery Flyer Comparison API**\n\n"
        "Compare grocery prices across Canadian stores using real flyer data.\n\n"
        "**Features:**\n"
        "- 📍 Location-based store discovery\n"
        "- 🏪 Real-time flyer data from major Canadian grocery chains\n"
        "- 💰 Price comparison and savings calculations\n"
        "- 🔄 Weekly automated data refresh\n"
        "- 🗺️ Google Maps integration for directions\n\n"
        "**Data Sources:**\n"
        "- Google Places API (store locations)\n"
        "- Unofficial Flipp API (flyer data)\n"
        "- SQLite database (caching and performance)"
    ),
    version=settings.APP_VERSION,
    contact={
        "name": "FlyerFlutter Support",
        "email": "support@flyerflutter.ca",
    },
    license_info={
        "name": "MIT License",
        "url": "https://opensource.org/licenses/MIT",
    },
    lifespan=lifespan
)

# Configure CORS middleware
if settings.DEBUG:
    # Development: permissive CORS
    logger.info("🔧 Configuring CORS for development environment")
    cors_origins = [
        "http://localhost:3000",
        "http://localhost:5173",  # Vite dev server
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5173",
        "http://localhost:8080",  # Alternative dev port
        "http://127.0.0.1:8080"
    ]
else:
    # Production: restrictive CORS
    logger.info("🔒 Configuring CORS for production environment")
    cors_origins = settings.ALLOWED_ORIGINS

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=[
        "Accept",
        "Accept-Language", 
        "Content-Language",
        "Content-Type",
        "Authorization",
        "X-Requested-With",
        "Origin"
    ],
)

# Include API routes
app.include_router(router, prefix="/api")

# Health check endpoint (outside /api prefix)
@app.get("/health")
async def health_check():
    """Simple health check endpoint."""
    return {
        "status": "healthy",
        "application": "FlyerFlutter",
        "version": settings.APP_VERSION
    }

# Root endpoint - conditionally serve frontend or API
@app.get("/")
async def root():
    """
    Root endpoint - serve React frontend if available, otherwise API info.
    """
    # Check if frontend is built and available
    static_dir = Path(__file__).parent.parent / "frontend" / "dist"
    index_file = static_dir / "index.html"
    
    if index_file.exists():
        # Serve the React app
        return FileResponse(index_file)
    else:
        # Serve API welcome message
        return {
            "message": "🍎 Welcome to FlyerFlutter API!",
            "description": "Canadian Grocery Flyer Comparison Service",
            "version": settings.APP_VERSION,
            "docs": "/docs",
            "redoc": "/redoc",
            "health": "/health",
            "api_status": "/api/status"
        }


# Static file serving for frontend
def setup_static_files():
    """
    Setup static file serving for React frontend.
    
    Only mounts if frontend build directory exists.
    """
    static_dir = Path(__file__).parent.parent / "frontend" / "dist"
    
    if static_dir.exists() and static_dir.is_dir():
        logger.info(f"📁 Serving static files from: {static_dir}")
        
        # Serve static assets (JS, CSS, images) with StaticFiles
        app.mount("/assets", StaticFiles(directory=static_dir / "assets"), name="assets")
        
        # Also serve other static files from dist root (like manifest.json, favicon, etc.)
        app.mount("/static", StaticFiles(directory=static_dir), name="static")
        
        # Note: SPA catch-all routing is handled in the 404 error handler below
    else:
        logger.info("📁 Frontend build not found - serving API only")
        logger.info("💡 To serve frontend, run: cd frontend && npm run build")


# Setup static files on startup
setup_static_files()


# Error handlers
@app.exception_handler(404)
async def not_found_handler(request, exc):
    """Custom 404 handler - serve React SPA for non-API routes."""
    path = str(request.url.path)
    logger.info(f"🔍 404 handler called for path: {path}")
    
    # For API routes, return proper error
    if (path.startswith("/api/") or 
        path.startswith("/docs") or 
        path.startswith("/redoc") or 
        path.startswith("/assets/") or
        "/assets/" in path or
        path == "/health"):
        return {
            "error": "Not Found",
            "message": "The requested resource was not found",
            "path": path,
            "available_endpoints": {
                "api_docs": "/docs",
                "api_status": "/api/status",
                "health": "/health",
                "stores": "/api/stores",
                "deals": "/api/deals"
            }
        }
    
    # For non-API routes, try to serve React SPA
    static_dir = Path(__file__).parent.parent / "frontend" / "dist"
    index_file = static_dir / "index.html"
    
    if index_file.exists():
        return FileResponse(index_file)
    else:
        return {
            "error": "Not Found",
            "message": "Frontend not available",
            "path": path
        }


@app.exception_handler(500) 
async def internal_server_error_handler(request, exc):
    """Custom 500 handler."""
    logger.error(f"Internal server error: {exc}")
    return {
        "error": "Internal Server Error",
        "message": "An unexpected error occurred",
        "support": "Please contact support if this persists"
    }


if __name__ == "__main__":
    import uvicorn
    
    logger.info("🚀 Starting FlyerFlutter server directly")
    logger.info(f"🌐 Server will be available at: http://{settings.HOST}:{settings.PORT}")
    logger.info(f"📚 API Documentation: http://{settings.HOST}:{settings.PORT}/docs")
    
    
    uvicorn.run(
        "backend.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level="debug" if settings.DEBUG else "info",
        access_log=settings.DEBUG
    )