from http import HTTPStatus

import pytest

from tests.functional.utils.helpers import (extract_genre, extract_genres,
                                            extract_payload)
from tests.functional.utils.schemas import GenreDetail


@pytest.fixture(scope='session')
async def load_testing_genres_data(es_client):
    index = 'genres'
    payload = await extract_payload(f'{index}.json', GenreDetail, index)
    await es_client.bulk(body=payload[0], index=index, refresh=True)
    yield
    await es_client.bulk(body=payload[1], index=index, refresh=True)


@pytest.mark.asyncio
async def test_general_genres_list(make_get_request,
                                   load_testing_genres_data,
                                   redis_client):
    response = await make_get_request('genres?page_number=0&page_size=20')
    genres = await extract_genres(response)
    cache = await redis_client.get('genres:0:20')
    assert response.status == HTTPStatus.OK
    assert len(genres) > 0
    assert cache


@pytest.mark.asyncio
async def test_genre_search_via_id(make_get_request, redis_client):
    response_genres = await make_get_request('genres/')
    genres_list = await extract_genres(response_genres)
    genre_id = genres_list[0].id
    response = await make_get_request(f'genres/{genre_id}')
    genre = await extract_genre(response)
    cache = await redis_client.get(f'{genre_id}')
    assert response_genres.status == HTTPStatus.OK
    assert response.status == HTTPStatus.OK
    assert genre.id == genre_id
    assert cache


@pytest.mark.asyncio
async def test_genres_search(make_get_request, redis_client):
    response_genres = await make_get_request('genres/')
    genres_list = await extract_genres(response_genres)
    genre_name = genres_list[0].name
    response = await make_get_request(f'genres/search?query={genre_name}')
    search_genre = await extract_genres(response)
    cache = await redis_client.get(f'genres:{genre_name}:name:0:20')
    assert response.status == HTTPStatus.OK
    assert len(search_genre) > 0
    assert cache


@pytest.mark.asyncio
async def test_es_genre_uploading(make_get_request, redis_client):
    response = await make_get_request(
        'genres/3d8d9bf5-0d90-4353-88ba-4ccc5d2c07f1')
    genre = await extract_genre(response)
    cache = await redis_client.get('3d8d9bf5-0d90-4353-88ba-4ccc5d2c07f1')
    assert str(genre.id) == "3d8d9bf5-0d90-4353-88ba-4ccc5d2c07f1"
    assert genre.name == "SuperAction"
    assert cache
