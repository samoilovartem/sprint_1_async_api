from http import HTTPStatus
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query

from core.config import Config
from models.schemas import MovieDetail, MovieList
from services.movies import MovieService, get_service

router = APIRouter(prefix='/movies', tags=['Movies'])


@router.get(
    path='',
    name='Movies List',
    description='Get a list of all movies with optional filtering by genre and sorting by IMDb rating',
    response_model=list[MovieList],
    response_model_exclude_unset=True,
)
async def get_movies_list(
        sort: str = None,
        genre_id: UUID = None,
        page_number: int = Query(default=0, ge=0),
        page_size: int = Query(default=Config.PROJECT_GLOBAL_PAGE_SIZE, gt=0),
        movie_service: MovieService = Depends(get_service),
):
    if not sort:
        sort_field = 'imdb_rating'
        sort_type = 'desc'
    else:
        sort_field = 'imdb_rating' if sort.endswith('imdb_rating') else None
        if not sort_field:
            raise HTTPException(
                status_code=HTTPStatus.NOT_FOUND, detail='Invalid sorting field'
            )
        sort_type = 'desc' if sort.startswith('-') else 'asc'
    movies_list = await movie_service.get_sorted_movies(
        page_number=page_number,
        page_size=page_size,
        sort_field=sort_field,
        sort_type=sort_type,
        genre_id=genre_id,
    )
    if not movies_list:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail='No movies found')
    return [
        MovieList(id=movie.id, title=movie.title, imdb_rating=movie.imdb_rating)
        for movie in movies_list
    ]


@router.get(
    path='/search',
    name='Search Movies',
    description='Search for movies by title and paginate the results',
    response_model=list[MovieList],
    response_model_exclude_unset=True,
)
async def get_movies_by_search(
        query: str,
        page_number: int = Query(default=0, ge=0),
        page_size: int = Query(default=Config.PROJECT_GLOBAL_PAGE_SIZE, gt=0),
        movie_service: MovieService = Depends(get_service),
) -> list[MovieList]:
    movies_list = await movie_service.search_movies(query, page_number, page_size)
    if not movies_list:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail='No movies found')
    return [
        MovieList(id=movie.id, title=movie.title, imdb_rating=movie.imdb_rating)
        for movie in movies_list
    ]


@router.get(
    path='/{movie_id}',
    name='Movie Details',
    description='Get detailed information about a specific movie by its ID',
    response_model=MovieDetail,
    response_model_exclude_unset=True,
)
async def get_movie_details(
        movie_id: UUID, movie_service: MovieService = Depends(get_service)
) -> MovieDetail:
    movie = await movie_service.get_movie_by_id(movie_id)
    if not movie:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail='Movie not found')
    return movie


# @router.get(
#     path='/{movie_id}/similar',
#     name='Similar Movies',
#     description='Get a list of movies similar to the specified movie, based on genre',
#     response_model=list[MovieList],
#     response_model_exclude_unset=True,
# )
# async def get_similar_movies(
#         movie_id: UUID, movie_service: MovieService = Depends(get_service)
# ) -> list[MovieList]:
#     movies_list = await movie_service.get_similar(movie_id)
#     if not movies_list:
#         raise HTTPException(
#             status_code=HTTPStatus.NOT_FOUND, detail='No similar movies found'
#         )
#     return [
#         MovieList(id=movie.id, title=movie.title, imdb_rating=movie.imdb_rating)
#         for movie in movies_list
#     ]
#
#
# @router.get(
#     path='/genres/{genre_id}',
#     name='Popular Movies in Genre',
#     description='Get a list of the most popular movies in a specific genre',
#     response_model=list[MovieList],
#     response_model_exclude_unset=True,
# )
# async def get_popular_in_genre(
#         genre_id: UUID, movie_service: MovieService = Depends(get_service)
# ) -> list[MovieList]:
#     movies_list = await movie_service.get_popular_genre(genre_id)
#     if not movies_list:
#         raise HTTPException(
#             status_code=HTTPStatus.NOT_FOUND, detail='No movies found in the specified genre'
#         )
#     return [
#         MovieList(id=movie.id, title=movie.title, imdb_rating=movie.imdb_rating)
#         for movie in movies_list
#     ]
