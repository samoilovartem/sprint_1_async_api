from functools import lru_cache
from typing import Optional
from uuid import UUID

from aioredis import Redis
from elasticsearch import AsyncElasticsearch
from fastapi import Depends
from pydantic import BaseModel

from core.config import REDIS_CACHE_TIMEOUT, PROJECT_GLOBAL_PAGE_SIZE
from db.elastic import get_elastic
from db.redis import get_redis
from models.schemas import MovieDetail
from services.common import MixinService


class MovieService(MixinService):
    es_index = 'movies'
    model = MovieDetail

    async def get_by_id(self, movie_id: UUID) -> Optional[MovieDetail]:
        return await self._get_by_id(
            id=movie_id,
            model=self.model,
            es_index=self.es_index,
            cache_timout=REDIS_CACHE_TIMEOUT,
        )

    async def get_by_search(
        self, search_string: str, page_number: int, page_size: int
    ) -> list[BaseModel]:
        return await self._get_by_search(
            search_string=search_string,
            search_field='title',
            page_number=page_number,
            page_size=page_size,
            es_index=self.es_index,
            model=self.model,
            cache_timout=REDIS_CACHE_TIMEOUT,
        )

    async def get_sorted(
        self,
        sort_field: str,
        sort_type: str,
        genre_id: UUID,
        page_number: int,
        page_size: int,
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

        movies_list = await self._get_from_cache(
            key=f'{sort_field}:{sort_type}:{genre_id}:{self.es_index}',
            model=self.model
        )

        if not movies_list:
            movies_list = await self._get_list_with_elastic(
                page_number=page_number,
                page_size=page_size,
                es_index=self.es_index,
                model=self.model,
                query=query,
            )
            await self._put_into_cache(
                key=f'{sort_field}:{sort_type}:{genre_id}:{self.es_index}',
                data_list=movies_list,
                cache_timout=REDIS_CACHE_TIMEOUT,
            )
        return movies_list

    async def get_similar_with_cache(self, movie_id: UUID) -> Optional[list[MovieDetail]]:
        movies_list = await self._get_from_cache(
            key=f'similar:{movie_id}:{self.es_index}',
            model=self.model
        )
        if not movies_list:
            movies_list = await self.get_similar_with_elastic(movie_id)
            await self._put_into_cache(
                key=f'similar:{movie_id}:{self.es_index}',
                data_list=movies_list,
                cache_timout=REDIS_CACHE_TIMEOUT,
            )
        return movies_list

    async def get_similar_with_elastic(self, movie_id: UUID) -> Optional[list[MovieDetail]]:
        movie = await self.get_by_id(movie_id)
        if not movie or not movie.genres:
            return None
        data = []
        for genre in movie.genres:
            similar_movies = await self.get_sorted(
                sort_field='imdb_rating',
                sort_type='desc',
                genre_id=genre.id,
                page_number=0,
                page_size=PROJECT_GLOBAL_PAGE_SIZE,
            )
            if similar_movies:
                data.extend(similar_movies)
        return data
    
    async def get_popular_genre_with_cache(self, genre_id: UUID) -> list[MovieDetail]:
        movies_list = await self._get_from_cache(
            key=f'popular_genre:{genre_id}:{self.es_index}',
            model=self.model
        )
        if not movies_list:
            movies_list = await self.get_popular_genre_with_elastic(genre_id)
            await self._put_into_cache(
                key=f'popular_genre:{genre_id}:{self.es_index}',
                data_list=movies_list,
                cache_timout=REDIS_CACHE_TIMEOUT,
            )
        return movies_list

    async def get_popular_genre_with_elastic(self, genre_id: UUID) -> list[MovieDetail]:
        movies_list = await self.get_sorted(
            sort_field='imdb_rating',
            sort_type='desc',
            genre_id=genre_id,
            page_number=0,
            page_size=PROJECT_GLOBAL_PAGE_SIZE,
        )
        return movies_list
    
    

@lru_cache()
def get_service(
    redis: Redis = Depends(get_redis),
    elastic: AsyncElasticsearch = Depends(get_elastic),
) -> MovieService:
    return MovieService(redis=redis, elastic=elastic)
