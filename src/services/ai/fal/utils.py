from typing import IO

import fal_client
import io
import zipfile
import os

from aiogram import Bot


async def upload_zip(file: bytes, file_name: str | None = None) -> str:
    return await fal_client.upload_async(file, content_type='application/zip',
                                         file_name=file_name)


async def upload_zip_by_io(files: list[IO]) -> str:
    b_io = io.BytesIO()
    with zipfile.ZipFile(b_io, "w") as z:
        for i, file in enumerate(files):
            z.writestr(os.path.basename(file.name), data=file.read())
            file.close()

    b_io.seek(0)
    return await upload_zip(b_io.getvalue())


async def upload_zip_by_file_ids(file_ids: list[str], bot: Bot):

    saved_files = []
    for i, file_id in enumerate(file_ids):
        file = await bot.download(file_id)
        file.name = f'{i}.jpg'
        saved_files.append(file)

    return await upload_zip_by_io(files=saved_files)