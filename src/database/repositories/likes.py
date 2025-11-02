from database import models
from database.repositories.base import BaseRepo


class LikesRepo(BaseRepo[models.Like]):
    model = models.Like