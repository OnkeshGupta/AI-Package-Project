from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes.upload import router as upload_router
from app.core.exceptions import AppException
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager

from app.db.database import engine
from app.db.base import Base
import app.models  # IMPORTANT: loads models

@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    print("✅ Database tables ensured")
    yield
    print("🛑 Application shutting down")

app = FastAPI(
    title="TalentLens AI",
    lifespan=lifespan
)

@app.exception_handler(AppException)
async def app_exception_handler(request, exc: AppException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": exc.detail}
    )

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(upload_router, prefix="/api")