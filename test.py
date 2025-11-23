import asyncio

from api.depends import get_payments_use_case
from database.engine import async_session


def test_payment_avatar():
    async def do():
        async with async_session() as session:
            use_case = get_payments_use_case(session)
            await use_case.on_payment(
                amount=1490, metadata=dict(
                    type='avatar',
                    user_id=1304563494,
                    model_level=1
                )
            )
            await session.commit()
    asyncio.get_event_loop().run_until_complete(do())


if __name__ == '__main__':
    test_payment_avatar()