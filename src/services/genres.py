from functools import lru_cache
from typing import Optional
from uuid import UUID

from aioredis import Redis
from elasticsearch import AsyncElasticsearch
from fastapi import Depends
from pydantic import BaseModel

from core.config import Config
from data_services.cache import RedisCache, Cache
from data_services.database import ElasticSearch, Database
from db.elastic import get_elastic
from db.redis import get_redis
from models.schemas import GenreDetail
from services.common import MixinService


class GenreService(MixinService):
    def __init__(self, cache: Cache, database: Database):
        super().__init__(cache, database)
        self.es_index = 'genres'
        self.model = GenreDetail

    async def get_genre_by_id(self, genre_id: UUID) -> Optional[GenreDetail]:
        return await self.get_by_id(
            id=genre_id,
            model=self.model,
            es_index=self.es_index,
            cache_timeout=Config.REDIS_CACHE_TIMEOUT
        )

    async def get_genres_list(
        self, page_number: int, page_size: int
    ) -> Optional[list[GenreDetail]]:
        return await self.get_list(
            page_number=page_number,
            page_size=page_size,
            es_index=self.es_index,
            model=self.model,
            cache_timeout=Config.REDIS_CACHE_TIMEOUT,
        )

    async def get_genres_by_search(
        self, search_string: str, page_number: int, page_size: int
    ) -> list[BaseModel]:
        return await self.get_by_search(
            search_string=search_string,
            search_field='name',
            page_number=page_number,
            page_size=page_size,
            es_index=self.es_index,
            model=self.model,
            cache_timeout=Config.REDIS_CACHE_TIMEOUT,
        )


@lru_cache()
def get_service(
    redis: Redis = Depends(get_redis),
    elastic: AsyncElasticsearch = Depends(get_elastic),
) -> GenreService:
    redis_cache = RedisCache(redis)
    async_elastic_search = ElasticSearch(elastic)
    return GenreService(cache=redis_cache, database=async_elastic_search)
