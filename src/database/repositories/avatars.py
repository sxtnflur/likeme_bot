from schemas.avatars import AvatarSchema
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from .base import BaseRepo
from .. import models


class AvatarsRepo(BaseRepo[models.Avatar]):
    model = models.Avatar

    async def get_one(self, **filters) -> models.Avatar | None:
        stmt = (
            select(models.Avatar)
            .filter_by(**filters)
        )
        avatar = await self.db.scalar(stmt)
        if not avatar:
            return
        return AvatarSchema.model_validate(avatar)

    async def get_by_user_current(self, user_id: int) -> AvatarSchema | None:
        stmt = (
            select(models.Avatar)
            .select_from(models.User)
            .filter(models.Avatar.id == models.User.current_avatar_id,
                    models.User.id == user_id)
        )
        avatar = await self.db.scalar(stmt)
        if not avatar:
            return
        return AvatarSchema.model_validate(avatar)