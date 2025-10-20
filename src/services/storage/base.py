import abc
import os.path
from contextlib import asynccontextmanager, contextmanager

from typing_extensions import Self, AsyncGenerator, AsyncContextManager


class BaseStorageTransaction(abc.ABC):
    def __init__(self, storage: 'BaseStorage'):
        self.storage = storage
        self.__filepaths = []

    async def _close(self, with_exc: bool) -> None:
        if with_exc:
            for filename, folder in self.__filepaths:
                print(f'{filename=}')
                print(f'{folder=}')
                try:
                    await self.delete_file(filename, folder)
                except:
                    pass
        self.__filepaths.clear()

    async def save_file_get_url(self, file: bytes, filename: str | None = None,
                                folder: str | None = None,
                                replace_by_file_path: bool = False
                                ) -> str:

        self.__filepaths.append((filename, folder))
        return await self.storage.save_file_get_url(
            file, filename, folder, replace_by_file_path=replace_by_file_path
        )

    async def delete_file(self, filename: str | None = None, folder: str | None = None) -> None:
        await self.storage.delete_file(filename, folder)


class BaseStorage(abc.ABC):
    _on_transaction: bool = False

    @asynccontextmanager
    async def _start_transaction(self):
        self._on_transaction = True
        trans = BaseStorageTransaction(self)
        try:
            yield trans
        except Exception as e:
            self._on_transaction = False
            await trans._close(with_exc=True)
            raise e
        else:
            await trans._close(with_exc=False)
        finally:
            del trans

    def start_transaction(self) -> AsyncContextManager[BaseStorageTransaction]:
        return self._start_transaction()

    @abc.abstractmethod
    def create_url(self, filename: str, folder: str | None = None) -> str: ...
    @abc.abstractmethod
    def get_file_path(self, filename: str, folder: str | None = None) -> str: ...
    @abc.abstractmethod
    async def save_file_get_url(self, file: bytes, filename: str | None = None,
                                folder: str | None = None,
                                replace_by_file_path: bool = False) -> str: ...
    @abc.abstractmethod
    async def delete_file(self, filename: str | None = None, folder: str | None = None) -> None: ...