import datetime

from bot import screens, loader
from database import AvatarsRepo, db_connect, GeneratedImagesRepo, PaymentsRepo
from services.bg_tasks.base import BgTasksProtocol
from services.feed import get_random_top_generation, RandomGeneration
from sqlalchemy.ext.asyncio import AsyncSession
from texts import get_texts
from utils.tg_link import create_remix_link


@db_connect()
async def on_first_start_bot(ctx, user_id: int, language: str = 'ru', *, db: AsyncSession | None = None):
    print('on_first_start_bot done')
    if not await AvatarsRepo(db).exists(user_id=user_id):
        await screens.notifications.didnot_load_photos_in_begin(
                get_texts(language)
        ).send_by_id(user_id, bot=loader.bot)


@db_connect()
async def on_created_avatar(ctx, ts_from: int, user_id: int, language: str = 'ru', *, db: AsyncSession | None = None):
    if not await GeneratedImagesRepo(db).exists(
        user_id=user_id, created_at__ge=datetime.datetime.fromtimestamp(ts_from)
    ):
        random_generation: RandomGeneration = await get_random_top_generation(db=db)
        await screens.notifications.created_avatar_didnot_generations(
            texts=get_texts(language),
            user_name=random_generation.user_name,
            image_url=random_generation.image_url,
            remix_it_url=create_remix_link(random_generation.generation_id)
        ).send_by_id(user_id, bot=loader.bot)


@db_connect()
async def on_spent_generations(ctx, ts_from: int, user_id: int, language: str = 'ru', *, db: AsyncSession | None = None):
    if not await PaymentsRepo(db).exists(
        user_id=user_id, created_at__ge=datetime.datetime.fromtimestamp(ts_from)
    ):
        random_generation: RandomGeneration = await get_random_top_generation(db=db)
        await screens.notifications.generations_spent_and_no_payments(
            image_url=random_generation.image_url
        ).send_by_id(user_id, bot=loader.bot)


class NotificationsBgTasks:
    functions = [on_first_start_bot, on_created_avatar]

    def __init__(self, bg_tasks_service: BgTasksProtocol):
        self.bg_tasks_service = bg_tasks_service

    async def on_first_start_bot(self, user_id: int, language: str = 'ru'):
        await self.bg_tasks_service.delay(
            on_first_start_bot, user_id, language,
            delay_by=datetime.timedelta(hours=24)
        )

    async def on_created_avatar(self, user_id: int, language: str = 'ru'):
        await self.bg_tasks_service.delay(
            on_created_avatar,
            round(datetime.datetime.utcnow().timestamp()), user_id, language,
            delay_by=datetime.timedelta(hours=24)
        )

    async def on_spent_generations(self, user_id: int, language: str = 'ru'):
        await self.bg_tasks_service.delay(
            on_spent_generations,
            round(datetime.datetime.utcnow().timestamp()), user_id, language,
            delay_by=datetime.timedelta(hours=24)
        )