import datetime
from typing import Callable

from typing_extensions import Protocol


class BgTasksProtocol(Protocol):
    async def delay(self, f: Callable, *args,
                    delay_by: datetime.timedelta | None = None,
                    delay_until: datetime.datetime | None = None, **kwargs): ...