# backend/services/youtube_client.py
import httpx
from typing import List, Dict, Any
from config import settings
import os 

YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY")
async def fetch_trends(region: str = "US", max_results: int = 50) -> List[Dict[str, Any]]:
    if not YOUTUBE_API_KEY:
        raise ValueError("YOUTUBE_API_KEY is not set")

    url = "https://www.googleapis.com/youtube/v3/videos"
    params = {
        "part": "snippet,contentDetails,statistics",
        "chart": "mostPopular",
        "regionCode": region,
        "maxResults": max_results,
        "key": YOUTUBE_API_KEY,
    }

    # Логируем URL и ключ (скрывая часть ключа для безопасности)
    masked_key = YOUTUBE_API_KEY[:4] + "..." + YOUTUBE_API_KEY[-4:]
    print(f"🔍 Requesting YouTube API: {url}?part={params['part']}&chart={params['chart']}&regionCode={params['regionCode']}&maxResults={params['maxResults']}&key={masked_key}")

    async with httpx.AsyncClient(timeout=10.0) as client:
        try:
            response = await client.get(url, params=params)
            response.raise_for_status()
            data = response.json()
        except Exception as e:
            print(f"YouTube API request failed: {e}")
            raise 
    videos = []
    for item in data.get("items", []):
        # Извлекаем длительность (ISO 8601 -> секунды)
        duration_str = item["contentDetails"]["duration"]
        duration_sec = parse_duration(duration_str)

        # Берём наилучшую доступную превьюшку
        thumbnails = item["snippet"]["thumbnails"]
        thumbnail_url = thumbnails.get("maxres", {}).get("url") or \
                        thumbnails.get("high", {}).get("url") or \
                        thumbnails.get("default", {}).get("url")

        video = {
            "video_id": item["id"],
            "title": item["snippet"]["title"],
            "channel_title": item["snippet"]["channelTitle"],
            "channel_id": item["snippet"]["channelId"],
            "views": item["statistics"].get("viewCount", "0"),
            "duration": duration_sec,
            "thumbnail": thumbnail_url,
            "category_id": item["snippet"]["categoryId"],
            "published_at": item["snippet"]["publishedAt"],
        }
        videos.append(video)
    return videos

def parse_duration(duration_str: str) -> int:
    """Конвертирует ISO 8601 длительность в секунды."""
    import re
    pattern = r"PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?"
    match = re.match(pattern, duration_str)
    if not match:
        return 0
    hours = int(match.group(1) or 0)
    minutes = int(match.group(2) or 0)
    seconds = int(match.group(3) or 0)
    return hours * 3600 + minutes * 60 + seconds
