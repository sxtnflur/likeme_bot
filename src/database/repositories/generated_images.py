from enum import StrEnum

from sqlalchemy import select, desc, func
from sqlalchemy.orm import selectinload
from .base import BaseRepo
from ..models.generated_images import GeneratedImage


class FeedStrategy(StrEnum):
    NEWEST = "newest"
    POPULAR = "popular"
    TRENDING = "trending"


class GeneratedImagesRepo(BaseRepo[GeneratedImage]):
    model = GeneratedImage

    async def get_list_with_user(
            self, filters: dict,
            strategy: FeedStrategy = FeedStrategy.NEWEST,
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

        if strategy == FeedStrategy.NEWEST:
            stmt = stmt.order_by(desc(self.model.created_at))

        elif strategy == FeedStrategy.POPULAR:
            # Предполагаем, что у вас есть поля для оценки популярности
            stmt = stmt.order_by(
                desc(self.model.likes_count),  # или views_count, rating и т.д.
                desc(self.model.created_at)  # второстепенная сортировка по новизне
            )

        elif strategy == FeedStrategy.TRENDING:
            # Более сложная логика - комбинация популярности и новизны
            # Например: популярность * коэффициент новизны
            stmt = stmt.order_by(
                desc(self.model.likes_count * func.exp(
                    -0.1 * func.extract('epoch', func.now() - self.model.created_at))),
                desc(self.model.created_at)
            )

        return await self.db.scalars(stmt)