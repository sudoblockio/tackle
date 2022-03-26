import os
import json
import logging
import requests
from typing import Union, Any

from tackle.models import BaseHook, Field

logger = logging.getLogger(__name__)


def exit_none_200(r: requests.Response, no_exit: bool, url: str):
    """Exit if the status code is not 2xx."""
    if not (r.status_code - 200) < 100 and not no_exit:
        raise requests.exceptions.HTTPError(
            f"Error sending request to {url}, got '{r.status_code}' status code."
        )


def process_content(r: requests.Response):
    """Output the content based on the header."""
    if 'application/json' in r.headers['Content-Type']:
        return json.loads(r.content)
    elif 'text/plain' in r.headers['Content-Type']:
        return r.content


class RequestsGetHook(BaseHook):
    """
    Hook for Requests 'get' type prompts.
    [Link](https://docs.python-requests.org/en/latest/api/#requests.get)
    """

    hook_type: str = 'http_get'

    # fmt: off
    url: str = Field(..., description="URL for the new request object.")
    kwargs: Union[str, dict] = Field(
        {}, description="Optional arguments that request takes.",
        render_by_default=True
    )
    params: dict = Field(None,
                         description="Dictionary, list of tuples or bytes to send in the query string for the Request.")
    no_exit: bool = Field(False, description="Whether to exit on non-200 response.")
    # fmt: on

    args: list = [
        'url',
        'kwargs',
        'params',
    ]

    def exec(self) -> dict:
        r = requests.get(self.url, params=self.params, **self.kwargs)
        exit_none_200(r, self.no_exit, self.url)
        return process_content(r)


class RequestsPostHook(BaseHook):
    """
    Hook for Requests 'post' type prompts.
    [Link](https://docs.python-requests.org/en/latest/api/#requests.post)
    """

    hook_type: str = 'http_post'

    # fmt: off
    url: str = Field(..., description="URL for the new request object.")
    kwargs: Union[str, dict] = Field(
        {}, description="Optional arguments that request takes.",
        render_by_default=True
    )
    # Requests API docs call for additional functionality not for yaml
    data: Any = Field(
        None,
        description="Dictionary, list of tuples, bytes, or file-like object to send in the body of the Request.",
        render_by_default=True
    )
    input_json: dict = None
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

        r = requests.post(self.url, data=self.data, json=self.input_json, **self.kwargs)
        exit_none_200(r, self.no_exit, self.url)

        return r.json()


class RequestsPutHook(BaseHook):
    """
    Hook for Requests 'put' type prompts.
    [Link](https://docs.python-requests.org/en/latest/api/#requests.put)
    """

    hook_type: str = 'http_put'

    # fmt: on
    url: str = Field(..., description="URL for the new request object.")
    kwargs: Union[str, dict] = Field(
        {}, description="Optional arguments that request takes.",
        render_by_default=True
    )
    data: Any = Field(
        None,
        description="Dictionary, list of tuples, bytes, or file-like object to send in the body of the Request.",
        render_by_default=True
    )
    input_json: dict = Field(
        None,
        description="Json data to send in the body of the Request.",
    )
    no_exit: bool = Field(False, description="Whether to exit on non-200 response.")
    # fmt: off

    args: list = ['url', 'data', 'kwargs']

    def exec(self):
        r = requests.put(self.url, data=self.data, json=self.input_json, **self.kwargs)
        exit_none_200(r, self.no_exit, self.url)

        return r.json()


class RequestsPatchHook(BaseHook):
    """
    Hook for Requests 'patch' type prompts.
    [Link](https://docs.python-requests.org/en/latest/api/#requests.patch)
    """

    hook_type: str = 'http_patch'

    # fmt: off
    url: str = Field(..., description="URL for the new request object.")
    kwargs: Union[str, dict] = Field(
        {}, description="Optional arguments that request takes.",
        render_by_default=True
    )
    data: Any = Field(
        None,
        description="Dictionary, list of tuples, bytes, or file-like object to send in the body of the Request.",
        render_by_default=True
    )
    input_json: dict = Field(
        None,
        description="Json data to send in the body of the Request.",
    )
    no_exit: bool = Field(False, description="Whether to exit on non-200 response.")
    # fmt: off

    args: list = ['url', 'data', 'kwargs']

    def exec(self):
        r = requests.patch(
            self.url, data=self.data, json=self.input_json, **self.kwargs
        )
        exit_none_200(r, self.no_exit, self.url)

        return r.json()


class RequestsDeleteHook(BaseHook):
    """
    Hook for Requests 'delete' type prompts.
    [Link](https://docs.python-requests.org/en/latest/api/#requests.delete)
    """

    hook_type: str = 'http_delete'

    # fmt: off
    url: str = Field(..., description="URL for the new request object.")
    kwargs: Union[str, dict] = Field(
        {}, description="Optional arguments that request takes.",
        render_by_default=True
    )
    no_exit: bool = Field(False, description="Whether to exit on non-200 response.")
    # fmt: on

    args: list = ['url', 'kwargs']

    def exec(self):
        r = requests.delete(self.url, **self.kwargs)
        exit_none_200(r, self.no_exit, self.url)

        return r.status_code
