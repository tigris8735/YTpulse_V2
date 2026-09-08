# backend/routers/generate.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Dict, Any
from datetime import datetime, timezone
import uuid

from ..database import get_db
from ..models import User, GenerationJob
from ..services.ai_clients import generate_preview_variants
from ..auth import get_current_user, require_pro  # эти функции будут добавлены в auth.py

router = APIRouter()

# Модели запроса/ответа
class GenerateRequest(BaseModel):
    trend_title: str
    trend_description: str = ""

class VariantResponse(BaseModel):
    variant: int
    image_url: str
    prompt: str

class GenerateResponse(BaseModel):
    job_id: int
    status: str
    variants: List[VariantResponse]

@router.post("/thumb", response_model=GenerateResponse)
def generate_thumb(
    data: GenerateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)  # проверяем авторизацию
):
    """
    Генерация 3 вариантов превью для указанного тренда.
    Доступно только пользователям с планом Pro.
    """
    # 1. Проверяем план Pro
    if not require_pro(current_user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Pro subscription required. Please upgrade your plan."
        )

    # 2. Создаём задачу в БД (status = rendering)
    job = GenerationJob(
        user_id=current_user.id,
        type="thumb",
        status="rendering",
        prompt_text=data.trend_title,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )
    db.add(job)
    db.commit()
    db.refresh(job)

    try:
        # 3. Запускаем генерацию 3 вариантов
        variants_data = generate_preview_variants(
            trend_title=data.trend_title,
            trend_description=data.trend_description,
            num_variants=3
        )
    except Exception as e:
        # В случае ошибки обновляем задачу
        job.status = "error"
        job.error = str(e)
        job.updated_at = datetime.now(timezone.utc)
        db.commit()
        raise HTTPException(status_code=500, detail=f"Generation failed: {str(e)}")

    # 4. Формируем ответ
    variants_response = []
    for v in variants_data:
        variants_response.append(
            VariantResponse(
                variant=v["variant"],
                image_url=v["image_url"],
                prompt=v["prompt"]
            )
        )

    # 5. Обновляем задачу (статус ready)
    job.status = "ready"
    job.file_url = variants_response[0].image_url  # сохраняем ссылку на первый вариант как основной
    job.updated_at = datetime.now(timezone.utc)
    db.commit()

    return GenerateResponse(
        job_id=job.id,
        status=job.status,
        variants=variants_response
    )