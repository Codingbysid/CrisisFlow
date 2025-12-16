from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database import engine, Base
from app.api import endpoints, auth, data_ingestion, analytics
from app.api import websocket as ws

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="CrisisFlow API",
    description="Real-Time Disaster Intelligence Platform",
    version="1.0.0"
)

# CORS middleware for frontend communication
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Next.js default port
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
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

