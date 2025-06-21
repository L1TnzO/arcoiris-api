"""Main FastAPI application module."""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

from app.core.config import get_settings
from app.core.database import create_tables
from app.core.security import get_password_hash
from app.models.admin import Admin
from app.api.v1 import products, admin
from app.core.database import SessionLocal

# Get settings
settings = get_settings()

# Setup logging
logging.basicConfig(
    level=logging.INFO if not settings.debug else logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Setup rate limiter
limiter = Limiter(key_func=get_remote_address)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan events for the application."""
    # Startup
    logger.info("Starting up Furniture API")
    
    # Create database tables
    create_tables()
    
    # Create default admin user if not exists
    await create_default_admin()
    
    logger.info("Furniture API started successfully")
    
    yield
    
    # Shutdown
    logger.info("Shutting down Furniture API")


async def create_default_admin():
    """Create default admin user if it doesn't exist."""
    db = SessionLocal()
    try:
        # Check if any admin exists
        existing_admin = db.query(Admin).first()
        if not existing_admin:
            # Create default admin
            admin = Admin(
                username=settings.admin_username,
                email=settings.admin_email,
                hashed_password=get_password_hash(settings.admin_password),
                is_active=True
            )
            db.add(admin)
            db.commit()
            logger.info(f"Created default admin user: {settings.admin_username}")
    except Exception as e:
        logger.error(f"Error creating default admin: {e}")
        db.rollback()
    finally:
        db.close()


# Create FastAPI application
app = FastAPI(
    title=settings.project_name,
    version=settings.version,
    description="A complete, production-ready FastAPI backend system for product management",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# Add rate limiting
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"] if settings.debug else settings.backend_cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler for unhandled errors."""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    
    return JSONResponse(
        status_code=500,
        content={
            "error": "internal_server_error",
            "message": "An internal server error occurred",
            "detail": str(exc) if settings.debug else "Internal server error"
        }
    )


# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": settings.project_name,
        "version": settings.version
    }


# Root endpoint
@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "message": "Welcome to Furniture Product Management API",
        "version": settings.version,
        "docs": "/docs",
        "health": "/health"
    }


# Include API routers
app.include_router(
    products.router,
    prefix=f"{settings.api_v1_prefix}/products",
    tags=["products"]
)

app.include_router(
    admin.router,
    prefix=f"{settings.api_v1_prefix}/admin",
    tags=["admin"]
)


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.debug,
        log_level="info"
    )
