# -*- coding: utf-8 -*-

"""Tests dict input objects for `cookiecutter.operator.lists` module."""
import os
import pytest
from tackle.main import tackle


def test_parser_conditionals_when(change_dir_fixture):
    """Verify that the `when` keyword acts right."""
    o = tackle('.', no_input=True, context_file='when.yaml')
    assert 'blah' in o
    assert 'foo' not in o
    assert 'bar' in o
    assert 'bings' in o


def test_loops(change_dir_fixture, tmpdir):
    """Verify Jinja2 time extension work correctly."""
    outputs = [x for x in os.listdir('loops') if x.startswith('output')]
    for o in outputs:
        os.remove(os.path.join('loops', o))
    output = tackle('.', no_input=True, context_file='loops.yaml')
    # output_dir=str(tmpdir),
    assert len(output['a_list_of_strings']) == 3

    outputs = [x for x in os.listdir('loops') if x.startswith('output')]
    for o in outputs:
        os.remove(os.path.join('loops', o))


def test_parser_hooks_raises_error_on_bad_hook_input(change_dir_fixture):
    """Verify that the hook parser raises the right error when a value in the hook
    dict is not in the hook type."""
    from tackle.exceptions import HookCallException

    with pytest.raises(HookCallException):
        tackle('.', context_file='unknown-hook-input.yaml')


def test_parser_hooks_raises_error_on_bad_hook_input_type(change_dir_fixture):
    """
    Verify that the hook parser raises the right error when a value in the hook
    dict is not in the hook type.
    """
    from pydantic.error_wrappers import ValidationError

    with pytest.raises(ValidationError):
        tackle('.', context_file='bad-hook-input.yaml')
