from .base import BaseRepo
from ..models import Promocode, UsedPromocodes


class PromocodesRepo(BaseRepo[Promocode]):
    model = Promocode


class UsedPromocodesRepo(BaseRepo[UsedPromocodes]):
    model = UsedPromocodes