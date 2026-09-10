# backend/routers/payments.py
from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.orm import Session
from pydantic import BaseModel
from datetime import datetime, timezone, timedelta
import uuid

from database import get_db
from models import User, Payment # Предполагаю, что у вас есть модель Payment
from auth import get_current_user
from services.yoomoney_client import create_payment_link, check_payment_status

router = APIRouter()

class PaymentRequest(BaseModel):
    term: str

class PaymentResponse(BaseModel):
    payment_url: str


@router.post("/create", response_model=PaymentResponse)
def create_payment(
    data: PaymentRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Определяем сумму и длительность в зависимости от срока
    if data.term == "month":
        amount = 500.0
        duration_days = 30
    elif data.term == "year":
        amount = 4500.0
        duration_days = 365
    else:
        raise HTTPException(status_code=400, detail="Invalid term. Use 'month' or 'year'.")

    # Генерируем уникальный label для этого платежа
    label = f"user_{current_user.id}_{uuid.uuid4().hex[:8]}"

    # Создаем ссылку на оплату
    try:
        payment_url = create_payment_link(
            amount=amount,
            label=label,
            description=f"Подписка YT Pulse Pro ({data.term}) для {current_user.email}"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"YooMoney error: {str(e)}")

    # Сохраняем информацию о платеже в БД
    payment = Payment(
        user_id=current_user.id,
        amount=int(amount),
        label=label,
        term=data.term,  # сохраняем срок
        status="pending",
        created_at=datetime.now(timezone.utc)
    )
    db.add(payment)
    db.commit()

    return PaymentResponse(payment_url=payment_url)

@router.get("/check")
def check_payment(
    label: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Проверяет статус платежа по его label.
    Этот эндпоинт можно вызывать с фронтенда после возврата пользователя с оплаты.
    """
    # Ищем платеж в БД
    payment = db.query(Payment).filter(Payment.label == label, Payment.user_id == current_user.id).first()
    if not payment:
        raise HTTPException(status_code=404, detail="Payment not found")

    # Если платеж уже подтвержден, просто возвращаем успех
    if payment.status == "success":
        return {"status": "success", "message": "Payment already confirmed"}

    # Проверяем статус через API ЮMoney
    try:
        is_success = check_payment_status(label)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to check payment status: {str(e)}")

    if is_success:
        # Обновляем статус платежа и активируем Pro-подписку пользователю
        payment.status = "success"
        # Здесь нужно обновить план пользователя
        user = db.query(User).filter(User.id == current_user.id).first()
        if user:
            user.plan = "pro"
            # Можно установить дату окончания подписки
            # user.pro_expires_at = datetime.now(timezone.utc) + timedelta(days=30)
        db.commit()
        return {"status": "success", "message": "Payment confirmed, Pro activated!"}
    else:
        return {"status": "pending", "message": "Payment not yet confirmed"}