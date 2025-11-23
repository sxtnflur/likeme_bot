from pydantic import BaseModel


class GenerationsBuy(BaseModel):
    id: int
    generations: int
    price: int


class ImageGenerationsBuy(GenerationsBuy): ...


class ModelInfo(BaseModel):
    name: str
    level: int
    price: int
    payment_description: str