from fastapi import FastAPI, HTTPException, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import redis.asyncio as redis
import httpx
import logging
import time
from .routers import auth
from .core.config import settings
from .core.database import init_db
# from .middleware.request_id import RequestIDMiddleware
# from .middleware.logging import LoggingMiddleware

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan management"""
    # Startup
    logger.info("🚀 Starting PPT Generator API Gateway...")
    
    # Initialize database
    await init_db()
    logger.info("✅ Database initialized")
    
    # Initialize Redis connection
    app.redis = redis.from_url(settings.redis_url, decode_responses=True)
    try:
        await app.redis.ping()
        logger.info("✅ Redis connection established")
    except Exception as e:
        logger.error(f"❌ Redis connection failed: {e}")
        raise
    
    # Initialize HTTP client for service communication
    app.http_client = httpx.AsyncClient(
        timeout=httpx.Timeout(30.0),
        limits=httpx.Limits(max_keepalive_connections=20, max_connections=100)
    )
    logger.info("✅ HTTP client initialized")
    
    # Initialize service registry
    services = {
        "document_processor": settings.document_processor_url,
        "ai_generator": settings.ai_generator_url,
        "presentation_renderer": settings.presentation_renderer_url
    }
    app.services = services
    logger.info(f"✅ Service registry: {list(services.keys())}")
    
    yield
    
    # Shutdown
    logger.info("🔄 Shutting down API Gateway...")
    await app.redis.close()
    await app.http_client.aclose()
    logger.info("✅ Cleanup completed")

# Create FastAPI application
app = FastAPI(
    title="PPT Generator API Gateway",
    description="Central gateway for PPT generation microservices",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add middleware
# app.add_middleware(RequestIDMiddleware)
# app.add_middleware(LoggingMiddleware)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["X-Request-ID"]
)

# Include routers
app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
# app.include_router(presentations.router, prefix="/api/presentations", tags=["Presentations"])
# app.include_router(tasks.router, prefix="/api/tasks", tags=["Task Management"])
# app.include_router(upload.router, prefix="/api/upload", tags=["File Upload"])

# Health check endpoints
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "API Gateway",
        "version": "1.0.0",
        "timestamp": time.time()
    }

@app.get("/health/detailed")
async def detailed_health_check(request: Request):
    """Detailed health check with dependencies"""
    health_status = {
        "service": "API Gateway",
        "status": "healthy",
        "timestamp": time.time(),
        "dependencies": {}
    }
    
    # Check Redis
    try:
        await request.app.redis.ping()
        health_status["dependencies"]["redis"] = "healthy"
    except Exception as e:
        health_status["dependencies"]["redis"] = f"unhealthy: {str(e)}"
        health_status["status"] = "degraded"
    
    # Check downstream services
    for service_name, service_url in request.app.services.items():
        try:
            response = await request.app.http_client.get(f"{service_url}/health", timeout=5.0)
            if response.status_code == 200:
                health_status["dependencies"][service_name] = "healthy"
            else:
                health_status["dependencies"][service_name] = f"unhealthy: HTTP {response.status_code}"
                health_status["status"] = "degraded"
        except Exception as e:
            health_status["dependencies"][service_name] = f"unhealthy: {str(e)}"
            health_status["status"] = "degraded"
    
    return health_status

@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "message": "PPT Generator API Gateway",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health",
        "services": {
            "authentication": "/api/auth",
            # "presentations": "/api/presentations", 
            # "tasks": "/api/tasks",
            # "upload": "/api/upload"
        }
    }

# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Global exception: {exc}")
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal Server Error",
            "message": "An unexpected error occurred",
            "request_id": getattr(request.state, "request_id", None)
        }
    )