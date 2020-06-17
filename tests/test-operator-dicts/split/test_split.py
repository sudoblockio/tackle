# -*- coding: utf-8 -*-

"""Tests dict input objects for `cookiecutter.prompt` module."""
import pytest
from cookiecutter.operator import run_operator, parse_operator

context = {
    'cookiecutter': {
        'project_name': "Slartibartfast",
        'string': {"type": "split", "items": "stuff.thing"},
        'string-sep': {"type": "split", "items": "stuff-thing", "separator": "-"},
        'list-sep': {
            "type": "split",
            "items": ["stuff-thing", "foo-bar"],
            "separator": "-",
        },
    }
}


@pytest.mark.parametrize(
    'key, expected_value',
    [
        ('string', ['stuff', 'thing']),
        ('string-sep', ['stuff', 'thing']),
        ('list-sep', [['stuff', 'thing'], ['foo', 'bar']]),
    ],
)
def test_split_operator_string(key, expected_value):
    """Verify simplest functionality."""
    operator_output, delayed_output = run_operator(
        context['cookiecutter'][key], context
    )

    assert operator_output == expected_value
    cookiecutter_dict = parse_operator(context, key, {})
    assert cookiecutter_dict == {key: expected_value}
