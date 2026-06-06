import uuid
import time
import logging
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from app.config import config
from app.database import create_tables
from app.api.routes import router
from app.utils.logging import setup_logging, request_id_var

# Setup logging before anything else
setup_logging(config.log_level)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="Document API",
    version="1.0.0",
    description="Production-grade document storage API",
)

# Create database tables on startup
create_tables()


# Middleware: attach request_id to every request
@app.middleware("http")
async def attach_request_id(request: Request, call_next):
    request_id = str(uuid.uuid4())[:8]
    request_id_var.set(request_id)

    start = time.time()
    response = await call_next(request)
    latency_ms = round((time.time() - start) * 1000, 2)

    # Log every request
    logger.info(
        "http_request",
        extra={
            "extra_fields": {
                "method": request.method,
                "path": request.url.path,
                "status_code": response.status_code,
                "latency_ms": latency_ms,
            }
        },
    )

    # Add request_id to response headers for tracing
    response.headers["X-Request-ID"] = request_id
    return response


# Health check endpoint
@app.get("/health")
async def health():
    """Service health check."""
    return {"status": "healthy", "env": config.app_env, "version": "1.0.0"}


# Readiness probe
@app.get("/ready")
async def ready():
    """Check if service is ready to accept traffic."""
    try:
        from app.database import engine

        with engine.connect():
            pass
        return {"status": "ready"}
    except Exception as e:
        logger.error(
            "readiness_check_failed", extra={"extra_fields": {"error": str(e)}}
        )
        return JSONResponse(status_code=503, content={"status": "not ready"})


# Register routes
app.include_router(router)
