from .base import BaseRepo
from ..models import Promocode


class PromocodesRepo(BaseRepo[Promocode]):
    model = Promocode