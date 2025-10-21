import fal_client
import io
import zipfile
import os

from aiogram import Bot


async def upload_zip(file: bytes) -> str:
    return await fal_client.upload_async(file)


async def upload_zip_by_file_ids(file_ids: list[str], user_id: int, bot: Bot):

    saved_files = []
    for file_id in file_ids:
        file = await bot.download(file_id)
        saved_files.append(file)

    b_io = io.BytesIO()
    with zipfile.ZipFile(b_io, "w") as z:
        for i, p in enumerate(saved_files):
            z.writestr(os.path.basename(f'{user_id}_{i}.jpg'), data=p.read())
    return await upload_zip(b_io.read())