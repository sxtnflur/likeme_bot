from pydantic import BaseModel
from typing import TypeVar, Generic

TSchema = TypeVar('TSchema', bound=BaseModel)


class GPTResponse(BaseModel):
    text_prompt: str | list[dict] | None = None
    text_answer: str


class GPTSchemaResponse(BaseModel, Generic[TSchema]):
    prompt: str | list[dict] | None = None
    answer: TSchema
