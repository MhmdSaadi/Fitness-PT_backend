from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import redis.asyncio as redis

from src.core.config import settings
from src.core.database import init_db
from src.domains.auth.routes import auth_router
from src.domains.coaching.routes import coaching_router

# Global Redis connection
redis_client = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    global redis_client
    redis_client = redis.from_url(settings.REDIS_URL, decode_responses=True)
    await init_db()
    yield
    # Shutdown
    if redis_client:
        await redis_client.close()

app = FastAPI(
    title="HBT FootFit API",
    description="Professional Foot Fitness Coach API",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth_router, prefix="/api/v1/auth", tags=["Authentication"])
app.include_router(coaching_router, prefix="/api/v1/coaching", tags=["Coaching"])

@app.get("/")
async def root():
    return {"message": "HBT FootFit API is running!"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}