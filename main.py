from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi_limiter import FastAPILimiter
from fastapi_limiter.depends import RateLimiter
from redis.asyncio import Redis

from app.api import auth, notes
from config import settings

app = FastAPI(dependencies=[Depends(RateLimiter(times=100, seconds=60))])

origins = [
    "http://localhost",
    "http://localhost:8000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def on_startup():
    redis = Redis(host=settings.REDIS_HOST, port=settings.REDIS_PORT, decode_responses=True)
    await FastAPILimiter.init(redis)

app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(notes.router, prefix="/notes", tags=["notes"])