import dataclasses

from database import GeneratedImagesRepo, db_connect
from sqlalchemy.ext.asyncio import AsyncSession


@dataclasses.dataclass
class RandomGeneration:
    user_name: str
    generation_id: int
    image_url: str


@db_connect()
async def get_random_top_generation(*, db: AsyncSession | None = None) -> RandomGeneration:
    gen = await GeneratedImagesRepo(db).get_random_top_generation()
    return RandomGeneration(
        user_name=gen.user.first_name,
        generation_id=gen.id,
        image_url=gen.image_url
    )