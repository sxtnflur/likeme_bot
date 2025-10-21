from database.repositories.base import BaseRepo
from ..models.categories import Category, GeneratedImageCategory


class CategoriesRepo(BaseRepo[Category]):
    model = Category


class GeneratedImagesCategoriesRepo(BaseRepo[GeneratedImageCategory]):
    model = GeneratedImageCategory