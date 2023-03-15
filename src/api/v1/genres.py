from http import HTTPStatus
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query

from models.schemas import GenreDetail
from services.genres import GenreService, get_service

router = APIRouter()


@router.get(
    '',
    response_model=list[GenreDetail],
    response_model_exclude_unset=True,
    description="Get a list of all genres with pagination",
)
async def get_genres_list(
    page_number: int = Query(default=0, ge=0),
    page_size: int = Query(default=20, gt=0),
    genre_service: GenreService = Depends(get_service),
) -> list[GenreDetail]:
    genres_list = await genre_service.get_list(
        page_number=page_number, page_size=page_size
    )
    if not genres_list:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail='Genres not found')
    return [
        GenreDetail(id=genre.id, name=genre.name, description=genre.description)
        for genre in genres_list
    ]


@router.get(
    '/{genre_id}',
    response_model=GenreDetail,
    response_model_exclude_unset=True,
    description="Get a detailed genre description",
)
async def get_genre_detail(
    genre_id: UUID, genre_service: GenreService = Depends(get_service)
) -> GenreDetail:
    genre = await genre_service.get_by_id(genre_id)
    if not genre:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail='Genre not found')
    return GenreDetail(id=genre.id, name=genre.name, description=genre.description)
