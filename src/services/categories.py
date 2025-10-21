from enum import Enum, auto, StrEnum
from pydantic import BaseModel
from services.ai.openai_service import OpenAIService


class CategoriesEnum(StrEnum):
    reality = auto()
    fantasy = auto()
    aesthetics = auto()
    celebrities = auto()
    surrealism = auto()
    memes = auto()
    futurism = auto()


class CategoriesService:
    enum = CategoriesEnum
    category_keys: list[str] = list(map(lambda x: x.name, enum))

    def __init__(self, openai: OpenAIService):
        self.openai = openai

    async def generate_categories_for_image(self, image_url: str) -> list[str]:
        class GPTSchema(BaseModel):
            categories: list[CategoriesEnum] = []

        res = await self.openai.send_images_get_schema(
            schema=GPTSchema,
            photo_urls=[image_url],
            messages=[{
                'role': 'system',
                'content': '''
                Есть категории на выбор:
                
                reality - Реальность+ (реалистичный фото)
                fantasy - Фэнтези
                aesthetics - Эстетика
                celebrities - Знаменитости
                surrealism - Сюрреализм
                memes - Мемы
                futurism - Футуризм
                
                Ты должен выбрать, к каким категориям относится сгенерированное нейросетью изображение, которое тебе отправлено
                '''}],
            model='gpt-4.1-mini'
        )
        keys = list(map(lambda x: str(x.name), res.categories))
        print(f'{keys=}')
        return keys