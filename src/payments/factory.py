from datetime import datetime

import aiohttp
from typing_extensions import Literal
from .base import PaymentData, AbstractPaymentService
from .yookassa import YooKassaServiceABC
from .prodamus import ProdamusServiceABC

PaymentMethod = Literal['yookassa']


class PaymentFactory:
    payment_methods_objs: dict[PaymentMethod, YooKassaServiceABC]

    def __init__(
            self,
            yookassa: YooKassaServiceABC,
            # prodamus: ProdamusServiceABC
    ):
        self.yookassa = yookassa
        # self.prodamus = prodamus

        self.payment_methods_objs = {
            'yookassa': yookassa,
            # 'prodamus': prodamus
        }

    async def create_payment(self,
                             amount: int, description: str,
                             test: bool = False,
                             payment_method: PaymentMethod = 'yookassa',
                             metadata: dict | None = None,
                             expired_date: datetime | None = None,
                             session: aiohttp.ClientSession | None = None
                             ) -> PaymentData:
        return await self.payment_methods_objs[payment_method].create_payment(
            amount, description, test, expired_date=expired_date,
            session=session
        )

