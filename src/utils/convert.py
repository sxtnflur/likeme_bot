import aiohttp
from aiogram.types import BufferedInputFile
from aiogram import Bot
from PIL import Image
import io


async def image_url_to_bytes(image_url: str, session: aiohttp.ClientSession) -> bytes:
    async with session.get(url=image_url) as response:
        return await response.read()


async def image_url_to_input_file(image_url: str, session: aiohttp.ClientSession,
                                   filename: str = 'generated_image.jpg') -> BufferedInputFile:
    async with session.get(url=image_url) as response:
        return BufferedInputFile(await response.read(), filename)


async def videos_urls_to_input_files(
    video_url: str, session: aiohttp.ClientSession,
    filename: str = 'generated_video.mp4'
) -> BufferedInputFile:
    return await image_url_to_input_file(
        video_url, session=session, filename=filename
    )


async def image_url_to_pil(url: str, session: aiohttp.ClientSession) -> Image.Image:
    async with session.get(url) as response:
        response.raise_for_status()
        # file = await file.read()
        file = io.BytesIO(await response.read())
    return Image.open(file)


async def image_file_id_to_pil(file_id: str, bot: Bot) -> Image.Image:
    return Image.open(io.BytesIO((await bot.download(file_id)).read()))