from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.middleware.trustedhost import TrustedHostMiddleware
from app.database import engine, Base
from app.api import endpoints, auth, data_ingestion, analytics
from app.api import websocket as ws
import os
from dotenv import load_dotenv

load_dotenv()

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="CrisisFlow API",
    description="Real-Time Disaster Intelligence Platform",
    version="1.0.0",
    docs_url="/api/docs" if os.getenv("ENVIRONMENT") != "production" else None,
    redoc_url="/api/redoc" if os.getenv("ENVIRONMENT") != "production" else None,
)

# Security Headers Middleware
class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Permissions-Policy"] = "geolocation=(), microphone=(), camera=()"
        return response

app.add_middleware(SecurityHeadersMiddleware)

# Rate limiting (optional, can be enabled in production)
# from app.middleware.rate_limit import RateLimitMiddleware
# app.add_middleware(RateLimitMiddleware, requests_per_minute=60)

# Trusted Host Middleware (for production)
if os.getenv("ENVIRONMENT") == "production":
    allowed_hosts = os.getenv("ALLOWED_HOSTS", "").split(",")
    if allowed_hosts:
        app.add_middleware(
            TrustedHostMiddleware,
            allowed_hosts=allowed_hosts
        )

# CORS middleware - secure configuration
allowed_origins = os.getenv("ALLOWED_ORIGINS", "http://localhost:3000").split(",")
allowed_origins = [origin.strip() for origin in allowed_origins if origin.strip()]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization", "X-Requested-With"],
    expose_headers=["Content-Type", "X-Total-Count"],
    max_age=3600,
)

# Include API routes
app.include_router(auth.router, prefix="/api/v1/auth", tags=["authentication"])
app.include_router(endpoints.router, prefix="/api/v1", tags=["reports"])
app.include_router(data_ingestion.router, prefix="/api/v1/ingest", tags=["data-ingestion"])
app.include_router(analytics.router, prefix="/api/v1/analytics", tags=["analytics"])
app.include_router(ws.router, prefix="/ws", tags=["websocket"])


@app.get("/")
async def health_check():
    """Health check endpoint"""
    return {"status": "CrisisFlow backend online"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)

