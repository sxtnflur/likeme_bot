from datetime import datetime

from sqlalchemy import func, BIGINT, ForeignKey
from sqlalchemy.orm import declarative_base, mapped_column
from typing_extensions import Annotated

Base = declarative_base()

IntPk = Annotated[int, mapped_column(primary_key=True, autoincrement=True)]
TgId = Annotated[int, mapped_column(BIGINT)]
TgIdPk = Annotated[int, mapped_column(BIGINT, primary_key=True)]
CreatedAt = Annotated[datetime, mapped_column(server_default=func.now())]
# UpdatedAt = Annotated[datetime, mapped_column(server_default=func.now(),
#                                               server_onupdate=func.now()]
