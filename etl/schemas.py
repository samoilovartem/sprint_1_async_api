from typing import Optional
from uuid import UUID

from pydantic import BaseModel, PostgresDsn, Field
from pydantic.env_settings import BaseSettings


class PostgresConfig(BaseSettings):
    HOST: str
    PORT: int
    USER: str
    PASSWORD: str
    DB: str

    class Config:
        env_prefix = 'POSTGRES_'

    @property
    def dsn(self) -> str:
        return PostgresDsn.build(
            scheme='postgresql',
            user=self.USER,
            password=self.PASSWORD,
            host=self.HOST,
            port=str(self.PORT),
            path=f'/{self.DB}',
        )

    @property
    def url(self) -> str:
        return str(self.dsn)


class ElasticsearchConfig(BaseSettings):
    HOST: str
    PORT: int

    class Config:
        env_prefix = 'ES_'

    @property
    def url(self) -> str:
        return f'{self.HOST}:{self.PORT}'


class CustomSettings(BaseSettings):
    CHUNK_SIZE: int = Field(200)
    FREQUENCY: int = Field(60)
    STATE_FILE_NAME: str = Field('movies_state.json')
    INDEX_NAME: str = Field('movies')
    MAX_TRIES = int = Field(5)


class MovieData(BaseModel):
    id: UUID
    imdb_rating: Optional[float]
    title: Optional[str]
    description: Optional[str]
    genre: Optional[list]
    director: Optional[list]
    actors: Optional[list[dict]]
    writers: Optional[list[dict]]
    actors_names: Optional[list[str]]
    writers_names: Optional[list[str]]
