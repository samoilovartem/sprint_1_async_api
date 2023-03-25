import logging

import aioredis
import uvicorn
from elasticsearch import AsyncElasticsearch
from fastapi import FastAPI
from fastapi.responses import ORJSONResponse

from api import router
from core.config import Config
from core.custom_logger import CustomLogger
from db import elastic, redis

logger = logging.getLogger(__name__)

app = FastAPI(
    title=Config.PROJECT_NAME,
    description=Config.PROJECT_DESCRIPTION,
    version=Config.PROJECT_VERSION,
    license_info=Config.PROJECT_LICENSE,
    docs_url=Config.PROJECT_DOCS_URL,
    openapi_url=Config.PROJECT_OPENAPI_URL,
    openapi_tags=Config.PROJECT_OPENAPI_TAGS,
    default_response_class=ORJSONResponse,
    logger=CustomLogger.make_logger(),
)


@app.on_event('startup')
async def startup():
    redis.redis = await aioredis.create_redis_pool(
        f'redis://{Config.REDIS_HOST}:{Config.REDIS_PORT}'
    )
    elastic.es = AsyncElasticsearch(hosts=[f'{Config.ES_HOST}:{Config.ES_PORT}'])


@app.on_event('shutdown')
async def shutdown():
    await redis.redis.close()
    await elastic.es.close()


app.include_router(router)


if __name__ == '__main__':
    uvicorn.run(
        'main:app',
        host=Config.FASTAPI_HOST,
        port=Config.FASTAPI_PORT,
    )
