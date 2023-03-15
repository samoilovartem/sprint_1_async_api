import os
from pydantic import BaseSettings, Field


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


class Config(BaseSettings):
    PROJECT_NAME: str = Field('movies', env='PROJECT_NAME')
    PROJECT_DOCS_URL: str = Field('/api/openapi', env='PROJECT_DOCS_URL')
    PROJECT_OPENAPI_URL: str = Field('/api/openapi.json', env='PROJECT_OPENAPI_URL')
    PROJECT_GLOBAL_PAGE_SIZE: int = Field(20, env='PROJECT_GLOBAL_PAGE_SIZE')

    REDIS_HOST: str = Field('127.0.0.1', env='REDIS_HOST')
    REDIS_PORT: int = Field(6379, env='REDIS_PORT')
    REDIS_CACHE_TIMEOUT: int = Field(60 * 10, env='REDIS_CACHE_TIMEOUT')

    ES_HOST: str = Field('127.0.0.1', env='ES_HOST')
    ES_PORT: int = Field(9200, env='ES_PORT')

    POSTGRES_HOST: str = Field('db', env='POSTGRES_HOST')
    POSTGRES_PORT: int = Field(5432, env='POSTGRES_PORT')
    POSTGRES_USER: str = Field('app', env='POSTGRES_USER')
    POSTGRES_PASSWORD: str = Field('123qwe', env='POSTGRES_PASSWORD')
    POSTGRES_DB: str = Field('movies_database', env='POSTGRES_DB')

    FASTAPI_HOST: str = Field('0.0.0.0', env='FASTAPI_HOST')
    FASTAPI_PORT: int = Field(8000, env='FASTAPI_PORT')

    LOG_LEVEL: str = Field('INFO', env='LOGLEVEL')
    LOG_PATH: str = Field(os.path.join(BASE_DIR, './logs/fastapi.log'), env='LOG_PATH')
    LOG_RETENTION: str = Field('10 days', env='LOG_RETENTION')
    LOG_ROTATION: str = Field('1 day', env='LOG_ROTATION')

    class Config:
        env_file = os.path.join(BASE_DIR, '..', '.env')


Config = Config()
