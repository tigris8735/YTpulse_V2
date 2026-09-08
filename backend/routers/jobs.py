# backend/routers/jobs.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import desc
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime, timezone

from database import get_db
from models import User, GenerationJob
from auth import get_current_user, require_pro

router = APIRouter()

# Модели запроса/ответа
class CreateJobRequest(BaseModel):
    type: str = "video"  # пока только video, но можно расширить
    prompt_text: Optional[str] = None

class JobResponse(BaseModel):
    id: int
    type: str
    status: str  # queued, rendering, ready, error
    prompt_text: Optional[str]
    file_url: Optional[str]
    error: Optional[str]
    created_at: datetime
    updated_at: datetime

class CreateJobResponse(BaseModel):
    job_id: int
    status: str
    message: str


@router.post("/", response_model=CreateJobResponse)
def create_job(
    data: CreateJobRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Создаёт задачу на генерацию ролика (видео).
    Доступно только пользователям с планом Pro.
    """
    # 1. Проверяем Pro
    if not require_pro(current_user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Pro subscription required. Please upgrade your plan."
        )

    # 2. Создаём задачу в БД (status = queued)
    job = GenerationJob(
        user_id=current_user.id,
        type=data.type,
        status="queued",
        prompt_text=data.prompt_text or f"Video generation for user {current_user.email}",
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )
    db.add(job)
    db.commit()
    db.refresh(job)

    # 3. В реальном проекте здесь бы запускалась фоновая задача (Celery/RQ)
    # Для прототипа просто имитируем обработку (переводим в ready через пару секунд)
    # Но мы сделаем синхронно: сразу переводим в rendering и затем в ready
    # Это имитация, чтобы пользователь видел изменение статуса
    
    # Имитация обработки (в реальном проекте это делается в фоне)
    try:
        # Обновляем статус на rendering
        job.status = "rendering"
        job.updated_at = datetime.now(timezone.utc)
        db.commit()
        
        # Имитация генерации видео (заглушка)
        # В реальном проекте здесь был бы вызов внешнего API для генерации видео
        # или FFmpeg-склейка клипов
        job.status = "ready"
        job.file_url = "https://storage.yandexcloud.net/yt-pulse/sample-video.mp4"  # заглушка
        # Или локальный файл: /static/sample-video.mp4
        job.updated_at = datetime.now(timezone.utc)
        db.commit()
    except Exception as e:
        job.status = "error"
        job.error = str(e)
        job.updated_at = datetime.now(timezone.utc)
        db.commit()
        raise HTTPException(status_code=500, detail=f"Job processing failed: {str(e)}")

    return CreateJobResponse(
        job_id=job.id,
        status=job.status,
        message="Job created and processed successfully"
    )


@router.get("/{job_id}", response_model=JobResponse)
def get_job_status(
    job_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Возвращает статус конкретной задачи.
    """
    job = db.query(GenerationJob).filter(GenerationJob.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    # Проверяем, что задача принадлежит текущему пользователю
    if job.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied to this job")
    
    return JobResponse(
        id=job.id,
        type=job.type,
        status=job.status,
        prompt_text=job.prompt_text,
        file_url=job.file_url,
        error=job.error,
        created_at=job.created_at,
        updated_at=job.updated_at
    )


@router.get("/", response_model=List[JobResponse])
def list_user_jobs(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    limit: int = 20,
    offset: int = 0
):
    """
    Возвращает список всех задач текущего пользователя.
    """
    jobs = db.query(GenerationJob).filter(
        GenerationJob.user_id == current_user.id
    ).order_by(desc(GenerationJob.created_at)).offset(offset).limit(limit).all()
    
    return [
        JobResponse(
            id=job.id,
            type=job.type,
            status=job.status,
            prompt_text=job.prompt_text,
            file_url=job.file_url,
            error=job.error,
            created_at=job.created_at,
            updated_at=job.updated_at
        ) for job in jobs
    ]