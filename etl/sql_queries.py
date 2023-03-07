main_sql_query = """
    SELECT
        film_work.id,
        film_work.title,
        film_work.description,
        film_work.rating,
        film_work.type,
        film_work.created_at,
        film_work.updated_at,
        COALESCE (json_agg(
        DISTINCT jsonb_build_object(
           'role', person_film_work.role,
           'id', person.id,
           'name', person.full_name
       )
    ) FILTER (WHERE person.id is not null), '[]') as all_persons,
    array_agg(DISTINCT genre.name) as genres
    FROM content.film_work
    LEFT JOIN content.person_film_work ON person_film_work.film_work_id = film_work.id
    LEFT JOIN content.person ON person.id = person_film_work.person_id
    LEFT JOIN content.genre_film_work ON genre_film_work.film_work_id = film_work.id
    LEFT JOIN content.genre ON genre.id = genre_film_work.genre_id
    WHERE film_work.updated_at > %s OR person.updated_at > %s OR genre.updated_at > %s
    GROUP BY film_work.id
"""