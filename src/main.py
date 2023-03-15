import logging

import aioredis
import uvicorn
from elasticsearch import AsyncElasticsearch
from fastapi import FastAPI
from fastapi.responses import ORJSONResponse

from api.v1 import genres, movies, persons
from core.config import Config
from core.custom_logger import CustomLogger
from db import elastic, redis

logger = logging.getLogger(__name__)

app = FastAPI(
    title=Config.PROJECT_NAME,
    docs_url=Config.PROJECT_DOCS_URL,
    openapi_url=Config.PROJECT_OPENAPI_URL,
    default_response_class=ORJSONResponse,
    logger=CustomLogger.make_logger(),
)


@app.on_event('startup')
async def startup():
    redis.redis = await aioredis.create_redis_pool(f'redis://{Config.REDIS_HOST}:{Config.REDIS_PORT}')
    elastic.es = AsyncElasticsearch(hosts=[f'{Config.ES_HOST}:{Config.ES_PORT}'])


@app.on_event('shutdown')
async def shutdown():
    await redis.redis.close()
    await elastic.es.close()


app.include_router(movies.router, prefix='/api/v1/movies', tags=['movies'])
app.include_router(genres.router, prefix='/api/v1/genres', tags=['genres'])
app.include_router(persons.router, prefix='/api/v1/persons', tags=['persons'])


if __name__ == '__main__':
    uvicorn.run(
        'main:app',
        host=Config.FASTAPI_HOST,
        port=Config.FASTAPI_PORT,
    )
