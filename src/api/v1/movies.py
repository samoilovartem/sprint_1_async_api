from http import HTTPStatus
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException

from models.schemas import MovieList, MovieDetail
from services.movies import MovieService, get_service

router = APIRouter()


@router.get('', response_model=list[MovieDetail],
            response_model_exclude_unset=True,
            description="Get a list of all movies with "
                        "optional filtering by genre")
async def get_movies_list(sort: str = None,
                          genre_id: UUID = None,
                          page_number: int = 0,
                          page_size: int = 20,
                          movie_service: MovieService = Depends(get_service)):
    if not sort:
        sort_field = 'imdb_rating'
        sort_type = 'desc'
    else:
        sort_field = 'imdb_rating' if sort.endswith('imdb_rating') else None
        if not sort_field:
            raise HTTPException(status_code=HTTPStatus.NOT_FOUND,
                                detail='Sorting not found')
        sort_type = 'desc' if sort.startswith('-') else 'asc'
    movies_list = await movie_service.get_sorted(
        sort_field=sort_field,
        sort_type=sort_type,
        genre_id=genre_id,
        page_number=page_number,
        page_size=page_size)
    if not movies_list:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND,
                            detail='Movie not found')
    return [MovieList(id=movie.id,
                      title=movie.title,
                      imdb_rating=movie.imdb_rating) for movie in movies_list]


@router.get('/search', response_model=list[MovieList],
            response_model_exclude_unset=True,
            description="Search movies by title")
async def get_movies_by_search(query: str,
                               page_number: int = 0,
                               page_size: int = 20,
                               movie_service: MovieService = Depends(
                                   get_service)) -> list[MovieList]:
    movies_list = await movie_service.get_by_search(query, page_number, page_size)
    if not movies_list:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND,
                            detail='Movie not found')
    return [MovieList(id=movie.id,
                      title=movie.title,
                      imdb_rating=movie.imdb_rating) for movie in movies_list]


@router.get('/{movie_id}', response_model=MovieDetail,
            response_model_exclude_unset=True,
            description="Get a detailed movie description")
async def get_movie_details(movie_id: UUID,
                            movie_service: MovieService = Depends(
                                get_service)) -> MovieDetail:
    movie = await movie_service.get_by_id(movie_id)
    if not movie:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND,
                            detail='Movie not found')
    return MovieDetail(id=movie.id,
                       imdb_rating=movie.imdb_rating,
                       genres=movie.genres,
                       title=movie.title,
                       description=movie.description,
                       directors=movie.directors,
                       actors=movie.actors,
                       writers=movie.writers)


@router.get('/{movie_id}/similar', response_model=list[MovieList],
            response_model_exclude_unset=True,
            description="Get similar movies (the current implementation "
                        "gets movies of the same genre)")
async def get_similar_movies(movie_id: UUID,
                             movie_service: MovieService = Depends(
                                 get_service)) -> list[MovieList]:
    movies_list = await movie_service.get_similar(movie_id)
    if not movies_list:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND,
                            detail='Similar movies not found')
    return [MovieList(id=movie.id,
                      title=movie.title,
                      imdb_rating=movie.imdb_rating) for movie in movies_list]


@router.get('/genres/{genre_id}', response_model=list[MovieList],
            response_model_exclude_unset=True,
            description="Get popular movies in the genre")
async def get_popular_in_genre(genre_id: UUID,
                               movie_service: MovieService = Depends(
                                   get_service)) -> list[MovieList]:
    movies_list = await movie_service.get_popular_genre(genre_id)
    if not movies_list:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND,
                            detail='Movies of genre not found')
    return [MovieList(id=movie.id,
                      title=movie.title,
                      imdb_rating=movie.imdb_rating) for movie in movies_list]
