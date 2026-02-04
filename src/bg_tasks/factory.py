from services.bg_tasks import ARQRedisBgTasks
from .notifications import NotificationsBgTasks


class BgTasksFactory:
    def __init__(self, bg_tasks_service: ARQRedisBgTasks):
        self.bg_tasks_service = bg_tasks_service

    @property
    def notifications(self):
        return NotificationsBgTasks(self.bg_tasks_service)

    async def start(self):
        await self.bg_tasks_service.connect()

    async def shutdown(self):
        await self.bg_tasks_service.disconnect()

    async def run(self):
        await self.bg_tasks_service.run(
            functions=self.notifications.functions
        )