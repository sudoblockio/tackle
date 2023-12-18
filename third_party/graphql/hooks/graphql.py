from typing import Union

from gql import Client, gql
from gql.transport.aiohttp import AIOHTTPTransport

from tackle.models import BaseHook, Field


class GraphQlHook(BaseHook):
    """Hook to call graphql queries."""

    hook_name: str = 'graphql'
    url: str = Field(
        None,
        description="",
    )
    query: str = Field(...)
    transport: str = Field('http')
    fetch_schema_from_transport: bool = Field(True, description="")

    args = ['url', 'query']

    def exec(self) -> Union[dict, list]:
        match self.transport:
            case 'http':
                transport = AIOHTTPTransport(url=self.url)
            case _:
                transport = AIOHTTPTransport(url=self.url)

        client = Client(transport=transport, fetch_schema_from_transport=True)
        query = gql(self.query)
        result = client.execute(query)
        return result
