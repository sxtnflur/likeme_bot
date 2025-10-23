import abc
import os.path
import time
from contextlib import asynccontextmanager, contextmanager
from pathlib import Path
from urllib.parse import urljoin
import re

from typing_extensions import Self, AsyncGenerator, AsyncContextManager


class BaseStorageTransaction(abc.ABC):
    def __init__(self, storage: 'BaseStorage'):
        self.storage = storage
        self.__filepaths = []

    async def close(self, with_exc: bool) -> None:
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
                                by_file_path: Path | None = None,
                                replace_by_file_path: bool = False
                                ) -> str:
        self.__filepaths.append((filename, folder))
        return await self.storage.save_file_get_url(
            file, filename, folder, by_file_path=by_file_path, replace_by_file_path=replace_by_file_path
        )

    async def delete_file(self, filename: str | None = None, folder: str | None = None) -> None:
        await self.storage.delete_file(filename, folder)


class BaseStorage(abc.ABC):
    _on_transaction: bool = False

    def __init__(self, base_url: str, base_path: str = ''):
        self.base_url = base_url
        self.base_path = base_path

    @asynccontextmanager
    async def _start_transaction(self):
        self._on_transaction = True
        await self._on_start_transaction()
        trans = BaseStorageTransaction(self)

        try:
            yield trans
        except Exception as e:
            self._on_transaction = False
            await trans.close(with_exc=True)
            await self._on_close_transaction(exc=e)
            raise e
        else:
            await trans.close(with_exc=False)
            await self._on_close_transaction(exc=None)
        finally:
            del trans

    def start_transaction(self) -> AsyncContextManager[BaseStorageTransaction]:
        return self._start_transaction()

    def get_file_path(self, filename: str, folder: str | None = None) -> Path:
        folder = folder or './'
        path = Path(folder)
        return path.joinpath(filename)

    def create_url(self, file_path: Path) -> str:
        file_path = file_path.__str__()
        file_path = file_path.replace('\\', '/')
        file_path = re.sub(r'^/+', '/', file_path)
        return urljoin(self.base_url.rstrip('/') + '/', file_path.lstrip('/'))

    async def _on_start_transaction(self) -> None:
        pass

    async def _on_close_transaction(self, exc: Exception | None = None) -> None:
        pass

    @abc.abstractmethod
    async def _save_file_get_url(self, file: bytes, file_path: Path) -> None: ...

    async def save_file_get_url(self, file: bytes, filename: str | None = None,
                                folder: str | None = None,
                                by_file_path: Path | None = None,
                                replace_by_file_path: bool = False) -> str:
        if by_file_path:
            file_path = by_file_path
        else:
            filename = '-'.join(filename.split())
            print(f'{replace_by_file_path=}')
            if not replace_by_file_path:
                filename = f'{round(time.time())}_' + filename
            file_path = self.get_file_path(filename, folder)
            print(f'{file_path=}')
        await self._save_file_get_url(file, file_path)
        return self.create_url(file_path)

    @abc.abstractmethod
    async def _delete_file(self, file_path: Path) -> None: ...

    async def delete_file(self, filename: str | None = None, folder: str | None = None) -> None:
        file_path = self.get_file_path(filename, folder)
        return await self._delete_file(file_path)
