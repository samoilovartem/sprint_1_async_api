import logging
import uvicorn
from elasticsearch import AsyncElasticsearch
from fastapi import FastAPI
from fastapi.responses import ORJSONResponse

from api.v1 import movies, genres, persons
from core import config
from core.custom_logger import CustomLogger
from db import elastic


logger = logging.getLogger(__name__)

app = FastAPI(
    title=config.PROJECT_NAME,
    docs_url='/api/openapi',
    openapi_url='/api/openapi.json',
    default_response_class=ORJSONResponse,
    logger=CustomLogger.make_logger()
)


@app.on_event('startup')
async def startup():
    elastic.es = AsyncElasticsearch(
        hosts=[f'{config.ES_HOST}:{config.ES_PORT}'])


@app.on_event('shutdown')
async def shutdown():
    await elastic.es.close()


app.include_router(movies.router, prefix='/api/v1/movies')
app.include_router(genres.router, prefix='/api/v1/genres')
app.include_router(persons.router, prefix='/api/v1/persons')


if __name__ == '__main__':
    uvicorn.run(
        'main:app',
        host='0.0.0.0',
        port=8000,
    )
