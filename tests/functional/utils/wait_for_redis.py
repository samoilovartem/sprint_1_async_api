import time

from loguru import logger
from redis import ConnectionError, Redis

from tests.functional.settings import test_settings
from tests.functional.utils.loguru_config import loguru_config

logger.add(**loguru_config)


def create_redis_client(host, port):
    return Redis(host=host, port=port)


def connect_to_redis(
    redis_client, host, port, sleep_interval=test_settings.SLEEP_INTERVAL
):
    while True:
        try:
            logger.info(f'Connecting to Redis at {host}:{port}...')
            redis_client.ping()
            break
        except ConnectionError:
            logger.warning(
                'Connection to Redis at {}:{} failed. Retrying in {} seconds...',
                host,
                port,
                sleep_interval,
            )
            time.sleep(sleep_interval)
    logger.success('Redis connected')


if __name__ == '__main__':
    host = test_settings.REDIS_HOST
    port = test_settings.REDIS_PORT
    redis_client = create_redis_client(host, port)
    connect_to_redis(redis_client, host, port)
