from sqlalchemy import select
from .base import BaseRepo
from .. import models


class AvatarsRepo(BaseRepo[models.Avatar]):
    model = models.Avatar

    async def get_by_user_current(self, user_id: int) -> models.Avatar | None:
        stmt = (
            select(models.Avatar)
            .select_from(models.User)
            .filter(models.Avatar.id == models.User.current_avatar_id,
                    models.User.id == user_id)
        )
        return await self.db.scalar(stmt)