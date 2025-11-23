import aiohttp
import openai
import base64
from pydantic import BaseModel
from schemas.gpt import GPTResponse, GPTSchemaResponse, TSchema
from openai import AsyncOpenAI, NOT_GIVEN
from openai.types.chat import ChatCompletionMessageParam
from typing_extensions import Iterable, TypeVar
import os


class OpenAIService:
    def __init__(self,
         openai_client: AsyncOpenAI,
         default_model: str | None = None,
         default_max_tokens: int | None = None,
         default_max_completition_tokens: int | None = None,
         system_prompt: str | None = None
    ):
        self.client = openai_client
        self.default_model = default_model
        self.default_max_tokens = default_max_tokens
        self.default_max_completition_tokens = default_max_completition_tokens
        self.system_prompt = system_prompt

    async def _send_completition(self, messages: list[ChatCompletionMessageParam],
                                 model: str | None = None,
                                 max_tokens: int | None = None,
                                 max_completion_tokens: int | None = None,
                                 **kwargs):
        if self.system_prompt:
            messages = [self.text_to_system_message(self.system_prompt)] + messages
        resp = await self.client.chat.completions.create(
            messages=messages,
            model=model or self.default_model,
            # max_tokens=max_tokens or self.default_max_tokens or NOT_GIVEN,
            max_completion_tokens=max_completion_tokens or self.default_max_completition_tokens or NOT_GIVEN,
            **kwargs
        )
        return resp

    async def _send_completition_get_schema(self, messages: list[ChatCompletionMessageParam],
                                 schema: type[TSchema],
                                 model: str | None = None,
                                 max_tokens: int | None = None,
                                 max_completion_tokens: int | None = None,
                                 **kwargs) -> TSchema:
        if self.system_prompt:
            messages = [self.text_to_system_message(self.system_prompt)] + messages
        resp = await self.client.chat.completions.parse(
            response_format=schema,
            messages=messages,
            model=model or self.default_model,
            max_tokens=max_tokens or self.default_max_tokens or NOT_GIVEN,
            max_completion_tokens=max_completion_tokens or self.default_max_completition_tokens or NOT_GIVEN,
            **kwargs
        )
        return resp

    @staticmethod
    def text_to_assistant_message(text: str) -> dict:
        return {
            'role': 'assistant', 'content': text
        }

    @staticmethod
    def text_to_user_message(text: str) -> dict:
        return {
            'role': 'user', 'content': text
        }

    @staticmethod
    def text_to_system_message(content: str) -> dict:
        return {
                'role': 'system', 'content': content
            }

    async def send_text_prompt(self, prompt: str,
                               messages: Iterable[ChatCompletionMessageParam] | None = None,
                               model: str | None = None,
                               **kwargs) -> GPTResponse:
        msgs = messages or []
        msgs.append(self.text_to_user_message(prompt))
        resp = await self._send_completition(msgs, model, **kwargs)
        return GPTResponse(
            text_prompt=prompt,
            text_answer=resp.choices[0].message.content
        )

    async def transcript_audio(self, audio_path: str, model: str | None = None) -> str:
        with open(audio_path, "rb") as audio_file:
            transcript = await self.client.audio.transcriptions.create(
                model="whisper-1",
                file=audio_file
            )
        os.remove(audio_path)
        return transcript.text

    async def send_audio_prompt(
        self,
        audio_path: str,
        messages: Iterable[ChatCompletionMessageParam] | None = None,
        model: str | None = None,
        **kwargs
    ) -> GPTResponse:
        # await self._send_completition(
        #     messages, model=model, **kwargs
        # )

        text_prompt = await self.transcript_audio(audio_path, model)
        print(f'{text_prompt=}')
        if not text_prompt:
            raise
        return await self.send_text_prompt(
            prompt=text_prompt, messages=messages, model=model,
            **kwargs
        )

    def create_images_content(self, photo_urls: list[str], caption: str = None) -> list[dict]:
        if not photo_urls:
            raise Exception("Список 'photo_urls' пуст")

        content = []
        if caption:
            content.append({
                "type": "text", "text": caption
            })
        if len(photo_urls) == 1:
            content.append({
            "type": "image_url", "image_url": {
                "url": photo_urls[0]
            }
        })
        else:
            content += [{
                "type": "image_url",
                "image_url": {
                    "url": photo
                }
            } for photo in photo_urls]

        return content

    async def send_images(self, photo_urls: list[str], caption: str | None = None,
                         messages: Iterable[ChatCompletionMessageParam] | None = None,
                         model: str | None = None, **kwargs) -> GPTResponse:
        msgs = messages or []
        user_content = self.create_images_content(photo_urls, caption)
        msgs.append(self.text_to_user_message(user_content))
        resp = await self._send_completition(
            messages=msgs,
            model=model or self.default_model,
            **kwargs
        )
        return GPTResponse(
            text_prompt=user_content,
            text_answer=resp.choices[0].message.content
        )

    async def send_images_get_schema(
            self,
            schema: type[TSchema],
            photo_urls: list[str | bytes], caption: str | None = None,
            messages: Iterable[ChatCompletionMessageParam] | None = None,
            model: str | None = None,
            session: aiohttp.ClientSession | None = None,
            has_tries: int = 1,
            **kwargs
    ) -> TSchema:
        msgs = messages or []
        user_content = self.create_images_content(photo_urls, caption)
        msgs.append(self.text_to_user_message(user_content))
        try:
            resp = await self._send_completition_get_schema(
                schema=schema,
                messages=msgs,
                model=model or self.default_model,
                **kwargs
            )
        except openai.BadRequestError as e:
            if e.code == 'invalid_image_url' and session is not None and has_tries > 0:
                photo_urls_ = []
                for url in photo_urls:
                    photo_file = await session.get(url)
                    photo_urls_.append(
                        f'data:image/jpeg;base64,'
                        f'{base64.b64encode(await photo_file.read()).decode("utf-8")}'
                    )

                return await self.send_images_get_schema(
                    schema=schema,
                    photo_urls=photo_urls_,
                    messages=messages,
                    model=model,
                    session=session,
                    has_tries=has_tries,
                    **kwargs
                )

        return resp.choices[0].message.parsed