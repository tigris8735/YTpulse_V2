# backend/routers/payments.py
from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional
from datetime import datetime, timezone, timedelta
import json

from database import get_db
from models import User, Payment
from auth import get_current_user
from services.yookassa_client import create_payment, get_payment_info

router = APIRouter()

# Цены и сроки подписок (в рублях и днях)
PLANS = {
    "1month": {"amount": 700, "days": 30, "label": "1 месяц"},
    "6months": {"amount": 1800, "days": 180, "label": "6 месяцев"},
    "1year": {"amount": 7000, "days": 365, "label": "1 год"},
}

class CreatePaymentRequest(BaseModel):
    term: str  # 1month, 6months, 1year

class CreatePaymentResponse(BaseModel):
    payment_id: str
    confirmation_url: str
    amount: int
    term: str

@router.post("/create", response_model=CreatePaymentResponse)
async def create_payment_endpoint(
    data: CreatePaymentRequest,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Создаёт платёж в ЮKassa для выбранного тарифа.
    Возвращает ссылку для перенаправления на оплату.
    """
    # 1. Проверяем, существует ли выбранный тариф
    plan = PLANS.get(data.term)
    if not plan:
        raise HTTPException(status_code=400, detail="Invalid term")

    # 2. Формируем описание и метаданные
    description = f"Подписка YT Pulse Pro: {plan['label']}"
    metadata = {
        "user_id": str(current_user.id),
        "term": data.term,
        "email": current_user.email,
    }

    # 3. Создаём платёж в ЮKassa
    try:
        # Формируем return_url (куда перенаправить пользователя после оплаты)
        # В продакшене это должен быть полный URL вашего фронтенда
        base_url = str(request.base_url).rstrip("/")
        return_url = f"{base_url}/api/payments/success?payment_id={{payment_id}}"
        
        payment_data = await create_payment(
            amount=plan["amount"],
            description=description,
            return_url=return_url,
            metadata=metadata,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Payment creation failed: {str(e)}")

    # 4. Сохраняем платёж в БД со статусом pending
    payment = Payment(
        user_id=current_user.id,
        yookassa_id=payment_data["id"],
        term=data.term,
        amount=plan["amount"],
        status="pending",
        created_at=datetime.now(timezone.utc),
    )
    db.add(payment)
    db.commit()

    # 5. Возвращаем данные для оплаты
    return CreatePaymentResponse(
        payment_id=payment_data["id"],
        confirmation_url=payment_data["confirmation"]["confirmation_url"],
        amount=plan["amount"],
        term=data.term,
    )


@router.post("/webhook")
async def yookassa_webhook(
    request: Request,
    db: Session = Depends(get_db),
):
    """
    Вебхук от ЮKassa для обработки статусов платежей.
    """
    # 1. Получаем сырой payload
    raw_payload = await request.json()
    
    # 2. Извлекаем данные о платеже
    event = raw_payload.get("event")
    payment_obj = raw_payload.get("object", {})
    payment_id = payment_obj.get("id")
    payment_status = payment_obj.get("status")
    metadata = payment_obj.get("metadata", {})
    amount = payment_obj.get("amount", {}).get("value")

    if not payment_id:
        return {"error": "Missing payment_id"}

    # 3. Находим платёж в нашей БД
    payment = db.query(Payment).filter(Payment.yookassa_id == payment_id).first()
    if not payment:
        return {"error": "Payment not found"}

    # 4. Сохраняем сырой вебхук в БД (для отладки)
    payment.raw_webhook = raw_payload

    # 5. Обрабатываем событие
    if event == "payment.succeeded" and payment_status == "succeeded":
        # Обновляем статус платежа
        payment.status = "succeeded"
        db.commit()

        # Обновляем пользователя — активируем Pro
        user = db.query(User).filter(User.id == payment.user_id).first()
        if user:
            # Определяем срок подписки
            term = payment.term
            plan = PLANS.get(term)
            if plan:
                # Добавляем дни к текущей дате (или от текущей, если ещё нет Pro)
                if user.pro_expires_at and user.pro_expires_at > datetime.now(timezone.utc):
                    # Если Pro уже активен, продлеваем
                    new_expires = user.pro_expires_at + timedelta(days=plan["days"])
                else:
                    # Если Pro не активен, начинаем с сегодня
                    new_expires = datetime.now(timezone.utc) + timedelta(days=plan["days"])
                
                user.plan = "pro"
                user.pro_expires_at = new_expires
                db.commit()

    elif event == "payment.canceled":
        payment.status = "canceled"
        db.commit()

    return {"status": "ok"}


@router.get("/success")
async def payment_success(
    payment_id: str,
    db: Session = Depends(get_db),
):
    """
    Эндпоинт для перенаправления после успешной оплаты.
    Проверяет статус платежа и возвращает результат.
    """
    # 1. Находим платёж в БД
    payment = db.query(Payment).filter(Payment.yookassa_id == payment_id).first()
    if not payment:
        return {"status": "error", "message": "Payment not found"}

    # 2. Если статус уже succeeded — возвращаем успех
    if payment.status == "succeeded":
        return {
            "status": "success",
            "message": "Payment successful! Your Pro subscription is active.",
        }

    # 3. Проверяем статус в ЮKassa (на всякий случай)
    try:
        payment_info = await get_payment_info(payment_id)
        if payment_info.get("status") == "succeeded":
            # Если платёж подтвердился, но вебхук ещё не пришёл — обновляем вручную
            payment.status = "succeeded"
            db.commit()
            return {
                "status": "success",
                "message": "Payment successful! Your Pro subscription is active.",
            }
    except Exception:
        pass

    # 4. Если платёж ещё в обработке
    return {
        "status": "pending",
        "message": "Payment is being processed. Please wait a moment.",
    }


@router.get("/history")
def get_payment_history(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Возвращает историю платежей текущего пользователя.
    """
    payments = db.query(Payment).filter(
        Payment.user_id == current_user.id
    ).order_by(Payment.created_at.desc()).all()

    return [
        {
            "id": p.id,
            "yookassa_id": p.yookassa_id,
            "term": p.term,
            "amount": p.amount,
            "status": p.status,
            "created_at": p.created_at.isoformat(),
        }
        for p in payments
    ]