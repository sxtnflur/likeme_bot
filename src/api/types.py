from fastapi import Query
from typing_extensions import Annotated

Offset = Annotated[int | None, Query(ge=0)]
Limit = Annotated[int, Query(ge=1, le=100)]