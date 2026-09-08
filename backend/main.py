# backend/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
# Импортируем наши модули
from .database import engine  # <-- добавили
from .models import Base      # <-- добавили
from .routers import auth, trends, preview, generate, jobs , payments
# Создаём таблицы, если их нет (при старте сервера)
Base.metadata.create_all(bind=engine)

app = FastAPI(title="YT Pulse API", version="1.0")

# Настройка CORS (разрешаем все домены для разработки)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory="static"), name="static")

# Подключаем роутеры
app.include_router(auth.router, prefix="/api/auth", tags=["Auth"])
app.include_router(trends.router, prefix="/api/trends", tags=["Trends"])  # <-- добавили
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