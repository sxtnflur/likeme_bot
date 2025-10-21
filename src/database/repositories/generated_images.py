from enum import StrEnum

from sqlalchemy import select, desc, func
from sqlalchemy.orm import selectinload
from .base import BaseRepo
from ..models.generated_images import GeneratedImage, Like


class FeedOrdering(StrEnum):
    new = "new"
    top = "top"
    all = "all"


class GeneratedImagesRepo(BaseRepo[GeneratedImage]):
    model = GeneratedImage

    async def get_list_with_user(
            self, filters: dict,
            ordering: FeedOrdering = FeedOrdering.all,
            offset: int | None = None,
            limit: int | None = None
    ) -> list[GeneratedImage]:
        '''

        :param strategy:
        :param filters:
        :param offset:
        :param limit:
        :return:
        '''
        stmt = (
            select(self.model)
            .options(
                selectinload(self.model.user)
            )
            .filter_by(**filters)
        )
        if offset:
            stmt = stmt.offset(offset)
        if limit:
            stmt = stmt.limit(limit)

        if ordering == FeedOrdering.new:
            stmt = stmt.order_by(desc(self.model.created_at))

        elif ordering == FeedOrdering.top:
            likes_subquery = (
                select(
                    Like.image_id,
                    func.count(Like.user_id).label('likes_count')
                )
                .group_by(Like.image_id)
                .subquery()
            )

            stmt = (
                stmt
                .outerjoin(likes_subquery, self.model.id == likes_subquery.c.image_id)
                .order_by(
                    desc(likes_subquery.c.likes_count),
                    desc(self.model.created_at)
                )
            )

        elif ordering == FeedOrdering.all:
            likes_subquery = (
                select(
                    Like.image_id,
                    func.count(Like.user_id).label('likes_count')
                )
                .group_by(Like.image_id)
                .subquery()
            )

            # Используем логарифмическую шкалу времени для избежания underflow
            time_diff_hours = func.extract('epoch', func.now() - self.model.created_at) / 3600
            # Формула: лайки / (1 + время_в_часах^1.5) - популярность со временем убывает
            score = func.coalesce(likes_subquery.c.likes_count, 0) / (1 + func.pow(time_diff_hours, 1.5))

            stmt = (
                stmt
                .outerjoin(likes_subquery, self.model.id == likes_subquery.c.image_id)
                .order_by(
                    desc(score),
                    desc(self.model.created_at)
                )
            )

        return await self.db.scalars(stmt)

    async def count_likes(self, id: int) -> int:
        stmt = (
            select(func.count())
            .select_from(Like)
            .filter(
                Like.image_id == id
            )
        )
        return await self.db.scalar(stmt)