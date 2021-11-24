"""
Experimental parser for asynchronously parsing an input dict and pulling out keys to
be evaluated later.
"""
import asyncio
import re
from tackle.models import Context
from tackle.utils.dicts import nested_get

from pydantic import BaseModel


class NodeDict(BaseModel):
    value_dict: dict
    dependencies: set = None


def extract_nodes(context: 'Context', node: NodeDict):
    """Walks dict, check for renderable, inspect render and return those values."""
    from tackle.parser import get_hook

    Hook = get_hook(node.value_dict['<-'], context)

    node.value_dict.pop('<-')
    x = Hook.__fields__
    hook = Hook(**node.value_dict)
    for k, v in Hook(**node.value_dict).items():
        print()

    pass


def is_tackle_function(value):

    if isinstance(value, bytes):
        return False

    REGEX = re.compile(
        r"""^.*(<-|<_)$""",
        re.VERBOSE,
    )
    return bool(REGEX.match(value))


async def update_tackle(context: 'Context', element, key_path: list = None):
    if len(key_path[-1]) == 2:
        # Expanded syntax handling - ie key is of form `<-` or `<_`
        x = nested_get(context.input_dict, key_path[:-1])

        node = NodeDict(
            # TODO: Replace nested get with a heap of size 2 to get parent value
            value_dict=nested_get(context.input_dict, key_path[:-1])
        )

        context.key_dict_[tuple(key_path)] = extract_nodes(context, node)
        return
    # Compact syntax handling - ie key is of form `key<-` or `key<_` - Value is string
    node = NodeDict(value_dict={key_path[-1][-2:]: element})
    context.key_dict_[tuple(key_path)] = extract_nodes(context, node)


async def walk_elements(context: 'Context', element, key_path: list = None):
    if key_path is None:
        key_path = []

    if isinstance(element, str):
        if is_tackle_function(key_path[-1]):
            await update_tackle(context, element, key_path)
        return

    if isinstance(element, list):
        await asyncio.gather(
            *[
                walk_elements(context, v, key_path + [i.to_bytes(2, byteorder='big')])
                for i, v in enumerate(element)
            ]
        )

    if isinstance(element, dict):
        await asyncio.gather(
            *[walk_elements(context, v, key_path + [k]) for k, v in element.items()]
        )
