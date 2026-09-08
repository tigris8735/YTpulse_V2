# backend/routers/preview.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Dict, Any
from ..database import get_db
from ..models import PreviewTags
from ..services.analyzer_engine import analyze_preview

router = APIRouter()

@router.get("/{video_id}")
def get_preview_tags(video_id: str, db: Session = Depends(get_db)) -> Dict[str, Any]:
    """
    Возвращает теги кликабельности для указанного video_id.
    Если теги уже есть в БД — возвращает их.
    Если нет — запускает локальный анализ, сохраняет результат и возвращает его.
    """
    # 1. Проверяем, есть ли запись в таблице preview_tags
    existing = db.query(PreviewTags).filter(PreviewTags.video_id == video_id).first()
    if existing:
        return {
            "video_id": video_id,
            "face_closeup": existing.face_closeup,
            "high_contrast": existing.high_contrast,
            "text_area": existing.text_area,
            "center_object": existing.center_object,
            "score_sum": existing.score_sum,
            "cached": True,
        }

    # 2. Нет в БД — запускаем анализ
    try:
        result = analyze_preview(video_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

    # 3. Сохраняем результат в БД
    new_tags = PreviewTags(
        video_id=video_id,
        face_closeup=result["face_closeup"],
        high_contrast=result["high_contrast"],
        text_area=result["text_area"],
        center_object=result["center_object"],
        score_sum=result["score_sum"],
    )
    db.add(new_tags)
    db.commit()
    db.refresh(new_tags)

    # 4. Возвращаем результат (убираем лишние поля, если нужно)
    return {
        "video_id": video_id,
        "face_closeup": new_tags.face_closeup,
        "high_contrast": new_tags.high_contrast,
        "text_area": new_tags.text_area,
        "center_object": new_tags.center_object,
        "score_sum": new_tags.score_sum,
        "cached": False,
    }