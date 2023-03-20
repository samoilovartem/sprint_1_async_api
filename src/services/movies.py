from functools import lru_cache
from typing import Optional
from uuid import UUID

from fastapi import Depends
from pydantic import BaseModel

from core.config import Config
from data_services.cache import RedisCache, Cache
from data_services.database import ElasticSearch, Database
from db.elastic import get_elastic
from db.redis import get_redis
from models.schemas import MovieDetail
from models.utils_schemas import MovieSortingType
from services.common import MixinService


class MovieService(MixinService):
    def __init__(self, cache: Cache, database: Database):
        super().__init__(cache, database)
        self.es_index = 'movies'
        self.model = MovieDetail

    async def get_movie_by_id(self, movie_id: UUID) -> Optional[MovieDetail]:
        return await self.get_by_id(
            id=movie_id,
            model=self.model,
            es_index=self.es_index,
            cache_timeout=Config.REDIS_CACHE_TIMEOUT,
        )

    async def search_movies(self, search_string: str, page_number: int, page_size: int) -> list[BaseModel]:
        return await self.get_by_search(
            search_string=search_string,
            search_field='title',
            page_number=page_number,
            page_size=page_size,
            es_index=self.es_index,
            model=self.model,
            cache_timeout=Config.REDIS_CACHE_TIMEOUT,
        )

    async def get_sorted_movies(
            self,
            page_number: int,
            page_size: int,
            sort_field: str,
            sort_type: str,
            genre_id: UUID,
    ) -> list[BaseModel] | None:
        query = {"sort": {sort_field: sort_type}}
        genre_query = {
            "query": {
                "nested": {
                    "path": "genres",
                    "query": {"bool": {"must": [{"match": {"genres.id": genre_id}}]}},
                }
            }
        }
        if genre_id:
            query = query | genre_query

        key = f'{sort_field}:{sort_type}:{genre_id}:{page_number}:{page_size}:{self.es_index}'
        movies_list = await self.cache.get_list(key=key, model=self.model)

        if not movies_list:
            movies_list = await self.database.get_list(
                page_number=page_number,
                page_size=page_size,
                es_index=self.es_index,
                model=self.model,
                query=query,
            )
            await self.cache.put_list(
                key=key,
                data_list=movies_list,
                cache_timeout=Config.REDIS_CACHE_TIMEOUT
            )
        return movies_list

    # async def get_similar(self, movie_id: UUID) -> Optional[list[MovieDetail]]:
    #     return await super().get_similar(
    #         movie_id=movie_id,
    #         es_index=self.es_index,
    #         model=self.model
    #     )
    #
    # async def get_popular_genre(self, genre_id: UUID) -> list[BaseModel]:
    #     return await super().get_popular_genre(
    #         genre_id=genre_id,
    #         es_index=self.es_index,
    #         model=self.model
    #     )


@lru_cache()
def get_service(
    redis=Depends(get_redis),
    elastic=Depends(get_elastic),
) -> MovieService:
    redis_cache = RedisCache(redis)
    async_elastic_search = ElasticSearch(elastic)
    return MovieService(cache=redis_cache, database=async_elastic_search)
