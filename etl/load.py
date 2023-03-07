from backoff import on_exception, expo
from elasticsearch import TransportError, ConnectionTimeout, RequestError, Elasticsearch, SerializationError
from elasticsearch.helpers import bulk
from loguru import logger

from configs import loguru_config, MOVIES_INDEX, settings_config
from schemas import MovieData

logger.add(**loguru_config)


class ElasticsearchLoader:
    """
    A class to load data into Elasticsearch.
    """

    def __init__(self, es_url: str, index_name: str):
        self.connection = None
        self.es_url = es_url
        self.index_name = index_name

    @on_exception(
        expo,
        (ConnectionError, TransportError, ConnectionTimeout),
        max_tries=settings_config.MAX_TRIES, logger=logger
    )
    def connect_to_elastic(self) -> None:
        """
        Connects to Elasticsearch.
        """

        logger.info('Attempting to connect to Elasticsearch')
        self.connection = Elasticsearch(hosts=[self.es_url])
        logger.info('The connection with Elasticsearch has been established')

    @on_exception(expo, RequestError, max_tries=settings_config.MAX_TRIES, logger=logger)
    def create_index(self) -> None:
        """
        Creates the Elasticsearch index if it doesn't exist.
        """

        if not self.connection.indices.exists(index=self.index_name):
            response = self.connection.indices.create(
                index=self.index_name,
                body=MOVIES_INDEX,
                ignore=400
            )
            logger.info('Created index "{}". Response from Elasticsearch: {}', self.index_name, response)

    @on_exception(expo, SerializationError, max_tries=settings_config.MAX_TRIES, logger=logger)
    def load_movies_data(self, data: list[MovieData]) -> None:
        """
        Loads data into Elasticsearch.
        """

        actions = [
            {
                '_index': self.index_name,
                '_id': row.id,
                '_source': row.dict()}
            for row in data
        ]
        bulk(self.connection, actions=actions)
        logger.info('Loaded {} documents to Elasticsearch.', len(data))

