from services.payment import PaymentService
from sqlalchemy.ext.asyncio import AsyncSession


class PaymentUseCase:
    def __init__(self, db: AsyncSession,
                 payments_service: PaymentService):
        self.db = db
        self.payment_service = payments_service

    async def on_payment(self, amount: float, metadata: dict) -> None:
        match metadata['type']:
            case 'package':
                await self.payment_service.on_payment_package(
                    int(metadata['package_id']),
                    user_id=int(metadata['user_id']),
                    amount=amount,
                    db=self.db
                )

            case 'model':
                await self.payment_service.on_payment_model(
                    user_id=int(metadata['user_id']),
                    avatar_id=int(metadata['avatar_id']),
                    amount=amount,
                    db=self.db
                )
            case _:
                return