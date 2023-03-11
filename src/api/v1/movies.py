from http import HTTPStatus

from fastapi import APIRouter, Depends, HTTPException

from models.schemas import MovieList, MovieDetail
from services.movies import MovieService, get_movie_service

router = APIRouter()


@router.get('/', response_model=list[MovieDetail], response_model_exclude_unset=True)
async def movies_sorted(sort: str = None,
                        filter_genre: str = None,
                        page_number: int = 0,
                        page_size: int = 20,
                        movie_service: MovieService = Depends(get_movie_service)):
    if not sort:
        sort_field = 'imdb_rating'
        sort_type = 'desc'
    else:
        sort_field = 'imdb_rating' if sort.endswith('imdb_rating') else None
        if not sort_field:
            raise HTTPException(status_code=HTTPStatus.NOT_FOUND,
                                detail='sorting not found')
        sort_type = 'desc' if sort.startswith('-') else 'asc'
    movie_list = await movie_service.get_movie_sorted(
        sort_field=sort_field,
        sort_type=sort_type,
        filter_genre=filter_genre,
        page_number=page_number,
        page_size=page_size)
    if not movie_list:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND,
                            detail='movie not found')
    return [MovieList(id=movie.id,
                      title=movie.title,
                      imdb_rating=movie.imdb_rating) for movie in movie_list]


@router.get('/search/{movie_search_string}', response_model=list[MovieList],
            response_model_exclude_unset=True)
async def movies_search(movie_search_string: str,
                        movie_service: MovieService = Depends(
                            get_movie_service)) -> list[MovieList]:
    movie_list = await movie_service.get_movie_by_search(movie_search_string)
    if not movie_list:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND,
                            detail='movie not found')
    return [MovieList(id=movie.id,
                      title=movie.title,
                      imdb_rating=movie.imdb_rating) for movie in movie_list]


@router.get('/{movie_id}', response_model=MovieDetail,
            response_model_exclude_unset=True)
async def movie_details(movie_id: str,
                        movie_service: MovieService = Depends(
                            get_movie_service)) -> MovieDetail:
    movie = await movie_service.get_movie_by_id(movie_id)
    if not movie:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND,
                            detail='movie not found')
    return MovieDetail(id=movie.id,
                       imdb_rating=movie.imdb_rating,
                       genre=movie.genre,
                       title=movie.title,
                       description=movie.description,
                       director=movie.director,
                       actors_names=movie.actors_names,
                       writers_names=movie.writers_names,
                       actors=movie.actors,
                       writers=movie.writers)