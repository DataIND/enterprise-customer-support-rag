"""FastAPI application entrypoint."""

from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.routes import chat, documents, health
from app.core.config import settings
from app.core.request_id import RequestIdMiddleware


@asynccontextmanager
async def lifespan(_app: FastAPI):
    """Application lifespan hooks."""
    yield


app = FastAPI(
    title=settings.APP_NAME,
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(RequestIdMiddleware)

app.include_router(health.router)
app.include_router(chat.router, prefix=f"{settings.API_PREFIX}/chat", tags=["chat"])
app.include_router(
    documents.router,
    prefix=f"{settings.API_PREFIX}/documents",
    tags=["documents"],
)
