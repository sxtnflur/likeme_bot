import aiogram
from bot import keyboards
from database import PaymentsRepo, UsersRepo, ModelsRepo, AvatarsRepo
from schemas.payment import ImageGenerationsBuy
from services.avatars_service import AvatarsService
from sqlalchemy.ext.asyncio import AsyncSession
from texts import get_texts


class PaymentService:
    image_packages = [
        ImageGenerationsBuy(
            id=1, generations=50, price=790
        ),
        ImageGenerationsBuy(
            id=2, generations=100, price=1390
        ),
        ImageGenerationsBuy(
            id=3, generations=300, price=2790
        )
    ]
    model_level_0_price: int = 290
    model_level_1_price: int = 1390

    def __init__(self, bot: aiogram.Bot):
        self.bot = bot

    async def get_image_packages(self) -> list[ImageGenerationsBuy]:
        return self.image_packages

    async def get_image_package(self, id: int) -> ImageGenerationsBuy:
        return list(filter(lambda x: x.id == id, self.image_packages))[0]

    async def on_payment_package(self, package_id: int, user_id: int, amount: float, db: AsyncSession) -> None:
        package = await self.get_image_package(package_id)
        await PaymentsRepo(db).add(
            user_id=user_id,
            package_id=package_id,
            amount=amount,
            type='package'
        )
        updated_generations = await UsersRepo(db).increase_field(
            filters=dict(id=user_id),
            field='image_generations',
            value=package.generations
        )
        language = await UsersRepo(db).get_one_field('language', id=user_id)
        texts = get_texts(language)
        await self.bot.send_message(
            chat_id=user_id,
            text=texts.payment.on_success_payment_package(updated_generations)
        )

    async def on_payment_model(self, user_id: int, amount: float, db: AsyncSession,
                               avatar_id: int, level: int = 1) -> None:
        await PaymentsRepo(db).add(
            user_id=user_id,
            amount=amount,
            type='model'
        )
        model_id = await ModelsRepo(db).add_and_get(
            dict(avatar_id=avatar_id,
                 level=level,
                 status='paid'),
            'id'
        )
        language = await UsersRepo(db).get_one_field('language', id=user_id)
        texts = get_texts(language)
        await self.bot.send_message(
            chat_id=user_id,
            text=texts.payment.ON_SUCCESS_PAYMENT,
            reply_markup=keyboards.on_success_payment_model(
                model_id=model_id,
                texts=texts,
                level=level
            )
        )

    async def on_payment_avatar(self, user_id: int, amount: float, db: AsyncSession) -> None:
        await PaymentsRepo(db).add(
            user_id=user_id,
            amount=amount,
            type='avatar'
        )
        await UsersRepo(db).update(
            filters=dict(id=user_id),
            updates=dict(can_create_avatar=True)
        )
        language = await UsersRepo(db).get_one_field('language', id=user_id)
        texts = get_texts(language)
        await self.bot.send_message(
            chat_id=user_id,
            text=texts.payment.ON_SUCCESS_PAYMENT,
            reply_markup=keyboards.on_success_payment_avatar(texts)
        )