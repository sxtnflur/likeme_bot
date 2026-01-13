from config import settings
from services.ai.openai_service import OpenAIService


class TranslationService:
    def __init__(self, openai: OpenAIService):
        self.openai = openai

    async def translate_by_openai(self, text: str, model: str | None = None) -> str:
        resp = await self.openai.send_text_prompt(
            prompt=text,
            messages=[{'role': 'system',
                       'content': 'Тебе отправляют промпты для генерации изображений с лицом пользователя. '
                                  'Твоя задача - перевести промпт на английский язык; '
                                  'Поменять слова, обозначающие основной субъект, '
                                  'по чьему лицу будет генерироваться, на слово "{trigger}". '
                                  'Отправь в ответ только отредактированный промпт, '
                                  'не оставляй никакх комментариев. '
                                  'Например: Я бегу по пляжу, и на меня все смотрят -> '
                                  '{trigger} running on the beach and everyone\'s looking at {trigger}'
                       .format(trigger=settings.TRIGGER_WORD)}],
            max_tokens=4000,
            model=model
        )
        return resp.text_answer

    async def translate_ru_to_en(self, text: str) -> str:
        try:
            return await self.translate_by_openai(text, model='gpt-4.1-mini')
        except Exception as e:
            return text
