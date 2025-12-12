from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes.upload import router as upload_router
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(title="AI Hiring MVP - Day 1")

# allow all origins for testing
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# include API routes
app.include_router(upload_router, prefix="/api")