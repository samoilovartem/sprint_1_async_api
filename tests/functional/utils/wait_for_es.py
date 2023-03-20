import time

from elasticsearch import Elasticsearch

from functional.settings import test_settings

if __name__ == '__main__':
    es_client = Elasticsearch(hosts=f'{test_settings.ES_HOST}:{test_settings.ES_PORT}',
                              validate_cert=False, use_ssl=False)
    while True:
        if es_client.ping():
            break
        time.sleep(1)
    print('Elasticsearch connected')
