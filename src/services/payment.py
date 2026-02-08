import aiogram
from bot import keyboards, screens
from database import PaymentsRepo, UsersRepo, AvatarsRepo
from schemas.payment import ImageGenerationsBuy, ModelInfo
from services.avatars_service import AvatarsService
from sqlalchemy.ext.asyncio import AsyncSession
from texts import get_texts

image_packages = [
        ImageGenerationsBuy(
            id=1, generations=1, price=1
        ),
        ImageGenerationsBuy(
            id=2, generations=50, price=790
        ),
        ImageGenerationsBuy(
            id=3, generations=100, price=1390
        ),
        ImageGenerationsBuy(
            id=4, generations=300, price=2790
        )
    ]
models = {
    0: ModelInfo(
        name='Simple',
        level=0,
        price=290,
        payment_description='Покупка аватара Simple'
    ),
    1: ModelInfo(
        name='Portrait',
        level=1,
        price=1390,
        payment_description='Покупка аватара Portrait'
    )
}


class PaymentService:
    image_packages = image_packages
    models = models
    # model_level_0_price: int = 290
    # model_level_1_price: int = 1390

    def __init__(self, bot: aiogram.Bot,
                 avatars_service: AvatarsService):
        self.bot = bot
        self.avatars_service = avatars_service

    def get_model_info(self, level: int):
        return self.models.get(level)

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
        await screens.payment.on_successful_payment_package(
            texts, generations=updated_generations
        ).send_by_id(user_id, bot=self.bot)

    async def on_payment_avatar(self, user_id: int, amount: float,
                                model_level: int, db: AsyncSession) -> None:
        avatar_id = await self.avatars_service.create_avatar(
            user_id=user_id,
            level=model_level,
            db=db
        )
        gens_by_model_level = {
            0: 3, 1: 7
        }
        await UsersRepo(db).increase_field(
            filters=dict(id=user_id),
            field='image_generations',
            value=gens_by_model_level.get(model_level, 0)
        )
        await PaymentsRepo(db).add(
            user_id=user_id,
            amount=amount,
            type='avatar'
        )
        language = await UsersRepo(db).get_one_field('language', id=user_id)
        texts = get_texts(language)
        await screens.payment.on_success_payment_avatar(texts, avatar_id=avatar_id)