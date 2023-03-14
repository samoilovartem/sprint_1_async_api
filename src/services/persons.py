from typing import Optional
from uuid import UUID

from elasticsearch import AsyncElasticsearch
from fastapi import Depends

from db.elastic import get_elastic
from models.schemas import PersonDetail
from services.common import MixinService


class PersonService(MixinService):
    es_index = 'persons'
    model = PersonDetail

    async def get_by_id(self, person_id: UUID) -> Optional[PersonDetail]:
        return await self._get_by_id(person_id, self.model, self.es_index)

    async def get_list(
            self, page_number: int, page_size: int) -> Optional[list[PersonDetail]]:
        return await self._get_list(page_number, page_size, self.es_index, self.model)

    async def get_by_search(
            self, search_string: str) -> Optional[list[PersonDetail]]:
        return await self._get_by_search(search_string, 'full_name', self.es_index, self.model)


def get_service(elastic: AsyncElasticsearch = Depends(get_elastic)) -> PersonService:
    return PersonService(elastic)
