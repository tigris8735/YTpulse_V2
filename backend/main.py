from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from database import engine
from models import Base
from routers import auth, trends, preview, generate, jobs, payments



app = FastAPI(title="YT Pulse API", version="1.0", redirect_slashes=False)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://ytpulse-v2-1.onrender.com"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization"],
)

app.include_router(auth.router, prefix="/auth", tags=["Auth"])
app.include_router(trends.router, prefix="/trends", tags=["Trends"])
app.include_router(preview.router, prefix="/preview", tags=["Preview"])
app.include_router(generate.router, prefix="/generate", tags=["Generate"])
app.include_router(jobs.router, prefix="/jobs", tags=["Jobs"])
app.include_router(payments.router, prefix="/payments", tags=["Payments"])

Base.metadata.create_all(bind=engine)

@app.get("/")
def root():
    return {"status": "YT Pulse API is running"}

@app.get("/health")
def health():
    return {"status": "ok"}