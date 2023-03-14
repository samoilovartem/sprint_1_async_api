from http import HTTPStatus
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException

from models.schemas import GenreDetail
from services.genres import GenreService, get_service

router = APIRouter()


@router.get('/', response_model=list[GenreDetail],
            response_model_exclude_unset=True)
async def get_genres_list(page_number: int = 0,
                          page_size: int = 20,
                          genre_service: GenreService = Depends(
                              get_service)) -> list[GenreDetail]:
    genres_list = await genre_service.get_list(page_number=page_number,
                                               page_size=page_size)
    if not genres_list:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND,
                            detail='persons not found')
    return [GenreDetail(id=genre.id,
                        name=genre.name,
                        description=genre.description) for genre in genres_list]


@router.get('/{genre_id}', response_model=GenreDetail,
            response_model_exclude_unset=True)
async def genre_detail(genre_id: UUID,
                       genre_service: GenreService = Depends(
                           get_service)) -> GenreDetail:
    genre = await genre_service.get_by_id(genre_id)
    if not genre:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND,
                            detail='person not found')
    return GenreDetail(id=genre.id,
                       name=genre.name,
                       description=genre.description)
