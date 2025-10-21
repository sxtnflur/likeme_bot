from database.models.fal_requests import FalRequest
from database.repositories.base import BaseRepo


class FalRequestsRepo(BaseRepo[FalRequest]):
    model = FalRequest