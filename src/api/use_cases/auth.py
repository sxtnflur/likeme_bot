import aiohttp
from aiogram.utils.web_app import safe_parse_webapp_init_data, WebAppUser
from config import settings
from services.users import UsersService
from sqlalchemy.ext.asyncio import AsyncSession


class AuthUseCase:
    def __init__(self, db: AsyncSession, users_service: UsersService):
        self.db = db
        self.users_service = users_service

    async def auth_by_telegram_init_data(self, init_data: str) -> WebAppUser | None:
        try:
            data = safe_parse_webapp_init_data(token=settings.BOT_TOKEN, init_data=init_data)
        except ValueError:
            return

        async with aiohttp.ClientSession() as session:
            resp = await session.get(data.user.photo_url)
            avatar = await resp.read()

        await self.users_service.add_user_with_avatar(
            avatar=avatar,
            tg_id=data.user.id,
            first_name=data.user.first_name,
            last_name=data.user.last_name,
            username=data.user.username,
            language=data.user.language_code,
            db=self.db
        )
        return data.user
