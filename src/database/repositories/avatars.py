from schemas.avatars import AvatarWithModelsSchema
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from .base import BaseRepo
from .. import models


class AvatarsRepo(BaseRepo[models.Avatar]):
    model = models.Avatar

    async def get_one(self, **filters) -> AvatarWithModelsSchema | None:
        stmt = (
            select(models.Avatar)
            # .join(self.model.models)
            .options(
                selectinload(self.model.models)
            )
        )
        avatar = await self.db.scalar(stmt)
        return AvatarWithModelsSchema.model_validate(avatar)

    async def get_by_user_current(self, user_id: int) -> AvatarWithModelsSchema | None:
        stmt = (
            select(models.Avatar)
            .select_from(models.User)
            .options(
                selectinload(self.model.models)
            )
            .filter(models.Avatar.id == models.User.current_avatar_id,
                    models.User.id == user_id)
        )
        avatar = await self.db.scalar(stmt)
        return AvatarWithModelsSchema.model_validate(avatar)

class ModelsRepo(BaseRepo[models.Model]):
    model = models.Model