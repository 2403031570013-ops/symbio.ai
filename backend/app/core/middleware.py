from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
import time

from starlette.responses import JSONResponse

from app.core.config import settings


class RateLimitMiddleware(BaseHTTPMiddleware):
    def __init__(self, app):
        super().__init__(app)
        self.requests = {}

    async def dispatch(self, request: Request, call_next):
        if request.url.path in {"/health", "/ready"}:
            return await call_next(request)

        now = time.time()
        window_start = now - 60
        client = request.client.host if request.client else "unknown"
        bucket = [ts for ts in self.requests.get(client, []) if ts >= window_start]
        if len(bucket) >= settings.RATE_LIMIT_PER_MINUTE:
            return JSONResponse(status_code=429, content={"success": False, "message": "Too many requests", "errors": ["Rate limit exceeded"]})
        bucket.append(now)
        self.requests[client] = bucket
        return await call_next(request)


class CacheControlMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        if request.url.path.startswith("/api"):
            response.headers["Cache-Control"] = "no-store"
        else:
            response.headers["Cache-Control"] = "public, max-age=300"
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Permissions-Policy"] = "camera=(), microphone=(), geolocation=()"
        response.headers["Content-Security-Policy"] = "default-src 'self'; img-src 'self' data: https:; connect-src 'self' http: https: ws: wss:; style-src 'self' 'unsafe-inline'; script-src 'self' 'unsafe-inline' https://accounts.google.com; frame-src https://accounts.google.com"
        return response
