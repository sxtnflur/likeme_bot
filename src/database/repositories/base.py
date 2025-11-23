from database.models.base import Base
from sqlalchemy import delete, select, update, exists, insert, text, func
from sqlalchemy.ext.asyncio import AsyncSession
from typing_extensions import TypeVar, Protocol

T = TypeVar('T', bound=Base)


class BaseRepo(Protocol[T]):
    model: type[Base]

    def __init__(self, db: AsyncSession):
        self.db = db

    async def add(self, **vals) -> None:
        self.db.add(self.model(**vals))

    async def add_all(self, objs: list[dict]) -> None:
        await self.db.execute(
            insert(self.model)
            .values(objs)
        )

    async def add_or_update(self, values: dict, not_update: list[str], on_conflict: list[str]) -> None:
        keys = list(values.keys())
        fields = ', '.join(keys)
        vals_names = ', '.join(list(map(lambda k: f':{k}', keys)))
        on_conflict_ = ', '.join(on_conflict)
        set_ = ', '.join([f'{k}=EXCLUDED.{k}' for k in keys if k not in not_update])
        stmt = text(f'''
        INSERT INTO {self.model.__tablename__} ({fields})
        VALUES ({vals_names})
        ON CONFLICT ({on_conflict_}) DO UPDATE SET {set_}
        ''').bindparams(**values)
        await self.db.execute(stmt)

    async def add_and_get(self, obj: dict, get_field: str = 'id'):
        return await self.db.scalar(
            insert(self.model)
            .values(**obj)
            .returning(getattr(self.model, get_field))
        )

    async def get_one(self, **filters) -> T:
        return await self.db.scalar(
            select(self.model)
            .filter_by(**filters)
        )

    async def get_list(
        self, filters: dict | None = None, offset: int = 0, limit: int | None = 10
    ) -> list[T]:
        stmt = select(self.model)
        if filters:
            stmt = stmt.filter_by(**filters)
        if offset:
            stmt = stmt.offset(offset)
        if limit:
            stmt = stmt.limit(limit)
        return await self.db.scalars(stmt)

    async def get_one_field(self, field: str, **filters):
        return await self.db.scalar(
            select(getattr(self.model, field))
            .filter_by(**filters)
        )

    async def get_only_fields(self, fields: list[str], **filters) -> tuple:
        fields_ = [getattr(self.model, f) for f in fields]
        res = await self.db.execute(
            select(*fields_).filter_by(**filters)
        )
        return res.fetchone()

    async def update(self, filters: dict, updates: dict) -> None:
        await self.db.execute(
            update(self.model)
            .filter_by(**filters)
            .values(**updates)
        )

    async def increase_field(self, filters: dict, field: str, value: int) -> int:
        return await self.db.scalar(
            update(self.model)
            .filter_by(**filters)
            .values(**{field: getattr(self.model, field) + value})
            .returning(getattr(self.model, field))
        )

    async def decrease_field(self, filters: dict, field: str, value: int) -> int:
        return await self.db.scalar(
            update(self.model)
            .filter_by(**filters)
            .values(**{field: getattr(self.model, field) - value})
            .returning(getattr(self.model, field))
        )

    async def delete(self, **filters) -> None:
        await self.db.execute(
            delete(self.model)
            .filter_by(**filters)
        )

    async def exists(self, **filters) -> bool:
        return await self.db.scalar(
            select(
                exists()
                .select_from(self.model)
                .where(
                    *[getattr(self.model, key) == value for key, value in filters.items()]
                )
            )
        )

    async def count(self, **filters) -> int:
        return await self.db.scalar(
            select(func.count())
            .select_from(self.model)
            .filter_by(**filters)
        )

