import abc
from io import BytesIO
from typing import Callable

import aioboto3
from types_aiobotocore_s3.client import S3Client
from botocore.exceptions import ClientError
import asyncio

from types_aiobotocore_s3.type_defs import FileobjTypeDef


class S3Service:
    __session = None
    __client: S3Client | None = None

    def __init__(self,
                 endpoint_url: str,
                 aws_access_key_id: str,
                 aws_secret_access_key: str,
                 region_name: str,
                 bucket: str,
                 service_name: str = 's3',
                 max_retries: int = 3
                 ):
        self.__endpoint_url = endpoint_url
        self.__aws_access_key_id = aws_access_key_id
        self.__aws_secret_access_key = aws_secret_access_key
        self.__region_name = region_name
        self.__service_name = service_name
        self.__bucket_name = bucket
        self.__max_retries = max_retries

    async def __aenter__(self) -> 'S3Service':
        if self.__session and self.__client:
            return self

        self.__session = aioboto3.Session()
        self.__client = self.__session.client(
            endpoint_url=self.__endpoint_url,
            aws_access_key_id=self.__aws_access_key_id,
            aws_secret_access_key=self.__aws_secret_access_key,
            region_name=self.__region_name,
            service_name=self.__service_name
        )
        self.__client: S3Client = await self.__client.__aenter__()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        await self.__client.__aexit__(exc_type, exc_val, exc_tb)
        self.__session = None
        self.__client = None

    async def __do(self, func: Callable, *args, **kwargs):
        for attempt in range(self.__max_retries):
            try:
                await func(*args, **kwargs)
                return  # Успешно, выходим
            except ClientError as e:
                if e.response['Error']['Code'] == 'OperationAborted' and attempt < self.__max_retries - 1:
                    # Экспоненциальная задержка перед повторной попыткой
                    delay = (2 ** attempt) * 0.1
                    await asyncio.sleep(delay)
                    continue
                else:
                    raise Exception(f'S3 Error (Повторные попытки исчерпаны): {e}')

    async def set(self, key: str, value: str | bytes) -> None:
        await self.__do(
            self.__client.put_object,
            Bucket=self.__bucket_name,
            Key=key,
            Body=value
        )

    async def upload_fileobj(self, key: str, fileobj: FileobjTypeDef) -> None:
        await self.__do(
            self.__client.upload_fileobj,
            Fileobj=fileobj,
            Bucket=self.__bucket_name,
            Key=key
        )

    async def get(self, key: str) -> str | bytes:
        await self.__do(
            self.__client.get_object,
            Bucket=self.__bucket_name, Key=key
        )

    async def delete(self, key: str) -> None:
        await self.__do(
            self.__client.put_object,
            Bucket=self.__bucket_name,
            Key=key,
            Body=None
        )


class ManagerS3ABC(abc.ABC):
    def __init__(self, s3: S3Service):
        self.s3 = s3

    async def __aenter__(self) -> 'ManagerS3ABC':
        await self.s3.__aenter__()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.s3.__aexit__(exc_type, exc_val, exc_tb)

    async def delete(self, key: str) -> None:
        await self.s3.delete(key)


class TextManagerS3(ManagerS3ABC):
    async def set(self, key: str, text: str) -> str:
        await self.s3.set(key, text)
        return key

    async def get(self, key: str) -> str:
        return (await self.s3.get(key)).decode('utf-8')


class FilesManagerS3(ManagerS3ABC):
    async def set(self, key: str, file: bytes) -> str:
        await self.s3.upload_fileobj(key, BytesIO(file))
        return key

    async def get(self, key: str) -> bytes:
        return await self.s3.get(key)