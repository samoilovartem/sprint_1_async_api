from functools import lru_cache
from typing import Optional
from uuid import UUID

from aioredis import Redis
from elasticsearch import AsyncElasticsearch
from fastapi import Depends

from core.config import REDIS_CACHE_TIMEOUT
from db.elastic import get_elastic
from db.redis import get_redis
from models.schemas import GenreDetail
from services.common import MixinService


class GenreService(MixinService):
    es_index = 'genres'
    model = GenreDetail

    async def get_by_id(self, genre_id: UUID) -> Optional[GenreDetail]:
        return await self._get_by_id(
            id=genre_id,
            model=self.model,
            es_index=self.es_index,
            cache_timout=REDIS_CACHE_TIMEOUT,
        )

    async def get_list(
        self, page_number: int, page_size: int
    ) -> Optional[list[GenreDetail]]:
        return await self._get_list(
            page_number=page_number,
            page_size=page_size,
            cache_timout=REDIS_CACHE_TIMEOUT,
            es_index=self.es_index,
            model=self.model,
        )


@lru_cache()
def get_service(
    redis: Redis = Depends(get_redis),
    elastic: AsyncElasticsearch = Depends(get_elastic),
) -> GenreService:
    return GenreService(redis=redis, elastic=elastic)
