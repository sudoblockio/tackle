from typing import TYPE_CHECKING, Callable

if TYPE_CHECKING:
    from tackle.models import BaseHook


def json_schema():
    pass


def flatten():
    pass


def pop():
    pass


def update():
    pass


def split():
    pass


def new_default_methods() -> dict[str, Callable]:
    return {
        'json_schema': json_schema,
        'flatten': flatten,
        'pop': pop,
        'update': update,
        'split': split,
    }
