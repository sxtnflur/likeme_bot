from database.models.base import Base
from sqlalchemy import delete, select, update, exists, insert, text, func
from sqlalchemy.ext.asyncio import AsyncSession
from typing_extensions import TypeVar, Protocol

T = TypeVar('T', bound=Base)


class BaseRepo(Protocol[T]):
    model: type[Base]

    def __init__(self, db: AsyncSession):
        self.db = db

    def _prepare_filters(self, filters: dict) -> list:
        _filters = []

        for k, v in filters.items():
            if '__' in k:
                field_name = k.split('__')[0]
                action = k.split('__')[1]
                if action == 'in':
                    if not isinstance(v, list):
                        raise ValueError(f'{k} должен быть списком')
                    if not hasattr(self.model, field_name):
                        raise ValueError(f'{self.model.__name__} не имеет поля {field_name}')

                    _filters.append(getattr(self.model, field_name).in_(v))
                elif action == 'lt':
                    _filters.append(getattr(self.model, field_name).__lt__(v))
                elif action == 'le':
                    _filters.append(getattr(self.model, field_name).__le__(v))
                elif action == 'gt':
                    _filters.append(getattr(self.model, field_name).__gt__(v))
                elif action == 'ge':
                    _filters.append(getattr(self.model, field_name).__ge__(v))
                elif action == 'not':
                    _filters.append(getattr(self.model, field_name) != v)
            else:
                _filters.append(getattr(self.model, k) == v)
        return _filters

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
            .filter(*self._prepare_filters(filters))
        )

    async def get_list(
        self, filters: dict | None = None, offset: int = 0, limit: int | None = 10
    ) -> list[T]:
        stmt = select(self.model)
        if filters:
            stmt = stmt.filter(*self._prepare_filters(filters))
        if offset:
            stmt = stmt.offset(offset)
        if limit:
            stmt = stmt.limit(limit)
        return await self.db.scalars(stmt)

    async def get_one_field(self, field: str, **filters):
        return await self.db.scalar(
            select(getattr(self.model, field))
            .filter(*self._prepare_filters(filters))
        )

    async def get_only_fields(self, fields: list[str], **filters) -> tuple:
        fields_ = [getattr(self.model, f) for f in fields]
        res = await self.db.execute(
            select(*fields_).filter(*self._prepare_filters(filters))
        )
        return res.fetchone()

    async def update(self, filters: dict, updates: dict) -> None:
        await self.db.execute(
            update(self.model)
            .filter(*self._prepare_filters(filters))
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
            .filter(*self._prepare_filters(filters))
            .values(**{field: getattr(self.model, field) - value})
            .returning(getattr(self.model, field))
        )

    async def delete(self, **filters) -> None:
        await self.db.execute(
            delete(self.model)
            .filter(*self._prepare_filters(filters))
        )

    async def exists(self, **filters) -> bool:
        return await self.db.scalar(
            select(
                exists()
                .select_from(self.model)
                .where(*self._prepare_filters(filters))
            )
        )

    async def count(self, **filters) -> int:
        return await self.db.scalar(
            select(func.count())
            .select_from(self.model)
            .filter(*self._prepare_filters(filters))
        )

