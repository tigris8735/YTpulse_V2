# backend/services/ai_clients.py
import httpx
import json
from typing import Dict, Any, List, Optional
from tenacity import retry, stop_after_attempt, wait_exponential
from config import settings

# ============================================
# ТЕКСТОВЫЕ МОДЕЛИ (Groq / Gemini)
# ============================================

@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
async def generate_text_groq(prompt: str, max_tokens: int = 300) -> str:
    """
    Генерация текста через Groq API.
    """
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {settings.GROQ_API_KEY}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": "mixtral-8x7b-32768",
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": max_tokens,
        "temperature": 0.8,
    }
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.post(url, json=payload, headers=headers)
        response.raise_for_status()
        data = response.json()
        return data["choices"][0]["message"]["content"].strip()


@retry(stop=stop_after_attempt(2), wait=wait_exponential(multiplier=1, min=1, max=5))
async def generate_text_gemini(prompt: str, max_tokens: int = 300) -> str:
    """
    Генерация текста через Google Gemini API (fallback).
    """
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent?key={settings.GEMINI_API_KEY}"
    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {
            "maxOutputTokens": max_tokens,
            "temperature": 0.8,
        }
    }
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.post(url, json=payload)
        response.raise_for_status()
        data = response.json()
        return data["candidates"][0]["content"]["parts"][0]["text"].strip()


async def generate_text(prompt: str, max_tokens: int = 300) -> str:
    """
    Основная функция генерации текста.
    Сначала пробует Groq, при ошибке — Gemini.
    """
    try:
        return await generate_text_groq(prompt, max_tokens)
    except Exception as e:
        print(f"Groq failed: {e}, falling back to Gemini")
        try:
            return await generate_text_gemini(prompt, max_tokens)
        except Exception as e2:
            print(f"Gemini also failed: {e2}")
            raise Exception("All text generation providers failed")


# ============================================
# ИЗОБРАЖЕНИЯ (Pollinations / Gemini Flash Image)
# ============================================

@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
async def generate_image_pollinations(prompt: str) -> str:
    """
    Генерация изображения через Pollinations.ai.
    Возвращает URL готового изображения.
    """
    # Pollinations бесплатный, не требует ключа
    url = f"https://image.pollinations.ai/prompt/{prompt}?width=1280&height=720&nologo=true"
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.get(url)
        response.raise_for_status()
        # Pollinations возвращает изображение, но нам нужен URL для скачивания
        # Возвращаем сгенерированный URL (он же и есть запрос)
        return url


@retry(stop=stop_after_attempt(2), wait=wait_exponential(multiplier=1, min=1, max=5))
async def generate_image_gemini(prompt: str) -> str:
    """
    Генерация изображения через Gemini Flash Image (экспериментальный).
    Возвращает URL изображения (или сохраняет и возвращает путь).
    """
    # Gemini Flash Image пока в бета-доступе, используем Imagen через Vertex AI или другой endpoint
    # Для прототипа используем заглушку — возвращаем заглушку-изображение
    # В реальном проекте здесь будет вызов к Gemini Image API
    fallback_url = "https://via.placeholder.com/1280x720/1a1a2e/ffffff?text=YT+Pulse+Preview"
    return fallback_url


async def generate_image(prompt: str) -> str:
    """
    Основная функция генерации изображения.
    Сначала пробует Pollinations, при ошибке — Gemini (или заглушка).
    """
    try:
        return await generate_image_pollinations(prompt)
    except Exception as e:
        print(f"Pollinations failed: {e}, falling back to Gemini")
        try:
            return await generate_image_gemini(prompt)
        except Exception as e2:
            print(f"Gemini also failed: {e2}")
            # Возвращаем заглушку
            return "https://via.placeholder.com/1280x720/1a1a2e/ffffff?text=YT+Pulse+Preview"


# ============================================
# ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ ДЛЯ ГЕНЕРАЦИИ ПРЕВЬЮ
# ============================================

async def generate_preview_prompt(trend_title: str, trend_description: str = "") -> str:
    """
    Генерирует промпт для превью на основе данных о тренде.
    """
    base_prompt = f"""
    Create a YouTube thumbnail for a video about: "{trend_title}"
    
    The thumbnail should be:
    - Bright and eye-catching
    - Have a clear focal point
    - Use bold colors (preferably red, yellow, or white text on dark background)
    - Include the main topic or a surprising element
    - Look clickable and professional
    
    Style: YouTube standard thumbnail, 16:9 aspect ratio, high contrast.
    """
    return base_prompt


async def generate_preview_variants(trend_title: str, trend_description: str = "", num_variants: int = 3) -> List[Dict[str, str]]:
    """
    Генерирует 3 варианта превью.
    Возвращает список словарей: [{"prompt": "...", "image_url": "..."}, ...]
    """
    # 1. Генерируем промпт для текста
    base_prompt = await generate_preview_prompt(trend_title, trend_description)
    
    variants = []
    for i in range(num_variants):
        # Генерируем немного отличающиеся промпты для каждого варианта
        variation_prompt = f"{base_prompt}\n\nVariant {i+1}: Try a different angle or composition."
        
        # Генерируем текст (пока не используем в прототипе, но задел)
        # text = await generate_text(base_prompt, max_tokens=100)
        
        # Генерируем изображение
        image_url = await generate_image(base_prompt.replace('\n', ' '))
        
        variants.append({
            "prompt": base_prompt,
            "image_url": image_url,
            "variant": i + 1
        })
    
    return variants