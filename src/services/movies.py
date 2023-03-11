from functools import lru_cache
from typing import Optional

from elasticsearch import AsyncElasticsearch
from fastapi import Depends

from db.elastic import get_elastic
from models.schemas import MovieDetail
from services.common import MixinService


class MovieService(MixinService):
    es_index = 'movies'
    model = MovieDetail

    async def get_movie_by_id(self, movie_id: str) -> Optional[MovieDetail]:
        return await self._get_by_id(movie_id, self.model, self.es_index)

    async def get_movie_by_search(
            self, search_string: str) -> Optional[list[MovieDetail]]:
        return await self._get_by_search(search_string, 'title',
                                         self.es_index, self.model)

    async def get_movie_sorted(
            self, sort_field: str, sort_type: str, filter_genre: str,
            page_number: int, page_size: int) -> Optional[list[MovieDetail]]:
        query = {"sort": {sort_field: sort_type}}
        if filter_genre:
            query = query | {
                "query": {"match": {"genre.id": {"query": filter_genre}}}}
        movie_list = await self._get_list(page_number,
                                          page_size,
                                          self.es_index,
                                          self.model,
                                          query=query)
        if not movie_list:
            return None
        return movie_list


def get_movie_service(
        elastic: AsyncElasticsearch = Depends(get_elastic)) -> MovieService:
    return MovieService(elastic)
