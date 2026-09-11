# backend/services/yoomoney_client.py
import os
from yoomoney import Quickpay, Client
from typing import Optional, Dict, Any

YOOMONEY_TOKEN = os.getenv("YOOMONEY_TOKEN")
YOOMONEY_RECEIVER = os.getenv("YOOMONEY_RECEIVER")

def create_payment_link(
    amount: float,
    label: str,
    description: str = "Оплата подписки YT Pulse",
    payment_type: str = "SB" # SB - банковская карта, PC - кошелек ЮMoney
) -> str:
    """
    Генерирует ссылку на оплату через Quickpay форму ЮMoney.
    :param amount: Сумма платежа.
    :param label: Уникальный идентификатор платежа (например, ID пользователя).
    :param description: Описание платежа.
    :param payment_type: Способ оплаты.
    :return: URL для перенаправления пользователя на оплату.
    """
    if not YOOMONEY_RECEIVER:
        raise ValueError("YOOMONEY_RECEIVER is not set")

    quickpay = Quickpay(
        receiver=YOOMONEY_RECEIVER,
        quickpay_form="shop",
        targets=description,
        paymentType=payment_type,
        sum=amount,
        label=label
    )
    # В библиотеке yoomoney метод redirect_url возвращает готовую ссылку
    return quickpay.redirected_url

def check_payment_status(label: str) -> bool:
    """
    Проверяет, был ли успешный платеж с указанным label.
    :param label: Уникальный идентификатор платежа.
    :return: True, если платеж найден и успешен, иначе False.
    """
    if not YOOMONEY_TOKEN:
        raise ValueError("YOOMONEY_TOKEN is not set")

    client = Client(YOOMONEY_TOKEN)
    history = client.operation_history(label=label)

    for operation in history.operations:
        # Проверяем, что операция - это входящий перевод и он успешен
        if operation.status == "success" and operation.direction == "in":
            return True
    return False