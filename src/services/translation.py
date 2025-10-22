from services.ai.openai_service import OpenAIService


class TranslationService:
    def __init__(self, openai: OpenAIService):
        self.openai = openai

    async def translate_by_openai(self, text: str, model: str | None = None) -> str:
        resp = await self.openai.send_text_prompt(
            prompt=text,
            messages=[{'role': 'system', 'content': 'Переводи на английский язык'}],
            max_tokens=4000,
            model=model
        )
        return resp.text_answer

    async def translate_ru_to_en(self, text: str) -> str:
        try:
            return await self.translate_by_openai(text, model='gpt-4.1-mini')
        except Exception as e:
            return text
