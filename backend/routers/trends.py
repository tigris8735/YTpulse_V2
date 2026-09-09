# backend/routers/trends.py
from fastapi import APIRouter, Depends, HTTPException, Query, BackgroundTasks
from sqlalchemy.orm import Session
from sqlalchemy import desc
from datetime import datetime, timezone, timedelta
from typing import List, Dict, Any, Optional
import json

from database import get_db
from models import TrendsCache, PreviewTags
from services.youtube_client import fetch_trends
from services.analyzer_engine import analyze_preview

router = APIRouter()

# Время жизни кэша (в часах)
CACHE_TTL_HOURS = 1


def apply_filter(videos: List[Dict[str, Any]], filter_name: str) -> List[Dict[str, Any]]:
    """
    Применяет фильтр к списку видео.
    Возвращает отфильтрованный список.
    """
    if filter_name == "all":
        return videos

    GAMING_CATEGORY = "20"
    AI_KEYWORDS = ["ai", "artificial intelligence", "machine learning", "chatgpt", "openai", "gemini", "deep learning"]
    FINANCE_KEYWORDS = ["finance", "stock", "investing", "crypto", "bitcoin", "ethereum", "economy", "trading"]

    result = []
    for v in videos:
        title = v.get("title", "").lower()
        channel = v.get("channel_title", "").lower()
        category = v.get("category_id", "")

        if filter_name == "shorts":
            if v.get("duration", 0) <= 60:
                result.append(v)
        elif filter_name == "longform":
            if v.get("duration", 0) > 60:
                result.append(v)
        elif filter_name == "gaming":
            if category == GAMING_CATEGORY or "game" in title or "gaming" in title:
                result.append(v)
        elif filter_name == "ai":
            if category == "28" or any(kw in title for kw in AI_KEYWORDS) or any(kw in channel for kw in AI_KEYWORDS):
                result.append(v)
        elif filter_name == "finance":
            if any(kw in title for kw in FINANCE_KEYWORDS) or any(kw in channel for kw in FINANCE_KEYWORDS):
                result.append(v)
    return result


def enrich_with_preview_tags(videos: List[Dict[str, Any]], db: Session) -> List[Dict[str, Any]]:
    """
    Для каждого видео добавляет поля face_closeup, high_contrast, text_area, score_sum
    из таблицы preview_tags (если есть).
    """
    video_ids = [v["video_id"] for v in videos if v.get("video_id")]
    if not video_ids:
        return videos

    # Загружаем все теги для этих video_id одним запросом
    tags = db.query(PreviewTags).filter(PreviewTags.video_id.in_(video_ids)).all()
    tags_map = {t.video_id: t for t in tags}

    for v in videos:
        vid = v.get("video_id")
        if vid and vid in tags_map:
            t = tags_map[vid]
            v["face_closeup"] = t.face_closeup
            v["high_contrast"] = t.high_contrast
            v["text_area"] = t.text_area
            v["score_sum"] = t.score_sum
        else:
            # Если тегов нет, ставим значения по умолчанию
            v["face_closeup"] = False
            v["high_contrast"] = False
            v["text_area"] = False
            v["score_sum"] = 0
    return videos

def analyze_new_videos(video_ids: List[str], db: Session):
    """
    Запускает анализ превью для списка video_id, которых ещё нет в preview_tags.
    Сохраняет результаты в БД.
    """
    # Проверяем, какие video_id уже есть в БД
    existing = db.query(PreviewTags.video_id).filter(PreviewTags.video_id.in_(video_ids)).all()
    existing_ids = {e[0] for e in existing}
    new_ids = [vid for vid in video_ids if vid not in existing_ids]

    if not new_ids:
        return

    for vid in new_ids:
        try:
            result = analyze_preview(vid)
            # Сохраняем результат
            tag = PreviewTags(
                video_id=vid,
                face_closeup=result["face_closeup"],
                high_contrast=result["high_contrast"],
                text_area=result["text_area"],
                center_object=result["center_object"],
                score_sum=result["score_sum"],
            )
            db.add(tag)
        except Exception as e:
            # Логируем ошибку, но не прерываем обработку остальных
            print(f"Failed to analyze {vid}: {e}")
            continue
    db.commit()


@router.get("/")
@router.get("")
def get_trends(
    filter: str = Query("all", enum=["all", "shorts", "longform", "gaming", "ai", "finance"]),
    db: Session = Depends(get_db)
):
    """
    Возвращает список трендовых видео для региона US.
    Фильтры: all, shorts, longform, gaming, ai, finance.
    Использует кэш в БД (TTL = 1 час).
    """
    # 1. Ищем свежий кэш для фильтра "all" (основной кэш)
    cache_entry = db.query(TrendsCache).filter(
        TrendsCache.filter == "all",
        TrendsCache.region == "US"
    ).order_by(desc(TrendsCache.fetched_at)).first()

    # Если кэш есть и не протух, используем его
    if cache_entry:
        age = datetime.now(timezone.utc) - cache_entry.fetched_at
        if age.total_seconds() < CACHE_TTL_HOURS * 3600:
            videos = cache_entry.youtube_json  # список словарей
            # Обогащаем тегами
            enriched = enrich_with_preview_tags(videos, db)
            # Применяем фильтр
            filtered = apply_filter(enriched, filter)
            return {
                "filter": filter,
                "videos": filtered,
                "cached": True,
                "fetched_at": cache_entry.fetched_at.isoformat()
            }

    # 2. Кэш отсутствует или протух — загружаем свежие данные
    try:
        raw_videos = fetch_trends(region="US", max_results=50)
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"YouTube API error: {str(e)}")

    # 3. Сохраняем в кэш (под фильтром "all")
    new_cache = TrendsCache(
        filter="all",
        region="US",
        youtube_json=raw_videos,
        fetched_at=datetime.now(timezone.utc)
    )
    db.add(new_cache)
    db.commit()

    # 4. Запускаем анализ превью для новых видео (в фоне или синхронно)
    video_ids = [v["video_id"] for v in raw_videos if v.get("video_id")]
    analyze_new_videos(video_ids, db)  # синхронно, но можно обернуть в BackgroundTasks

    # 5. Обогащаем тегами и фильтруем
    enriched = enrich_with_preview_tags(raw_videos, db)
    filtered = apply_filter(enriched, filter)

    return {
        "filter": filter,
        "videos": filtered,
        "cached": False,
        "fetched_at": new_cache.fetched_at.isoformat()
    }


@router.post("/refresh")
def refresh_trends(
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """
    Принудительно обновляет кэш трендов и перезапускает анализ превью для всех видео.
    """
    # Удаляем старый кэш (можно просто пометить как устаревший, но для простоты удалим)
    db.query(TrendsCache).filter(TrendsCache.region == "US").delete()
    db.commit()

    # Загружаем свежие данные
    try:
        raw_videos = fetch_trends(region="US", max_results=50)
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"YouTube API error: {str(e)}")

    # Сохраняем новый кэш
    new_cache = TrendsCache(
        filter="all",
        region="US",
        youtube_json=raw_videos,
        fetched_at=datetime.now(timezone.utc)
    )
    db.add(new_cache)
    db.commit()

    # Запускаем анализ в фоне (чтобы не ждать)
    video_ids = [v["video_id"] for v in raw_videos if v.get("video_id")]
    background_tasks.add_task(analyze_new_videos, video_ids, db)

    return {
        "status": "success",
        "message": f"Cache refreshed, {len(video_ids)} videos fetched, analysis started in background.",
        "fetched_at": new_cache.fetched_at.isoformat()
    }