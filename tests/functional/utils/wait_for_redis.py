import time

from redis import Redis, ConnectionError

from functional.settings import test_settings

if __name__ == '__main__':
    redis_client = Redis(host=test_settings.REDIS_HOST, port=test_settings.REDIS_PORT)
    while True:
        try:
            if redis_client.ping():
                break
        except ConnectionError:
            time.sleep(1)
    print('Redis connected')
