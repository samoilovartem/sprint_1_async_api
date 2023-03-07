from backoff import on_exception, expo
from loguru import logger
from pydantic import ValidationError

from configs import loguru_config, settings_config
from schemas import MovieData

logger.add(**loguru_config)


class DataTransformer:
    """A class to validate and transform postgres data with pydantic model."""

    def get_persons_by_role(
            self, persons: list[dict], roles: list[str]
    ) -> dict[str, tuple[list[dict], list[str]]]:
        persons_data_by_role = {}
        for role in roles:
            persons_with_role = [
                {'id': person['id'], 'name': person['name']}
                for person in persons
                if person['role'] == role
            ]
            names_of_persons_with_role = [person['name'] for person in persons_with_role]
            persons_data_by_role[role] = (persons_with_role, names_of_persons_with_role)
        return persons_data_by_role

    @on_exception(expo, ValidationError, max_tries=settings_config.MAX_TRIES, logger=logger)
    def transform_movies_data(self, movies: list[dict]) -> list[MovieData]:
        movies_data = []
        for movie in movies:
            persons = self.get_persons_by_role(
                movie['all_persons'], ['director', 'actor', 'writer']
            )
            movie_data = MovieData(
                id=movie['id'],
                imdb_rating=movie['rating'],
                genre=movie['genres'],
                title=movie['title'],
                description=movie['description'],
                director=persons['director'][1],
                actors_names=persons['actor'][1],
                writers_names=persons['writer'][1],
                actors=persons['actor'][0],
                writers=persons['writer'][0],
            )
            movies_data.append(movie_data)
        return movies_data
