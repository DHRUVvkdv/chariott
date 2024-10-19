from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse
from core.config import settings

API_KEY = settings.API_KEY


class AuthMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        if request.url.path in [
            "/docs",
            "/openapi.json",
        ]:  # Skip authentication for Swagger docs
            return await call_next(request)
        api_key = request.headers.get("API-Key")
        if api_key != API_KEY:
            return JSONResponse(
                status_code=403, content={"detail": "Could not validate credentials"}
            )
        return await call_next(request)
