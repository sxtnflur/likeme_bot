from pydantic import BaseModel


class GenerationsBuy(BaseModel):
    id: int
    generations: int
    price: int


class ImageGenerationsBuy(GenerationsBuy): ...