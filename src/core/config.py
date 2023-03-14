import os

PROJECT_NAME = os.getenv('PROJECT_NAME', 'movies')
PROJECT_DOCS_URL = os.getenv('PROJECT_DOCS_URL', '/api/openapi')
PROJECT_OPENAPI_URL = os.getenv('PROJECT_OPENAPI_URL', '/api/openapi.json')
PROJECT_HOST = os.getenv('PROJECT_HOST', '0.0.0.0')
PROJECT_PORT = int(os.getenv('PROJECT_PORT', 8000))

REDIS_HOST = os.getenv('REDIS_HOST', '127.0.0.1')
REDIS_PORT = int(os.getenv('REDIS_PORT', 6379))
REDIS_CACHE_TIMEOUT = int(os.getenv('REDIS_CACHE_TIMEOUT', 60 * 10))

ES_HOST = os.getenv('ES_HOST', '127.0.0.1')
ES_PORT = int(os.getenv('ES_PORT', 9200))

POSTGRES_HOST = os.getenv('POSTGRES_HOST')
POSTGRES_PORT = os.getenv('POSTGRES_PORT')
POSTGRES_USER = os.getenv('POSTGRES_USER')
POSTGRES_PASSWORD = os.getenv('POSTGRES_PASSWORD')
POSTGRES_DB = os.getenv('POSTGRES_DB')

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

LOGLEVEL = os.getenv('LOGLEVEL', 'INFO')
