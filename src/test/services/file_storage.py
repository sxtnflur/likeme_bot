import asyncio
from pathlib import Path

import aiohttp
from database import db_connect, GeneratedImage
from sqlalchemy.ext.asyncio import AsyncSession
from database.repositories import GeneratedImagesRepo
from depends import files_storage


@db_connect()
async def move_gen_images_to_s3(db: AsyncSession):
    gen_images: list[GeneratedImage] = list(await GeneratedImagesRepo(db).get_list())

    async with files_storage.start_transaction() as trans:
        async with aiohttp.ClientSession() as session:
            for image in gen_images:
                if 'https://bigling.ru/cdn/likeme/' not in image.image_url:
                    continue
                file_path = image.image_url.split('https://bigling.ru/cdn/likeme/')[1]
                resp = await session.get(image.image_url)
                new_url = await trans.save_file_get_url(file=await resp.read(), by_file_path=Path(file_path))
                image.image_url = new_url


if __name__ == '__main__':
    asyncio.run(move_gen_images_to_s3())