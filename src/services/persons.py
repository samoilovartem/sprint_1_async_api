from functools import lru_cache
from typing import Optional
from uuid import UUID

from aioredis import Redis
from elasticsearch import AsyncElasticsearch
from fastapi import Depends
from pydantic import BaseModel

from core.config import REDIS_CACHE_TIMEOUT
from db.elastic import get_elastic
from db.redis import get_redis
from models.schemas import PersonDetail
from services.common import MixinService


class PersonService(MixinService):
    es_index = 'persons'
    model = PersonDetail

    async def get_by_id(self, person_id: UUID) -> Optional[PersonDetail]:
        return await self._get_by_id(
            id=person_id,
            model=self.model,
            es_index=self.es_index,
            cache_timout=REDIS_CACHE_TIMEOUT
        )

    async def get_list(
        self, page_number: int, page_size: int
    ) -> Optional[list[PersonDetail]]:
        return await self._get_list(
            page_number=page_number,
            page_size=page_size,
            es_index=self.es_index,
            model=self.model,
            cache_timout=REDIS_CACHE_TIMEOUT,
        )

    async def get_by_search(
        self, search_string: str, page_number: int, page_size: int
    ) -> list[BaseModel]:
        return await self._get_by_search(
            search_string=search_string,
            search_field='full_name',
            page_number=page_number,
            page_size=page_size,
            es_index=self.es_index,
            model=self.model,
            cache_timout=REDIS_CACHE_TIMEOUT,
        )


@lru_cache()
def get_service(
        redis: Redis = Depends(get_redis),
        elastic: AsyncElasticsearch = Depends(get_elastic)
) -> PersonService:
    return PersonService(redis=redis, elastic=elastic)
