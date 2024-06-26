import json
import logging
import os
from dataclasses import dataclass
from typing import Any, Union

import requests
from requests.auth import HTTPBasicAuth

from tackle import BaseHook, Field

logger = logging.getLogger(__name__)


def exit_none_200(r: requests.Response, no_exit: bool, url: str):
    """Exit if the status code is not 2xx."""
    if not (r.status_code - 200) < 100 and not no_exit:
        raise requests.exceptions.HTTPError(
            f"Error sending request to {url}, got '{r.status_code}' status code.\n"
            f"{r.content.decode('utf-8')}"
        )


def process_content(r: requests.Response, encoding) -> Any:
    """Output the content based on the header."""
    if 'application/json' in r.headers['Content-Type']:
        return json.loads(r.content)
    return r.content.decode(encoding=encoding)


@dataclass
class AuthMixin:
    """Authorization for web requesst."""

    username: str = None
    password: str = None

    def auth(self):
        if self.username is not None:
            return HTTPBasicAuth(username=self.username, password=self.password)
        return None


class RequestsGetHook(BaseHook, AuthMixin):
    """
    Hook for Requests 'get' type prompts.
    [Link](https://docs.python-requests.org/en/latest/api/#requests.get)
    """

    hook_name = 'http_get'

    # fmt: off
    url: str = Field(
        ...,
        description="URL for the new request object.",
    )
    headers: dict = Field(
        None,
        description="Headers to include in request.",
    )
    extra_kwargs: Union[str, dict] = Field(
        {}, description="Optional arguments that request takes.",
        render_by_default=True
    )
    params: dict = Field(
        None,
        description="Dictionary, list of tuples or bytes to send in the query string "
                    "for the Request."
    )
    no_exit: bool = Field(
        False,
        description="Whether to exit on non-200 response."
    )
    encoding: str = Field(
        'utf-8',
        description="For text/plain type return values, the encoding of the type."
    )
    # fmt: on

    args: list = [
        'url',
        'kwargs',
        'params',
    ]

    def exec(self) -> dict:
        r = requests.get(
            self.url,
            headers=self.headers,
            params=self.params,
            auth=self.auth(),
            **self.extra_kwargs,
        )
        exit_none_200(r, self.no_exit, self.url)
        return process_content(r, encoding=self.encoding)


class RequestsPostHook(BaseHook, AuthMixin):
    """
    Hook for Requests 'post' type prompts.
    [Link](https://docs.python-requests.org/en/latest/api/#requests.post)
    """

    hook_name = 'http_post'

    # fmt: off
    url: str = Field(
        ...,
        description="URL for the new request object.",
    )
    headers: dict = Field(
        None,
        description="Headers to include in request.",
    )
    extra_kwargs: Union[str, dict] = Field(
        {},
        description="Optional arguments that request takes.",
        render_by_default=True
    )
    # Requests API docs call for additional functionality not for yaml
    data: Any = Field(
        None,
        description="Dictionary, list of tuples, bytes, or file-like object to send in the body of the Request.",
        render_by_default=True
    )
    json_: dict = Field(
        False,
        description="A json payload to post.",
        render_by_default=True,
        alias='json'
    )
    no_exit: bool = Field(False, description="Whether to exit on non-200 response.")
    # fmt: on

    args: list = ['url', 'data', 'kwargs']

    def exec(self) -> dict:
        if isinstance(self.data, str):
            if not os.path.exists(self.data):
                raise FileNotFoundError(
                    f"For the requests patch method, data fields must be a "
                    f"reference to a file path, not {self.data}."
                )

        r = requests.post(
            self.url,
            data=self.data,
            json=self.json_,
            auth=self.auth(),
            headers=self.headers,
            **self.extra_kwargs,
        )
        exit_none_200(r, self.no_exit, self.url)

        return r.json()


class RequestsPutHook(BaseHook, AuthMixin):
    """
    Hook for Requests 'put' type prompts.
    [Link](https://docs.python-requests.org/en/latest/api/#requests.put)
    """

    hook_name = 'http_put'

    # fmt: on
    url: str = Field(
        ...,
        description="URL for the new request object.",
    )
    extra_kwargs: Union[str, dict] = Field(
        {},
        description="Optional arguments that request takes.",
        render_by_default=True,
    )
    data: Any = Field(
        None,
        description="Dictionary, list of tuples, bytes, or file-like object to send in the body of the Request.",
    )
    json_: dict = Field(
        None,
        description="A json payload to put.",
        render_by_default=True,
        alias='json',
    )
    no_exit: bool = Field(
        False,
        description="Whether to exit on non-200 response.",
    )
    # fmt: off

    args: list = ['url', 'data', 'kwargs']

    def exec(self):
        r = requests.put(
            self.url,
            data=self.data,
            json=self.json_,
            auth=self.auth(),
            **self.extra_kwargs
        )
        exit_none_200(r, self.no_exit, self.url)

        return r.json()


class RequestsPatchHook(BaseHook, AuthMixin):
    """
    Hook for Requests 'patch' type prompts.
    [Link](https://docs.python-requests.org/en/latest/api/#requests.patch)
    """

    hook_name = 'http_patch'

    # fmt: off
    url: str = Field(..., description="URL for the new request object.")
    extra_kwargs: Union[str, dict] = Field(
        {}, description="Optional arguments that request takes.",
        render_by_default=True
    )
    headers: dict = Field(None, description="Headers to include in request.")
    data: Any = Field(
        None,
        description="Dictionary, list of tuples, bytes, or file-like object to send in the body of the Request.",
    )
    json_: dict = Field(
        None,
        description="A json payload to patch.",
        render_by_default=True,
        alias='json'
    )
    no_exit: bool = Field(False, description="Whether to exit on non-200 response.")
    # fmt: off

    args: list = ['url', 'data']

    def exec(self):
        r = requests.patch(
            self.url,
            data=self.data,
            json=self.json_,
            auth=self.auth(),
            headers=self.headers,
            **self.extra_kwargs
        )
        exit_none_200(r, self.no_exit, self.url)

        return r.json()


class RequestsDeleteHook(BaseHook, AuthMixin):
    """
    Hook for Requests 'delete' type prompts.
    [Link](https://docs.python-requests.org/en/latest/api/#requests.delete)
    """

    hook_name = 'http_delete'

    # fmt: off
    url: str = Field(..., description="URL for the new request object.")
    extra_kwargs: Union[str, dict] = Field(
        {}, description="Optional arguments that request takes.",
        render_by_default=True
    )
    no_exit: bool = Field(False, description="Whether to exit on non-200 response.")
    # fmt: on

    args: list = ['url', 'kwargs']

    def exec(self):
        r = requests.delete(
            self.url,
            auth=self.auth(),
            **self.extra_kwargs,
        )
        exit_none_200(r, self.no_exit, self.url)

        return r.status_code
