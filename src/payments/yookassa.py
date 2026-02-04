from yookassa import Configuration, Payment
import json
import abc

from yookassa.domain.response import PaymentResponse
from .base import AbstractPaymentService, PaymentData
from config import settings

class YooKassaServiceABC(AbstractPaymentService):
    @abc.abstractmethod
    def __init__(
            self,
            shop_id: str = settings.YOOKASSA_SHOP_ID,
            api_token: str = settings.YOOKASSA_API_KEY
    ):
        ...


class YooKassaService(YooKassaServiceABC):
    def __init__(
            self,
            shop_id: str = settings.YOOKASSA_SHOP_ID,
            api_token: str = settings.YOOKASSA_API_KEY
    ):
        Configuration.account_id = shop_id
        Configuration.secret_key = api_token

    async def create_payment(self, amount: int, description: str, test: bool = False,
                             metadata: dict | None = None, **kwargs) -> PaymentData:
        metadata = metadata or {}
        data = {
            "amount": {
                "value": amount,
                "currency": "RUB"
            },
            "capture": True,
            "confirmation": {
                "type": "redirect",
                "return_url": settings.BOT_URL
            },
            "description": description,
            "metadata": metadata,
            "receipt": {
                "customer": {
                    "full_name": "Иванов Иван Иванович",
                    "phone": "79000000000"
                },
                "items": [
                    {
                        "description": description,
                        "quantity": "1.00",
                        "amount": {
                            "value": amount,
                            "currency": "RUB"
                        },
                        "vat_code": "2",
                        "payment_mode": "full_prepayment",
                        "payment_subject": "commodity"
                    }
                ]
            },
            "test": test
        }

        payment = await Payment.create(data)
        return PaymentData(
            id=payment.id,
            url=payment.confirmation.confirmation_url
        )