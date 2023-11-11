import pytest
from typing import Callable, Type

from tackle.hooks import create_dcl_hook
from tackle.models import BaseHook


DCL_HOOK_FIXTURES: list[dict] = [
    {
        'stuff': 'things'
    },
    {
        'stuff': {
            'default': 'things',
        }
    },
    {
        'stuff': {
            'type': 'str',
            'default': 'things',
        },
    },
    {
        'stuff': {
            'enum': ['foo', 'things'],
            'default': 'things',
        },
    },
    {
        'stuff->': 'literal things',
    },
    # {
    #     'stuff': {
    #         '->': 'literal things',
    #     }
    # },
    # {
    #     'stuff': {
    #         '->': 'literal things',
    #         'if': True,
    #     }
    # },
]


@pytest.mark.parametrize("hook_input_raw", DCL_HOOK_FIXTURES)
def test_hooks_create_dcl_hook_simple_params(context, hook_input_raw):
    Hook = create_dcl_hook(
        context=context,
        hook_name="foo",
        hook_input_raw=hook_input_raw
    )
    hook = Hook()
    assert hook.hook_name == 'foo'
    assert hook.stuff == 'things'
