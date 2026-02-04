from typing import Callable, AsyncIterable

from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine, AsyncSession
from config import settings

async_engine = create_async_engine(settings.DATABASE_URL, echo=False)

async_session = async_sessionmaker(autocommit=False, autoflush=False, bind=async_engine)


async def get_db() -> AsyncIterable[AsyncSession]:
    db = async_session()
    try:
        yield db
    except Exception as e:
        await db.rollback()
        raise e
    else:
        await db.commit()
    finally:
        await db.close()


def connection(func: Callable):
    # @functools.wraps
    async def wrapper(*args, **kwargs):
        async with async_session() as session:
            return await func(session, *args, **kwargs)
    return wrapper