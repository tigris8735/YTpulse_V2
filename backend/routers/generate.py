# backend/routers/generate.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Dict, Any
from datetime import datetime, timezone
import uuid

from database import get_db
from models import User, GenerationJob
from services.ai_clients import generate_with_openrouter
from auth import get_current_user, require_pro

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

# ---------------------------------------------------------------------
# Вспомогательная функция для генерации вариантов через OpenRouter
# ---------------------------------------------------------------------
async def generate_preview_variants(
    trend_title: str,
    trend_description: str,
    num_variants: int = 3
) -> List[Dict[str, Any]]:
    """
    Генерирует num_variants промптов для превью с помощью OpenRouter,
    затем (в заглушке) создаёт ссылки на изображения.
    В реальном проекте здесь должен быть вызов сервиса генерации изображений.
    """
    system_prompt = (
        "You are an expert YouTube thumbnail designer. "
        "Generate creative, engaging, and clickable thumbnail concepts for a video about the given topic. "
        "Provide only the prompt text for image generation, nothing else. "
        "Each prompt should be on a new line, without numbering or extra text."
    )
    user_prompt = (
        f"Topic: {trend_title}\n"
        f"Description: {trend_description}\n"
        f"Generate {num_variants} different thumbnail concepts, each as a distinct prompt."
    )

    # 1. Получаем ответ от OpenRouter
    try:
        response = await generate_with_openrouter(
            prompt=user_prompt,
            system_prompt=system_prompt,
            temperature=0.8,
            max_tokens=500
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"OpenRouter error: {str(e)}")

    # 2. Парсим ответ – ожидаем список промптов по одному на строку
    prompts = [line.strip() for line in response.split('\n') if line.strip()]
    # Если получилось меньше num_variants, дублируем последний (или можно сгенерировать заново)
    while len(prompts) < num_variants:
        prompts.append(prompts[-1] if prompts else "default thumbnail prompt")
    prompts = prompts[:num_variants]

    # 3. Для каждого промпта генерируем изображение (заглушка)
    variants = []
    for i, prompt in enumerate(prompts, start=1):
        # ⚠️ Здесь должен быть реальный вызов генерации картинки
        # Например:
        #   image_url = await generate_image_from_prompt(prompt)
        # Пока используем заглушку – placeholder
        image_url = f"https://via.placeholder.com/1280x720?text={prompt[:30].replace(' ', '+')}"
        variants.append({
            "variant": i,
            "image_url": image_url,
            "prompt": prompt
        })

    return variants

# ---------------------------------------------------------------------
# Эндпоинт генерации (асинхронный)
# ---------------------------------------------------------------------
@router.post("/thumb", response_model=GenerateResponse)
async def generate_thumb(
    data: GenerateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # 1. Проверяем Pro-подписку
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
        # 3. Генерируем варианты (асинхронно)
        variants_data = await generate_preview_variants(
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
    if variants_response:
        job.file_url = variants_response[0].image_url  # сохраняем ссылку на первый вариант
    job.updated_at = datetime.now(timezone.utc)
    db.commit()

    return GenerateResponse(
        job_id=job.id,
        status=job.status,
        variants=variants_response
    )