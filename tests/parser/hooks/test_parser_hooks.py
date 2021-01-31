# -*- coding: utf-8 -*-

"""Tests dict input objects for `cookiecutter.operator.lists` module."""
import os
import pytest
from tackle.main import tackle
from tackle.exceptions import HookCallException
from pydantic.error_wrappers import ValidationError


def test_parser_conditionals_when(change_curdir_fixtures):
    """Verify that the `when` keyword acts right."""
    o = tackle('.', no_input=True, context_file='when.yaml')
    assert 'blah' in o
    assert 'foo' not in o
    assert 'bar' in o
    assert 'bings' in o
    assert o['else_str'] == 'this'
    assert o['else_str_var'] == 'this'
    assert o['else_list'] == ['this', 'that']
    assert o['else_list_var'] == ['this', 'that']
    assert o['else_dict'] == 'thing'
    assert o['else_dict_not'] == 'that'
    assert not o['sanity']


@pytest.fixture()
def cleanup_loops():
    """Clean up the outputs from loop."""
    outputs = [x for x in os.listdir('loops') if x.startswith('output')]
    for o in outputs:
        os.remove(os.path.join('loops', o))
    yield
    outputs = [x for x in os.listdir('loops') if x.startswith('output')]
    for o in outputs:
        os.remove(os.path.join('loops', o))


def test_parser_hooks_loops(change_curdir_fixtures, cleanup_loops):
    """Test looping functionality."""
    output = tackle('.', no_input=True, context_file='loops.yaml')
    assert len(output['a_list_of_strings_tackle']) == 3
    assert output['list_str_reversed'][0] == 'chickens'


def test_parser_hooks_loop_empty(change_curdir_fixtures, cleanup_loops):
    """Test looping functionality."""
    output = tackle('.', no_input=True, context_file='loop_empty.yaml')
    assert output


def test_parser_hooks_raises_error_on_bad_hook_input(change_curdir_fixtures):
    """
    Verify that the hook parser raises the right error.

    When a value in the hook dict is not in the hook type.
    """
    with pytest.raises(HookCallException):
        tackle('.', context_file='unknown-hook-input.yaml')


def test_parser_hooks_raises_error_on_bad_hook_input_type(change_curdir_fixtures):
    """
    Verify that the hook parser raises the right error.

    When a value in the hook dict is not in the hook type.
    """
    with pytest.raises(ValidationError):
        tackle('.', context_file='bad-hook-input.yaml')


# TODO: Fix this by importing all the hooks
# def test_no_duplicate_named_hooks(change_curdir_fixtures):
#     """Verify `prompt.prompt_for_config` raises correct error."""
#     tackle('.', no_input=True, context_file='when.yaml')
#     hook_list = BaseHook.__subclasses__()
#     operator_types = []
#
#     for o in hook_list:
#         type = inspect.signature(o).parameters['type'].default
#         operator_types = operator_types + [type]
#
#     left_over_operators = set(operator_types)
#     for i in operator_types:
#         left_over_operators.remove(i)
#
#     assert len(left_over_operators) == 0
#     assert len(operator_types) == len(set(operator_types))
