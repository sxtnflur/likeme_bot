from services.payment import PaymentService
from sqlalchemy.ext.asyncio import AsyncSession


class PaymentUseCase:
    def __init__(self, db: AsyncSession,
                 payments_service: PaymentService):
        self.db = db
        self.payment_service = payments_service

    async def on_payment(self, amount: float, metadata: dict) -> None:
        await self.payments_service.on_payment(
            metadata['package_id'], user_id=metadata['user_id'],
            amount=amount,
            db=self.db
        )
