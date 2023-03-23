import pytest
from http import HTTPStatus

from tests.functional.utils.schemas import MovieDetail
from tests.functional.utils.helpers import extract_movies, extract_movie, extract_payload


@pytest.fixture(scope='session')
async def load_testing_movies_data(es_client):
    index = 'movies'
    payload = await extract_payload('movies.json', MovieDetail, index)
    await es_client.bulk(body=payload[0], index=index, refresh=True)
    yield
    await es_client.bulk(body=payload[1], index=index, refresh=True)


@pytest.mark.asyncio
async def test_general_movies_list(make_get_request,
                                   load_testing_movies_data,
                                   redis_client):
    response = await make_get_request('movies?sort=-imdb_rating')
    movies = await extract_movies(response)
    cache = await redis_client.get('movies:imdb_rating:desc:None:0:20')
    assert response.status == HTTPStatus.OK
    assert len(movies) > 0
    assert cache


@pytest.mark.asyncio
async def test_movies_search_via_id(make_get_request, redis_client):
    response_movies = await make_get_request('movies?sort=-imdb_rating')
    movies_list = await extract_movies(response_movies)
    movie_id = movies_list[0].id
    response = await make_get_request(f'movies/{movie_id}')
    movie = await extract_movie(response)
    cache = await redis_client.get(f'{movie_id}')
    assert response_movies.status == HTTPStatus.OK
    assert response.status == HTTPStatus.OK
    assert movie.id == movie_id
    assert cache


@pytest.mark.asyncio
async def test_movies_list_asc_sorting(make_get_request, redis_client):
    response = await make_get_request('movies?sort=imdb_rating')
    movies = await extract_movies(response)
    cache = await redis_client.get('movies:imdb_rating:asc:None:0:20')
    assert response.status == HTTPStatus.OK
    assert len(movies) > 1
    assert movies[0].imdb_rating <= movies[1].imdb_rating
    assert cache


@pytest.mark.asyncio
async def test_movies_list_desc_sorting(make_get_request, redis_client):
    response = await make_get_request('movies?sort=-imdb_rating')
    movies = await extract_movies(response)
    cache = await redis_client.get('movies:imdb_rating:desc:None:0:20')
    assert response.status == HTTPStatus.OK
    assert len(movies) > 0
    assert movies[0].imdb_rating >= movies[1].imdb_rating
    assert cache


@pytest.mark.asyncio
async def test_movies_list_page_number(make_get_request, redis_client):
    response = await make_get_request('movies?sort=imdb_rating&page_number=0')
    films = await extract_movies(response)
    cache = await redis_client.get('movies:imdb_rating:desc:None:0:20')
    assert response.status == HTTPStatus.OK
    assert len(films) > 0
    assert cache


@pytest.mark.asyncio
async def test_movies_list_page_size(make_get_request, redis_client):
    response = await make_get_request('movies?sort=-imdb_rating&page_number=0&page_size=10')
    movies = await extract_movies(response)
    cache = await redis_client.get('movies:imdb_rating:desc:None:0:10')
    assert response.status == HTTPStatus.OK
    assert len(movies) > 0
    assert cache


@pytest.mark.asyncio
async def test_movies_list_page_number_and_size(make_get_request, redis_client):
    response = await make_get_request('movies?sort=-imdb_rating'
                                      '&page_size=18&page_number=0')
    movies = await extract_movies(response)
    cache = await redis_client.get('movies:imdb_rating:desc:None:0:18')
    assert response.status == HTTPStatus.OK
    assert len(movies) > 0
    assert cache


@pytest.mark.asyncio
async def test_movies_page_number_and_size_sorted_asc(make_get_request,
                                                      redis_client):
    response = await make_get_request('movies?sort=imdb_rating'
                                      '&page_size=13&page_number=1')
    movies = await extract_movies(response)
    cache = await redis_client.get('movies:imdb_rating:asc:None:1:13')
    assert response.status == HTTPStatus.OK
    assert len(movies) > 0
    assert movies[0].imdb_rating <= movies[1].imdb_rating
    assert cache


@pytest.mark.asyncio
async def test_movies_page_number_and_size_sorted_desc(make_get_request,
                                                       redis_client):
    response = await make_get_request('movies?sort=-imdb_rating'
                                      '&page_size=14&page_number=2')
    movies = await extract_movies(response)
    cache = await redis_client.get('movies:imdb_rating:desc:None:2:14')
    assert response.status == HTTPStatus.OK
    assert len(response.body) > 0
    assert movies[0].imdb_rating >= movies[1].imdb_rating
    assert cache


@pytest.mark.asyncio
async def test_movies_search(make_get_request, redis_client):
    response_movies = await make_get_request('movies?sort=-imdb_rating')
    movies_list = await extract_movies(response_movies)
    movie_title = movies_list[0].title
    response = await make_get_request(f'movies/search?query={movie_title}')
    search_movies = await extract_movies(response)
    cache = await redis_client.get(f'movies:{movie_title}:title:0:20')
    assert response.status == HTTPStatus.OK
    assert len(search_movies) > 0
    assert cache


@pytest.mark.asyncio
async def test_movies_popular_in_genre(make_get_request, redis_client):
    response = await make_get_request(
        'movies/genres/120a21cf-9097-479e-904a-13dd7198c1dd')
    movies = await extract_movies(response)
    cache = await redis_client.get(
        f'popular_genre:120a21cf-9097-479e-904a-13dd7198c1dd:movies')
    assert response.status == HTTPStatus.OK
    assert len(movies) > 0
    assert cache


@pytest.mark.asyncio
async def test_similar_movies(make_get_request, redis_client):
    response_movies = await make_get_request('movies?sort=-imdb_rating')
    movies_list = await extract_movies(response_movies)
    movie_id = movies_list[0].id
    response = await make_get_request(f'movies/{movie_id}/similar')
    movies = await extract_movies(response)
    cache = await redis_client.get(f'similar:{movie_id}:movies')
    assert response.status == HTTPStatus.OK
    assert len(movies) > 0
    assert cache


@pytest.mark.asyncio
async def test_es_uploading(make_get_request, redis_client):
    response = await make_get_request('movies/2a090dde-f688-46fe-a9f4-b781a9852756')
    movie = await extract_movie(response)
    cache = await redis_client.get('2a090dde-f688-46fe-a9f4-b781a9852756')
    assert str(movie.id) == "2a090dde-f688-46fe-a9f4-b781a9852756"
    assert movie.title == "Blindeer"
    assert cache
