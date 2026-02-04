from database import OrdersRepo
from log import logger
from services.payment import PaymentService
from sqlalchemy.ext.asyncio import AsyncSession


class PaymentUseCase:
    def __init__(self, db: AsyncSession,
                 payments_service: PaymentService):
        self.db = db
        self.payment_service = payments_service

    async def on_payment(self, amount: float, metadata: dict) -> None:
        order_id = metadata.get('order_id')
        user_id = metadata.get('user_id')

        if (not order_id) or (not user_id):
            logger.error(f'У платежа нет order_id/user_id в мета-данных. order_id: {order_id}, user_id: {user_id}')
            return

        user_id = int(user_id)

        try:
            if not await OrdersRepo(self.db).exists(
                id=order_id,
                user_id=user_id
            ):
                logger.error(f'Ордера с такими order_id и user_id не существует. order_id: {order_id}, user_id: {user_id}')
                return
        except:
            logger.error(f'Ордера с такими order_id и user_id не существует. order_id: {order_id}, user_id: {user_id}')
            return

        match metadata['type']:
            case 'package':
                await self.payment_service.on_payment_package(
                    int(metadata['package_id']),
                    user_id=user_id,
                    amount=amount,
                    db=self.db
                )

            case 'avatar':
                await self.payment_service.on_payment_avatar(
                    user_id=user_id,
                    model_level=int(metadata['model_level']),
                    amount=amount,
                    db=self.db
                )

            case _:
                pass

        try:
            await OrdersRepo(self.db).delete(id=order_id)
        except:
            pass
