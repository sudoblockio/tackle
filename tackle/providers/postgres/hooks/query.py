from tackle import BaseHook
import psycopg2


class PostgresQuery(BaseHook):
    """
    Hook for running a query against a postgres DB and returning a list of json records
    as the response.
    """

    hook_type = "postgres_query"

    db_host: str
    db_user: str
    db_name: str
    db_password: str
    db_port: int = 5432
    query: str

    def exec(self) -> list:
        connection = psycopg2.connect(
            user=self.db_user,
            password=self.db_password,
            host=self.db_host,
            port=self.db_port,
            database=self.db_name,
        )
        cursor = connection.cursor()
        cursor.execute(self.query)
        response = [
            dict((cursor.description[i][0], value) for i, value in enumerate(row))
            for row in cursor.fetchall()
        ]
        return response
