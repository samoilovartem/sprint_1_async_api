import time

from redis import Redis, ConnectionError

from settings import Config

if __name__ == '__main__':
    redis_client = Redis(host=Config.REDIS_HOST, port=Config.REDIS_PORT)
    while True:
        try:
            if redis_client.ping():
                break
        except ConnectionError:
            time.sleep(1)
    print('Redis connected')
