from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from database import engine
from models import Base
from routers import auth, trends, preview, generate, jobs, payments

Base.metadata.create_all(bind=engine)

app = FastAPI(title="YT Pulse API", version="1.0")

origins = [
    "https://ytpulse-v2-1.onrender.com",  # URL вашего фронта
    "http://localhost:5173",              # для локальной разработки (опционально)
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization"],
)

app.include_router(auth.router, prefix="/api/auth", tags=["Auth"])
app.include_router(trends.router, prefix="/api/trends", tags=["Trends"])
app.include_router(preview.router, prefix="/api/preview", tags=["Preview"])
app.include_router(generate.router, prefix="/api/generate", tags=["Generate"])
app.include_router(jobs.router, prefix="/api/jobs", tags=["Jobs"])
app.include_router(payments.router, prefix="/api/payments", tags=["Payments"])

@app.get("/")
def root():
    return {"status": "YT Pulse API is running"}

@app.get("/health")
def health():
    return {"status": "ok"}