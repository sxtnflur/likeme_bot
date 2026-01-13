import asyncio

from api.depends import get_payments_use_case
from database.engine import async_session
from services.ai.fal.face_swap import FaceSwapper


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


def test_face_swap():
    face_swapper = FaceSwapper()
    user_embed = face_swapper.save_face_data()
    face_swapper.swap_face(image=..., face_data=user_embed)


if __name__ == '__main__':
    test_payment_avatar()