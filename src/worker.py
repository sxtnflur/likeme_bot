import asyncio
from depends import bg_tasks_factory


async def start():
    await bg_tasks_factory.start()
    await bg_tasks_factory.run()
    await bg_tasks_factory.shutdown()

if __name__ == '__main__':
    asyncio.run(start())