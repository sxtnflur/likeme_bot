from enum import StrEnum
from enums.categories import CategoriesEnum
from sqlalchemy import select, desc, func, case
from sqlalchemy.orm import selectinload
from .base import BaseRepo
from ..models.categories import GeneratedImageCategory
from ..models.generated_images import GeneratedImage, Like


class FeedOrdering(StrEnum):
    new = "new"
    top = "top"
    all = "all"


class GeneratedImagesRepo(BaseRepo[GeneratedImage]):
    model = GeneratedImage

    async def get_one(self, user_id: int, **filters) -> GeneratedImage | None:
        res = await self.db.execute(
            select(self.model,
                   select(Like).filter(
                       Like.image_id == self.model.id,
                       Like.user_id == user_id
                   ).exists()
            )
            .options(
                selectinload(self.model.user)
            )
            .filter_by(**filters)
        )
        res = res.fetchone()
        return res

    async def get_feed(
            self,
            user_id: int,
            filters: dict,
            ordering: FeedOrdering = FeedOrdering.all,
            categories: list[CategoriesEnum] | None = None,
            offset: int | None = None,
            limit: int | None = None
    ) -> list[GeneratedImage]:
        """

        :param strategy:
        :param filters:
        :param offset:
        :param limit:
        :return:
        """
        stmt = (
            select(self.model,
                   select(Like).filter(
                       Like.image_id == self.model.id,
                       Like.user_id == user_id
                   ).exists()
                   )
            .options(
                selectinload(self.model.user)
            )
            .filter_by(**filters)
        )
        if offset:
            stmt = stmt.offset(offset)
        if limit:
            stmt = stmt.limit(limit)

        if categories:
            stmt = (
                stmt.join(self.model.categories_secondary)
                .filter(GeneratedImageCategory.category_key.in_(categories))
            )

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
                    desc(func.coalesce(likes_subquery.c.likes_count, 0)),
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

            # Комбинируем популярность и новизну через CASE для полного контроля
            time_diff_days = func.extract('epoch', func.now() - self.model.created_at) / (24 * 3600)

            # Вес в зависимости от возраста записи
            time_weight = case(
                (time_diff_days <= 1, 1.0),  # Меньше 1 дня - полный вес
                (time_diff_days <= 7, 0.7),  # 1-7 дней - 70% веса
                (time_diff_days <= 30, 0.3),  # 1-30 дней - 30% веса
                else_=0.1  # Старше 30 дней - 10% веса
            )

            score = func.coalesce(likes_subquery.c.likes_count, 0) * time_weight

            stmt = (
                stmt
                .outerjoin(likes_subquery, self.model.id == likes_subquery.c.image_id)
                .order_by(
                    desc(score),
                    desc(self.model.created_at)
                )
            )

        res = await self.db.execute(stmt)
        return res.fetchall()

    async def count_likes(self, id: int) -> int:
        stmt = (
            select(func.count())
            .select_from(Like)
            .filter(
                Like.image_id == id
            )
        )
        return await self.db.scalar(stmt)