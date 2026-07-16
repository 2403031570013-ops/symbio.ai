import logging
import time
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import JSONResponse
from dotenv import load_dotenv

from app.api.v1.api import api_router
from app.core.config import settings
from app.core.middleware import CacheControlMiddleware, RateLimitMiddleware
from app.db.init_db import init_db

load_dotenv()

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s %(message)s")
logger = logging.getLogger("symbioai")


@asynccontextmanager
async def lifespan(app: FastAPI):
    settings.validate_production_secrets()
    init_db()
    logger.info("Application startup complete")
    yield
    logger.info("Application shutdown complete")


app = FastAPI(
    title="SymbioAI API",
    version="1.0.0",
    description="Production-ready FastAPI backend for the SymbioAI industrial symbiosis platform.",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(CacheControlMiddleware)
app.add_middleware(RateLimitMiddleware)
app.add_middleware(GZipMiddleware, minimum_size=1000)


@app.middleware("http")
async def logging_middleware(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    duration_ms = round((time.time() - start_time) * 1000, 2)
    logger.info("%s %s %s %.2fms", request.method, request.url.path, response.status_code, duration_ms)
    response.headers["X-Request-Id"] = str(int(time.time() * 1000))
    return response


@app.exception_handler(404)
async def not_found_handler(request: Request, exc):
    return JSONResponse(status_code=404, content={"success": False, "message": "Route not found", "errors": ["The requested endpoint does not exist"]})


@app.exception_handler(500)
async def server_error_handler(request: Request, exc):
    logger.exception("Unhandled error for %s", request.url.path)
    return JSONResponse(status_code=500, content={"success": False, "message": "Internal server error", "errors": ["Unexpected server error"]})


app.include_router(api_router, prefix="/api")


@app.get("/health")
def health() -> dict:
    return {"success": True, "message": "Service healthy", "data": {"status": "ok"}}


@app.get("/ready")
def ready() -> dict:
    return {"success": True, "message": "Service ready", "data": {"status": "ready"}}


@app.get("/metrics")
def metrics() -> dict:
    return {"success": True, "message": "Metrics available", "data": {"uptime_seconds": 0, "status": "ok"}}
