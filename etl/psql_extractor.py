from datetime import datetime
from typing import Generator

import psycopg2
from backoff import on_exception, expo
from loguru import logger
from psycopg2 import DatabaseError, ProgrammingError, OperationalError
from psycopg2.extras import RealDictCursor

from configs import loguru_config, settings_config

logger.add(**loguru_config)


class PostgresExtractor:
    """
    A class that extracts data from a Postgres database using a provided SQL query.
    """

    def __init__(self, dsn: str, main_sql_query: str):
        self.cursor = None
        self.connection = None
        self.dsn = dsn
        self.main_sql_query = main_sql_query

    @on_exception(expo, OperationalError, max_tries=settings_config.MAX_TRIES, logger=logger)
    def connect_to_postgres(self) -> None:
        """
        Connects to PostgreSQL using the provided DSN.
        """

        logger.info('Attempting to connect to PostgreSQL')
        self.connection = psycopg2.connect(dsn=self.dsn, cursor_factory=RealDictCursor)
        self.cursor = self.connection.cursor()
        logger.info('The connection with PostgreSQL has been established')

    @on_exception(
        expo, (DatabaseError, ProgrammingError),
        max_tries=settings_config.MAX_TRIES,
        logger=logger
    )
    def get_movies_data(
            self, latest_updated_at: datetime,
            chunk_size: int = settings_config.CHUNK_SIZE
    ) -> Generator:
        """
        Retrieves movies data from PostgreSQL using the provided SQL query.
        """

        self.cursor.execute(query=self.main_sql_query, vars=(latest_updated_at,) * 3)
        while True:
            rows = self.cursor.fetchmany(chunk_size)
            if not rows:
                break
            yield rows
