# Asynchronous API for online cinema

### Project Launch

1. Clone repository:

    ```sh
    git clone https://github.com/samoilovartem/sprint_1_async_api.git
    ```

2. To build and run containers, go to the project folder and run docker-compose:

    ```sh
    docker-compose -f docker-compose.yml up -d --build
    ```
These steps will launch services with Python + FastAPI application, ETL, Postgres, ElasticSearch and Redis.


### API Documentation

0. Swagger: http://localhost:8000/api/openapi
1. Show popular movies: http://localhost:8000/api/v1/movies?sort=-imdb_rating&page_number=0&page_size=20
2. Movie Search: http://localhost:8000/api/v1/movies/search?query=star%20wars&page_number=0&page_size=20
3. Movie Details: http://localhost:8000/api/v1/movies/c35dc09c-8ace-46be-8941-7e50b768ec33
4. Show similar movies: http://localhost:8000/api/v1/movies/c35dc09c-8ace-46be-8941-7e50b768ec33/similar
5. Popular movies in the genre: http://localhost:8000/api/v1/movies/genres/120a21cf-9097-479e-904a-13dd7198c1dd
6. Show genre list: http://localhost:8000/api/v1/genres?page_number=0&page_size=20
7. Information about the genre: http://localhost:8000/api/v1/genres/120a21cf-9097-479e-904a-13dd7198c1dd
8. Show Personality List: http://localhost:8000/api/v1/persons?page_number=0&page_size=20
9. Search by persona: http://localhost:8000/api/v1/persons/search?query=Steven%20Melching&page_number=0&page_size=20
10. Person's information: http://localhost:8000/api/v1/persons/84c192fa-7178-4a57-bdd6-a81716e7bb40


### Tests

To run the tests, go to the tests/functional/ folder and run docker-compose (by first substituting a .env file, for example .env.example).
When you start the container, it will first wait to connect to elasticsearch and redis, and then start the tests.
If all is well, you will see something like the following in the console:

`Connecting to Elasticsearch at elasticsearch:9200...`

`Elasticsearch connected`

`Connecting to Redis at redis:6379...`

`Redis connected`

`============================= test session starts ==============================`

`platform linux -- Python 3.11.2, pytest-7.2.2, pluggy-1.0.0`

`rootdir: /tests/functional`

`plugins: asyncio-0.12.0`

`collected 24 items`

`src/test_genres.py ....                                                  [ 16%]`

`src/test_movies.py .............                                         [ 70%]`

`src/test_persons.py .......                                              [100%]`

`======================== 24 passed, 4 warnings in 0.40s ========================`
