from datetime import datetime
from uuid import UUID
from sqlalchemy import func, BIGINT, text
from sqlalchemy.orm import declarative_base, mapped_column
from typing_extensions import Annotated

Base = declarative_base()

IntPk = Annotated[int, mapped_column(primary_key=True, autoincrement=True)]
TgId = Annotated[int, mapped_column(BIGINT)]
TgIdPk = Annotated[int, mapped_column(BIGINT, primary_key=True)]
CreatedAt = Annotated[datetime, mapped_column(server_default=func.now())]
UUIDPK = Annotated[UUID, mapped_column(primary_key=True, server_default=text("gen_random_uuid()"))]