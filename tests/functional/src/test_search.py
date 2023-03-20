import datetime
import uuid
import json

import aiohttp
import pytest

from elasticsearch import AsyncElasticsearch

from functional.settings import test_settings


@pytest.mark.asyncio
async def test_search():
    es_data = [{
        'id': str(uuid.uuid4()),
        'imdb_rating': 8.5,
        'genres':
            {"name": ['Action', 'Sci-Fi']},
        'title': 'Star Wars',
        'description': 'New World',
        'directors':
            {'full_name': ['Stan']},
        'actors_names': ['Ann', 'Bob'],
        'writers_names': ['Ben', 'Howard'],
        'actors': [
            {'id': '111', 'full_name': 'Ann'},
            {'id': '222', 'full_name': 'Bob'}
        ],
        'writers': [
            {'id': '333', 'full_name': 'Ben'},
            {'id': '444', 'full_name': 'Howard'}
        ],
        'creation_date': datetime.datetime.now().strftime("%Y-%m-%d"),
        'type': 'movie'
    } for _ in range(60)]

    bulk_query = []
    for row in es_data:
        bulk_query.extend([
            json.dumps({'index': {'_index': test_settings.ES_INDEX,
                                  '_id': row[test_settings.ES_ID_FIELD]}}),
            json.dumps(row)
        ])

    str_query = '\n'.join(bulk_query) + '\n'

    es_client = AsyncElasticsearch(hosts=f'http://{test_settings.ES_HOST}:{test_settings.ES_PORT}',
                                   validate_cert=False,
                                   use_ssl=False)
    response = await es_client.bulk(str_query, refresh=True)
    await es_client.close()
    if response['errors']:
        print(response)
        raise Exception('Elasticsearch data writing error')

    session = aiohttp.ClientSession()
    url = f'http://{test_settings.SERVICE_HOST}:{test_settings.SERVICE_PORT}/api/v1/movies/search'
    query_data = {'query': 'star wars',
                  'page_number': 2,
                  'page_size': 20}
    async with session.get(url, params=query_data) as response:
        body = await response.json()
        headers = response.headers
        status = response.status
    await session.close()

    assert status == 200
    assert len(response._body) == 50
