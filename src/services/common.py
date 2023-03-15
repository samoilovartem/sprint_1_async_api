import json
from uuid import UUID

from aioredis import Redis
from elasticsearch import AsyncElasticsearch, NotFoundError
from pydantic import BaseModel, parse_raw_as
from pydantic.json import pydantic_encoder

from core.config import REDIS_CACHE_TIMEOUT


class MixinService:
    def __init__(self, redis: Redis, elastic: AsyncElasticsearch):
        self.redis = redis
        self.elastic = elastic

    async def _get_by_id(
            self, id: UUID, model: BaseModel, es_index: str,
            cache_timout: int = REDIS_CACHE_TIMEOUT
    ) -> BaseModel | None:
        data = await self._get_by_id_with_cache(id, model)
        if not data:
            data = await self._get_by_id_with_elastic(id, model, es_index)
            if data:
                await self._put_by_id_into_cache(data, cache_timout)
        return data

    async def _get_by_id_with_elastic(
            self, id: UUID, model: BaseModel, es_index: str
    ) -> BaseModel | None:
        try:
            doc = await self.elastic.get(index=es_index, id=id)
        except NotFoundError:
            return None
        return model(**doc['_source'])

    async def _get_by_search(
            self,
            search_string: str,
            search_field: str,
            page_number: int,
            page_size: int,
            es_index: str,
            cache_timout: int,
            model: BaseModel,
    ) -> list[BaseModel]:
        data = await self._get_from_cache(
            key=f'{es_index}:{search_string}:{search_field}',
            model=model,
        )
        if not data:
            data_list = await self._get_by_search_with_elastic(
                search_string, search_field, page_number, page_size, es_index, model
            )
            await self._put_into_cache(
                key=f'{es_index}:{search_string}:{search_field}',
                data_list=data_list,
                cache_timout=cache_timout,
            )
            return data_list

    async def _get_by_search_with_elastic(
            self,
            search_string: str,
            search_field: str,
            page_number: int,
            page_size: int,
            es_index: str,
            model: BaseModel
    ) -> list[BaseModel]:
        body = {"from": page_number * page_size, "size": page_size}
        query = {
            "query": {
                "match": {search_field: {"query": search_string, "fuzziness": "auto"}}
            }
        }
        doc = await self.elastic.search(index=es_index, body=body | query)
        return [model(**d['_source']) for d in doc['hits']['hits']]

    async def _get_list(
            self,
            page_number: int,
            page_size: int,
            cache_timout: int,
            es_index: str,
            model: BaseModel,
    ) -> list[BaseModel] | None:
        data_list = await self._get_from_cache(
            key=f'{es_index}:{page_number}:{page_size}', model=model
        )
        if not data_list:
            data_list = await self._get_list_with_elastic(page_number,
                                                          page_size,
                                                          es_index,
                                                          model)
            await self._put_into_cache(
                key=f'{es_index}:{page_number}:{page_size}',
                data_list=data_list, cache_timout=cache_timout
            )
        return data_list

    async def _get_list_with_elastic(
            self,
            page_number: int,
            page_size: int,
            es_index: str,
            model: BaseModel,
            query: dict = None
    ) -> list[BaseModel]:
        body = {"from": page_number * page_size, "size": page_size}
        if query:
            body = body | query
        docs = await self.elastic.search(
            index=es_index,
            body=body
        )
        return [model(**d['_source']) for d in docs['hits']['hits']]

    async def _get_by_id_with_cache(
            self, id: UUID, model: BaseModel) -> BaseModel | None:
        data = await self.redis.get(id)
        if not data:
            return None
        return model.parse_raw(data)

    async def _put_by_id_into_cache(self, model: BaseModel, cache_timeout: int):
        await self.redis.set(model.id, model.json(), expire=cache_timeout)

    async def _put_into_cache(self,
                              data_list: list[BaseModel],
                              cache_timout: int, key: str
                              ) -> None:
        list_json = json.dumps(data_list, default=pydantic_encoder)
        await self.redis.set(key, list_json, expire=cache_timout)

    async def _get_from_cache(
            self,
            key: str,
            model: BaseModel
    ) -> list[BaseModel] | None:
        data = await self.redis.get(key)
        if not data:
            return None
        return parse_raw_as(list[model], data)
