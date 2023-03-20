import os
from pydantic import BaseSettings, Field

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


class Config(BaseSettings):

    REDIS_HOST: str = Field('127.0.0.1', env='REDIS_HOST')
    REDIS_PORT: int = Field(6379, env='REDIS_PORT')

    ES_HOST: str = Field('127.0.0.1', env='ES_HOST')
    ES_PORT: int = Field(9200, env='ES_PORT')

    FASTAPI_HOST: str = Field('0.0.0.0', env='FASTAPI_HOST')
    FASTAPI_PORT: int = Field(8000, env='FASTAPI_PORT')

    class Config:
        env_file = os.path.join(BASE_DIR, '...', '.env')


Config = Config()
