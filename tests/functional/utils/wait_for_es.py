import time

from elasticsearch import Elasticsearch

from settings import Config

if __name__ == '__main__':
    es_client = Elasticsearch(hosts=f'{Config.ES_HOST}:{Config.ES_PORT}', validate_cert=False, use_ssl=False)
    while True:
        if es_client.ping():
            break
        time.sleep(1)
    print('Elasticsearch connected')
