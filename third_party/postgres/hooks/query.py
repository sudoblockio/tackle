from tackle import BaseHook, Field
import psycopg2


class PostgresQuery(BaseHook):
    """
    Hook for running a query against a postgres DB and returning a list of json records
    as the response.
    """

    hook_type = "postgres_query"

    # fmt: off
    query: str = Field(..., description="The query to run.")
    dbname: str = Field("postgres", description="The database name (database is a deprecated alias).")
    user: str = Field("postgres", description="User name used to authenticate.")
    password: str = Field(None, description="Password used to authenticate.")
    host: str = Field(None, description="Database host address (defaults to UNIX socket if not provided).")
    port: int = Field(5432, description="Connection port number (defaults to 5432 if not provided).")
    # fmt: on

    def exec(self) -> list:
        connection = psycopg2.connect(
            user=self.user,
            password=self.password,
            host=self.host,
            port=self.port,
            database=self.dbname,
        )
        cursor = connection.cursor()
        cursor.execute(self.query)
        response = [
            dict((cursor.description[i][0], value) for i, value in enumerate(row))
            for row in cursor.fetchall()
        ]
        return response
