import time

from redis import Redis, ConnectionError

from tests.functional.settings import test_settings

if __name__ == '__main__':
    host = test_settings.REDIS_HOST
    port = test_settings.REDIS_PORT
    redis_client = Redis(host=host, port=port)
    while True:
        try:
            print(f'Connecting to Redis at {host}:{port}...')
            if redis_client.ping():
                break
        except ConnectionError:
            time.sleep(5)
    print('Redis connected')
