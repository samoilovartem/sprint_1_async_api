import time
from datetime import datetime, timezone

from loguru import logger

from configs import loguru_config, pg_config, es_config, settings_config
from load import ElasticsearchLoader
from sql_queries import main_sql_query
from psql_extractor import PostgresExtractor
from transform import DataTransformer
from state import JsonFileStorage, State

logger.add(**loguru_config)


class ETL:
    """
    A class that performs an ETL process by extracting data from Postgres, transforming it,
    and loading it into Elasticsearch.
    """

    def __init__(self):
        self.psql = PostgresExtractor(dsn=pg_config.dsn, main_sql_query=main_sql_query)
        self.es = ElasticsearchLoader(es_url=es_config.url, index_name=settings_config.INDEX_NAME)
        self.transform = DataTransformer()
        self.state = State(JsonFileStorage(settings_config.STATE_FILE_NAME))

    def load_all_data(self) -> None:
        """
        Load data from Postgres to Elasticsearch
        """

        last_state = self.state.get_state('updated_at') or datetime.min
        count = 0
        try:
            for movies in self.psql.get_movies_data(last_state):
                self.state.set_state('updated_at', datetime.now(timezone.utc).isoformat())
                es_movies = self.transform.transform_movies_data(movies)
                self.es.load_movies_data(es_movies)
                count += len(movies)
            logger.info('Successfully transferred {} documents to Elasticsearch.', count)
        except Exception as e:
            logger.error('An error occurred while transferring data. Error: {}.', e)
            raise

    def run(self):
        while True:
            try:
                self.psql.connect_to_postgres()
                self.es.connect_to_elastic()
                self.es.create_index()
                self.load_all_data()
            except Exception as e:
                logger.error('An error occurred during ETL process. Error: {}.', e)
            finally:
                self.psql.cursor.close()
                self.psql.connection.close()
                time.sleep(settings_config.FREQUENCY)


if __name__ == "__main__":
    etl = ETL()
    etl.run()
