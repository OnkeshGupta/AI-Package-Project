from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes.upload import router as upload_router
from fastapi.responses import JSONResponse
from app.core.exceptions import AppException
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(title="AI Hiring MVP - Day 1")

@app.exception_handler(AppException)
async def app_exception_handler(request, exc: AppException):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.detail,
            "status_code": exc.status_code
        }
    )

# allow all origins for testing
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# include API routes
app.include_router(upload_router, prefix="/api")