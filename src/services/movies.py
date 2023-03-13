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

    async def get_movies_by_search(
            self, search_string: str) -> Optional[list[MovieDetail]]:
        return await self._get_by_search(search_string, 'title',
                                         self.es_index, self.model)

    async def get_movies_sorted(
            self, sort_field: str, sort_type: str, filter_genre: str,
            page_number: int, page_size: int) -> Optional[list[MovieDetail]]:
        query = {"sort": {sort_field: sort_type}}
        if filter_genre:
            query = query | {
                "query": {"match": {"genres.id": {"query": filter_genre}}}}
        movies_list = await self._get_list(page_number,
                                           page_size,
                                           self.es_index,
                                           self.model,
                                           query=query)
        if not movies_list:
            return None
        return movies_list

    async def get_similar_movies(
            self, movie_id: str) -> Optional[list[MovieDetail]]:
        movie = await self.get_movie_by_id(movie_id)
        if not movie or not movie.genres:
            return None
        result = []
        for genre in movie.genres:
            similar_movies = await self.get_movies_sorted(
                sort_field='imdb_rating',
                sort_type='desc',
                filter_genre=genres.id,
                page_number=0,
                page_size=10)
            if similar_movies:
                result.extend(similar_movies)
        return result

    async def get_popular_genre_movies(self, genre_id: str, ) -> list[MovieDetail]:
        movies_list = await self.get_movies_sorted(sort_field='imdb_rating',
                                                   sort_type='desc',
                                                   filter_genre=genre_id,
                                                   page_number=0,
                                                   page_size=30)
        return movies_list


def get_movie_service(
        elastic: AsyncElasticsearch = Depends(get_elastic)) -> MovieService:
    return MovieService(elastic)
