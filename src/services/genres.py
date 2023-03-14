from typing import Optional
from uuid import UUID

from elasticsearch import AsyncElasticsearch
from fastapi import Depends

from db.elastic import get_elastic
from models.schemas import GenreDetail
from services.common import MixinService


class GenreService(MixinService):
    es_index = 'genres'
    model = GenreDetail

    async def get_by_id(self, genre_id: UUID) -> Optional[GenreDetail]:
        return await self._get_by_id(genre_id, self.model, self.es_index)

    async def get_list(
            self, page_number: int, page_size: int) -> Optional[list[GenreDetail]]:
        return await self._get_list(page_number, page_size, self.es_index, self.model)


def get_service(elastic: AsyncElasticsearch = Depends(get_elastic)) -> GenreService:
    return GenreService(elastic)
