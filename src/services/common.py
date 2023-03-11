from elasticsearch import AsyncElasticsearch
from pydantic import BaseModel


class MixinService:
    def __init__(self, elastic: AsyncElasticsearch):
        self.elastic = elastic

    async def _get_by_id(
            self, id: str, model: BaseModel, es_index: str) -> BaseModel:
        doc = await self.elastic.get(es_index, id)
        return model(**doc['_source'])

    async def _get_by_search(
            self, search_string: str, search_field: str,
            es_index: str, model: BaseModel) -> list[BaseModel]:
        doc = await self.elastic.search(
            index=es_index,
            body={"query": {
                "match": {
                    search_field: {
                        "query": search_string,
                        "fuzziness": "auto"
                    }
                }
            }})
        return [model(**d['_source']) for d in doc['hits']['hits']]

    async def _get_list(
            self, page_number: int, page_size: int, es_index: str,
            model: BaseModel, query: dict = None) -> list[BaseModel]:
        body = {"from": page_number * page_size, "size": page_size}
        if query:
            body = body | query
        docs = await self.elastic.search(
            index=es_index,
            body=body
        )
        return [model(**d['_source']) for d in docs['hits']['hits']]
