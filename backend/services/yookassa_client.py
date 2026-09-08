# backend/services/yookassa_client.py
import httpx
import uuid
from typing import Dict, Any, Optional
from datetime import datetime, timezone
from ..config import settings

# Базовый URL для тестового режима ЮKassa
YOOKASSA_API_URL = "https://api.yookassa.ru/v3"
YOOKASSA_IDEMPOTENCE_KEY_HEADER = "Idempotence-Key"

def get_auth_headers() -> Dict[str, str]:
    """
    Возвращает заголовки для аутентификации в ЮKassa.
    Использует Basic Auth с shop_id и secret_key.
    """
    import base64
    auth_string = f"{settings.YOOKASSA_SHOP_ID}:{settings.YOOKASSA_SECRET_KEY}"
    encoded = base64.b64encode(auth_string.encode()).decode()
    return {
        "Authorization": f"Basic {encoded}",
        "Content-Type": "application/json",
    }

async def create_payment(
    amount: int,  # в рублях (целое число)
    description: str,
    return_url: str,
    metadata: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """
    Создаёт платёж в ЮKassa.
    
    Args:
        amount: Сумма в рублях (целое число, например, 700).
        description: Описание платежа (например, "Подписка Pro на 1 месяц").
        return_url: URL для перенаправления пользователя после оплаты.
        metadata: Дополнительные данные (например, user_id, term).
    
    Returns:
        Словарь с ответом от ЮKassa (включая id платежа, confirmation_url и т.д.).
    """
    url = f"{YOOKASSA_API_URL}/payments"
    
    # Генерируем уникальный ключ идемпотентности (для защиты от дублирования)
    idempotence_key = str(uuid.uuid4())
    
    headers = get_auth_headers()
    headers[YOOKASSA_IDEMPOTENCE_KEY_HEADER] = idempotence_key
    
    # Формируем тело запроса
    payload = {
        "amount": {
            "value": f"{amount:.2f}",  # ЮKassa принимает строку с двумя знаками после запятой
            "currency": "RUB",
        },
        "confirmation": {
            "type": "redirect",
            "return_url": return_url,
        },
        "description": description,
        "capture": True,  # Автоматически подтверждаем платёж
        "metadata": metadata or {},
    }
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.post(url, json=payload, headers=headers)
        response.raise_for_status()
        return response.json()


async def get_payment_info(payment_id: str) -> Dict[str, Any]:
    """
    Получает информацию о платеже по его ID.
    """
    url = f"{YOOKASSA_API_URL}/payments/{payment_id}"
    headers = get_auth_headers()
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.get(url, headers=headers)
        response.raise_for_status()
        return response.json()


async def process_webhook(payload: Dict[str, Any]) -> Dict[str, Any]:
    """
    Обрабатывает вебхук от ЮKassa.
    Возвращает словарь с данными о событии: 
        - event: 'payment.succeeded', 'payment.canceled', 'payment.waiting_for_capture' и др.
        - payment_id: ID платежа
        - payment_status: статус
        - metadata: метаданные из платежа
        - amount: сумма
    """
    event = payload.get("event")
    if not event:
        return {"error": "Missing event field"}
    
    # Извлекаем объект платежа
    payment_obj = payload.get("object", {})
    payment_id = payment_obj.get("id")
    payment_status = payment_obj.get("status")
    amount = payment_obj.get("amount", {}).get("value")
    metadata = payment_obj.get("metadata", {})
    
    return {
        "event": event,
        "payment_id": payment_id,
        "payment_status": payment_status,
        "amount": amount,
        "metadata": metadata,
        "raw_payload": payload,  # можно сохранить в БД для отладки
    }