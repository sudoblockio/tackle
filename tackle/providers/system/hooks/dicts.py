"""Dict hooks."""
import logging
from typing import Union, Dict, List

from tackle import BaseHook, Field
from tackle.utils import merge_configs

logger = logging.getLogger(__name__)


class DictUpdateHook(BaseHook):
    """Hook for updating dict objects with items."""

    hook_type: str = 'update'

    src: dict = Field(description="A dict or list of dicts to update the input `src`")
    input: dict = Field(description="A dict or list of dicts to update the input `src`")

    _args: list = ['src', 'input']

    def execute(self):
        self.src.update(self.input)
        return self.src


class DictMergeHook(BaseHook):
    """
    Hook for recursively merging dict objects with input maps.

    :param src: The input dict to update
    :param input: A dict or list of dicts to update the input `dict`
    :return: An updated dict object.
    """

    hook_type: str = 'merge'
    inputs: list = Field(
        ...,
        description="A list of dictionaries to merge together.",
        render_by_default=True,
    )
    # pairs: Union[dict, list] = Field(..., description="")

    _args: list = ['inputs']
    _render_by_default = ['pairs']

    def execute(self):
        output = {}
        for i in self.inputs:
            output = merge_configs(output, i)
        return output


class DictPopHook(BaseHook):
    """
    Hook  for recursively merging dict objects with input maps.

    :param src: The input dict to update
    :param item: A list or string of items to remove from a dictionary or list
    :return: An updated dict object.
    """

    hook_type: str = 'pop'

    src: Union[dict, list] = None
    item: Union[Dict, List[str], str] = None

    _args: list = ['src', 'item']

    def execute(self):
        if self.item is None:
            self.src.pop()
        elif isinstance(self.item, list):
            for i in self.item:
                self.src.pop(i)
        else:
            self.src.pop(self.item)

        return self.src


class DictKeysHook(BaseHook):
    """
    Hook  for returning the keys of a dict as a list.

    :param src: The input dict or list of dicts return the keys for
    :return: List of keys or list of list of keys if input is list
    """

    hook_type: str = 'keys'

    src: dict = None

    _args: list = ['src']

    def execute(self):
        if isinstance(self.src, list):
            keys = []
            for i in self.src:
                keys.append(i.keys())
            return keys
        else:
            return list(self.src.keys())
