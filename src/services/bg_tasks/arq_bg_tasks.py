from typing import Callable, Sequence, Union
from arq.typing import WorkerCoroutine
from arq.worker import Function
import datetime
import arq
from .base import BgTasksProtocol


class ARQRedisBgTasks(BgTasksProtocol):
    def __init__(self, redis_url: str,
                 max_jobs: int = 10) -> None:
        # инициализируем пул задач arq
        self.job_pool: arq.ArqRedis | None = None
        self.redis_url = redis_url
        self.max_jobs = max_jobs

    async def connect(self) -> None:
        # устанавливаем соединение с Redis
        self.job_pool = await arq.create_pool(
            arq.connections.RedisSettings.from_dsn(self.redis_url)
        )

    async def disconnect(self) -> None:
        """Для закрытия соединения"""
        if self.job_pool:
            await self.job_pool.close()

    async def run(self, functions: Sequence[Union[Function, WorkerCoroutine]]) -> None:
        """Для запуска воркера в другом сервисе"""

        worker = arq.Worker(
            functions=functions,
            max_jobs=self.max_jobs,
            health_check_interval=60,
            handle_signals=False,
            redis_pool=self.job_pool,
        )
        try:
            # запускаем воркер
            await worker.main()
        finally:
            # закрываем воркер
            await worker.close()

    async def delay(self, f: Callable, *args,
                    delay_by: datetime.timedelta | None = None,
                    delay_until: datetime.datetime | None = None, **kwargs):
        await self.job_pool.enqueue_job(
            f.__name__,
            *args,
            _defer_by=delay_by,
            _defer_until=delay_until,
            **kwargs
        )
