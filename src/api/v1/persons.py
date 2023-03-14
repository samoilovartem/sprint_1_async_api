from http import HTTPStatus
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException

from models.schemas import PersonDetail
from services.persons import PersonService, get_service

router = APIRouter()


@router.get(
    '',
    response_model=list[PersonDetail],
    response_model_exclude_unset=True,
    description="Get a list of all persons",
)
async def get_persons_list(
    page_number: int = 0,
    page_size: int = 20,
    person_service: PersonService = Depends(get_service),
) -> list[PersonDetail]:
    persons_list = await person_service.get_list(
        page_number=page_number, page_size=page_size
    )
    if not persons_list:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail='Persons not found'
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
    '/search', response_model=list[PersonDetail], response_model_exclude_unset=True
)
async def get_persons_by_search(
    query: str,
    page_number: int = 0,
    page_size: int = 20,
    person_service: PersonService = Depends(get_service),
) -> list[PersonDetail]:
    persons_list = await person_service.get_by_search(query, page_number, page_size)
    if not persons_list:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail='Persons not found'
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
    '/{person_id}',
    response_model=PersonDetail,
    response_model_exclude_unset=True,
    description="Get a detailed person description",
)
async def get_person_detail(
    person_id: UUID, person_service: PersonService = Depends(get_service)
) -> PersonDetail:
    person = await person_service.get_by_id(person_id)
    if not person:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail='Person not found')
    return PersonDetail(
        id=person.id,
        full_name=person.full_name,
        roles=person.roles,
        movies_ids=person.movies_ids,
    )
