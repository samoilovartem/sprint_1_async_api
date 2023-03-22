from http import HTTPStatus
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query

from core.config import Config
from models.schemas import PersonDetail
from services.persons import PersonService, get_service

router = APIRouter(prefix='/persons', tags=['Persons'])


@router.get(
    path='',
    name='Persons List',
    description='Get a list of all persons involved in the movies, with optional pagination',
    response_model=list[PersonDetail],
    response_model_exclude_unset=True,
)
async def get_persons_list(
    page_number: int = Query(default=0, ge=0),
    page_size: int = Query(default=Config.PROJECT_GLOBAL_PAGE_SIZE, gt=0),
    person_service: PersonService = Depends(get_service),
) -> list[PersonDetail]:

    """Get a list of all persons involved in the movies, with optional pagination."""

    persons_list = await person_service.get_persons_list(
        page_number=page_number, page_size=page_size
    )
    if not persons_list:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail='No persons found'
        )
    return [
        PersonDetail(
            id=person.id,
            full_name=person.full_name,
            roles=person.roles,
            movies_ids=person.movies_ids,
        )
        for person in persons_list
    ]


@router.get(
    path='/search',
    name='Search Persons',
    description='Search for persons involved in the movies by their name',
    response_model=list[PersonDetail],
    response_model_exclude_unset=True
)
async def get_persons_by_search(
    query: str,
    page_number: int = Query(default=0, ge=0),
    page_size: int = Query(default=Config.PROJECT_GLOBAL_PAGE_SIZE, gt=0),
    person_service: PersonService = Depends(get_service),
) -> list[PersonDetail]:

    """Search for persons involved in the movies by their name."""

    persons_list = await person_service.get_persons_by_search(query, page_number, page_size)
    if not persons_list:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail='No persons found'
        )
    return [
        PersonDetail(
            id=person.id,
            full_name=person.full_name,
            roles=person.roles,
            movies_ids=person.movies_ids,
        )
        for person in persons_list
    ]


@router.get(
    path='/{person_id}',
    name='Person Details',
    description='Get detailed information about a specific person by their ID',
    response_model=PersonDetail,
    response_model_exclude_unset=True,
)
async def get_person_detail(
    person_id: UUID, person_service: PersonService = Depends(get_service)
) -> PersonDetail:

    """Get detailed information about a specific person by their ID."""

    person = await person_service.get_person_by_id(person_id)
    if not person:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail='Person not found')
    return PersonDetail(
        id=person.id,
        full_name=person.full_name,
        roles=person.roles,
        movies_ids=person.movies_ids,
    )
