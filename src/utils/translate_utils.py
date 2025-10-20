from depends import openai_service


async def translate_by_openai(text: str, model: str | None = None) -> str:
    resp = await openai_service.send_text_prompt(
        prompt=text,
        messages=[{'role': 'system', 'content': 'Переводи на английский язык'}],
        max_tokens=4000,
        model=model
    )
    return resp.text_answer


async def translate_ru_to_en(text: str) -> str:
    try:
        return await translate_by_openai(text, model='gpt-4o-mini')
        # translated = MyMemoryTranslator(source='ru-RU', target='en-GB').translate(text)
        # return translated
    except Exception as e:
        return text
