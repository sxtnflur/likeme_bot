from .base import BaseRepo
from .. import models


class UsersRepo(BaseRepo[models.User]):
    model = models.User