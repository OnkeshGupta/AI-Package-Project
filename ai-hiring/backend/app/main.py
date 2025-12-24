from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager

from app.routes.upload import router as upload_router
from app.auth.auth_router import router as auth_router
from app.core.exceptions import AppException
from app.db.database import engine
from app.db.base import Base
import app.models  # IMPORTANT: load models

# -----------------------------
# Lifespan (startup / shutdown)
# -----------------------------
@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    print("✅ Database tables ensured")
    yield
    print("🛑 Application shutting down")

# -----------------------------
# Create FastAPI app FIRST
# -----------------------------
app = FastAPI(
    title="TalentLens AI",
    lifespan=lifespan
)

# -----------------------------
# Exception handling
# -----------------------------
@app.exception_handler(AppException)
async def app_exception_handler(request, exc: AppException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": exc.detail}
    )

# -----------------------------
# Middleware
# -----------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# -----------------------------
# Routers (AFTER app creation)
# -----------------------------
app.include_router(auth_router, prefix="/auth", tags=["Auth"])
app.include_router(upload_router, prefix="/api", tags=["Resume"])

# -----------------------------
# Health check
# -----------------------------
@app.get("/")
def root():
    return {"status": "TalentLens backend running"}