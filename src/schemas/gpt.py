from pydantic import BaseModel


class GPTResponse(BaseModel):
    text_prompt: str | list[dict] | None = None
    text_answer: str