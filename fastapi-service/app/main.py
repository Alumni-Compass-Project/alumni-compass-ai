from contextlib import asynccontextmanager
import os

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from . import db as db_module
from .routers import cv_analyzer, recommend

load_dotenv()


@asynccontextmanager
async def lifespan(_: FastAPI):
    if db_module.check_connection():
        print("Database connection successful.")
    else:
        print(
            "Warning: DATABASE_URL not set or DB unreachable. "
            "Recommendations will use fallback mentor data."
        )
    yield


def _allowed_origins() -> list[str]:
    raw = os.getenv("ALLOWED_ORIGINS", "*")
    if raw.strip() == "*":
        return ["*"]
    return [origin.strip() for origin in raw.split(",") if origin.strip()]


app = FastAPI(
    title="Alumni Compass AI Service",
    description="خدمة الذكاء الاصطناعي لمنصة Alumni Compass - توصيات وتحليل سير ذاتية",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=_allowed_origins(),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(recommend.router, prefix="/v1")
app.include_router(cv_analyzer.router, prefix="/v1")


@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "Alumni Compass AI",
        "db_connected": db_module.check_connection(),
        "version": "1.0.0",
    }
