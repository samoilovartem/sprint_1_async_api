import time

from elasticsearch import Elasticsearch

from tests.functional.settings import test_settings

if __name__ == '__main__':
    hosts = f'{test_settings.ES_HOST}:{test_settings.ES_PORT}'
    es_client = Elasticsearch(hosts=hosts,
                              validate_cert=False, use_ssl=False)
    while True:
        print(f'Connecting to Elasticsearch at {hosts}...')
        if es_client.ping():
            break
        time.sleep(5)
    print('Elasticsearch connected')
