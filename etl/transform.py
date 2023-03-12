from typing import Union

from backoff import on_exception, expo
from loguru import logger
from pydantic import ValidationError

from configs import loguru_config, settings_config
from schemas import MovieData, GenreData, FullPersonData

logger.add(**loguru_config)


class DataTransformer:
    """A class to validate and transform postgres data with pydantic model."""

    def get_persons_by_role(
            self,
            persons: list[dict],
            roles: list[str]
    ) -> dict[str, tuple[list[dict], list[str]]]:
        persons_data_by_role = {}
        for role in roles:
            persons_with_role = [
                {
                    'id': person.get('id'),
                    'full_name': person.get('full_name')
                }
                for person in persons
                if person.get('role') == role
            ]
            names_of_persons_with_role = [person.get('full_name') for person in persons_with_role]
            persons_data_by_role[role] = (persons_with_role, names_of_persons_with_role)
        return persons_data_by_role

    @on_exception(expo, ValidationError, max_tries=settings_config.MAX_TRIES, logger=logger)
    def transform_movies_data(
            self,
            movies_data: list[dict],
            index_name: str,
    ) -> list[Union[MovieData, GenreData, FullPersonData]]:
        es_data = []
        if index_name == 'movies':
            for movie in movies_data:
                persons = self.get_persons_by_role(
                    persons=movie['all_persons'],
                    roles=['director', 'actor', 'writer']
                )
                genres = [
                    GenreData(
                        id=genre['id'],
                        name=genre['name'],
                        description=genre['description'],
                    )
                    for genre in movie['all_genres']
                ]
                movie_data = MovieData(
                    id=movie['id'],
                    imdb_rating=movie['rating'],
                    type=movie['type'],
                    creation_date=movie["creation_date"],
                    genres=genres,
                    title=movie['title'],
                    file_path=movie["file_path"],
                    description=movie['description'],
                    directors_names=persons['director'][1],
                    actors_names=persons['actor'][1],
                    writers_names=persons['writer'][1],
                    directors=persons['director'][0],
                    actors=persons['actor'][0],
                    writers=persons['writer'][0],
                )
                es_data.append(movie_data)
            return es_data
        elif index_name == 'genres':
            for genre in movies_data:
                genre_data = GenreData(
                    id=genre['id'],
                    name=genre['name'],
                    description=genre['description'],
                )
                es_data.append(genre_data)
            return es_data
        else:
            for person in movies_data:
                person_data = FullPersonData(
                    id=person['id'],
                    full_name=person['full_name'],
                    roles=person['roles'],
                    movies_ids=[movie['id'] for movie in person['all_movies']],
                )
                es_data.append(person_data)
            return es_data
