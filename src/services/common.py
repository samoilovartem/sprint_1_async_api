from uuid import UUID

from pydantic import BaseModel

from core.config import Config
from data_services.cache import Cache
from data_services.database import Database


class MixinService:
    def __init__(self, cache: Cache, database: Database):
        self.cache = cache
        self.database = database

    async def get_by_id(
            self,
            id: UUID,
            model: BaseModel,
            es_index: str,
            cache_timeout: int = Config.REDIS_CACHE_TIMEOUT,
    ) -> BaseModel | None:
        data = await self.cache.get_by_id(id=id, model=model)
        if not data:
            data = await self.database.get_by_id(id=id, model=model, es_index=es_index)
            await self.cache.put_by_id(id=id, model=data, cache_timeout=cache_timeout)
        return data

    async def get_by_search(
            self,
            search_string: str,
            search_field: str,
            page_number: int,
            page_size: int,
            es_index: str,
            cache_timeout: int,
            model: BaseModel,
    ) -> list[BaseModel]:
        key = f'{es_index}:{search_string}:{search_field}:{page_number}:{page_size}'
        data = await self.cache.get_list(key=key, model=model)
        if not data:
            data = await self.database.search(search_string, search_field, page_number, page_size, es_index,
                                              model)
            await self.cache.put_list(key=key, data_list=data, cache_timeout=cache_timeout)
        return data

    async def get_list(
            self,
            page_number: int,
            page_size: int,
            cache_timeout: int,
            es_index: str,
            model: BaseModel,
    ) -> list[BaseModel] | None:
        key = f'{es_index}:{page_number}:{page_size}'
        data_list = await self.cache.get_list(key=key, model=model)
        if not data_list:
            data_list = await self.database.get_list(page_number, page_size, es_index, model)
            await self.cache.put_list(key=key, data_list=data_list, cache_timeout=cache_timeout)
        return data_list

    async def get_sorted_list(
            self,
            page_number: int,
            page_size: int,
            sort_field: str,
            sort_type: str,
            genre_id: UUID,
            es_index: str,
            cache_timeout: int,
            model: BaseModel,
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

        key = f'{sort_field}:{sort_type}:{genre_id}:{page_number}:{page_size}{es_index}'
        movies_list = await self.cache.get_list(key=key, model=model)

        if not movies_list:
            movies_list = await self.database.get_list(
                page_number=page_number,
                page_size=page_size,
                es_index=es_index,
                model=model,
                query=query,
            )
            await self.cache.put_list(
                key=key,
                data_list=movies_list,
                cache_timeout=cache_timeout
            )
        return movies_list


    # async def get_similar(
    #         self,
    #         movie_id: UUID,
    #         es_index: str,
    #         model: BaseModel,
    #         cache_timeout: int = Config.REDIS_CACHE_TIMEOUT,
    # ) -> Optional[list[BaseModel]]:
    #     key = f'similar:{movie_id}:{es_index}'
    #     movies_list = await self.cache.get(key)
    #     if not movies_list:
    #         movie = await self.get_by_id(id=movie_id, model=model, es_index=es_index)
    #         if not movie:
    #             return None
    #
    #         genres = movie.genres
    #
    #         search_body = {
    #             "query": {
    #                 "bool": {
    #                     "filter": [
    #                         {"terms": {"genres.id": [genre.id for genre in genres]}},
    #                         {"term": {"_id": str(movie_id)}}
    #                     ]
    #                 }
    #             },
    #             "size": 10,
    #         }
    #
    #         movies_list = await self.database.search_by_body(
    #             search_body=search_body, es_index=es_index, model=model
    #         )
    #
    #         await self.cache.set(key, movies_list, cache_timeout)
    #
    #     return movies_list
    #
    # async def get_popular_genre(
    #         self,
    #         genre_id: UUID,
    #         es_index: str,
    #         model: BaseModel,
    #         cache_timeout: int = Config.REDIS_CACHE_TIMEOUT,
    # ) -> list[BaseModel]:
    #     key = f'popular_genre:{genre_id}:{es_index}'
    #     movies_list = await self.cache.get(key)
    #     if not movies_list:
    #         search_body = {
    #             "query": {
    #                 "bool": {
    #                     "filter": [
    #                         {"term": {"genres.id": str(genre_id)}}
    #                     ]
    #                 }
    #             },
    #             "sort": [
    #                 {"imdb_rating": {"order": "desc"}}
    #             ],
    #             "size": 10,
    #         }
    #
    #         movies_list = await self.database.search_by_body(
    #             search_body=search_body, es_index=es_index, model=model
    #         )
    #
    #         await self.cache.set(key, movies_list, cache_timeout)
    #
    #     return movies_list
