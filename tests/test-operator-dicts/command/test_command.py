# -*- coding: utf-8 -*-

"""Tests dict input objects for `cookiecutter.prompt` module."""

from cookiecutter.operator import run_operator, parse_operator

context = {
    'cookiecutter': {
        'project_name': "Slartibartfast",
        'details': {"type": "command", "command": "echo here"},
    }
}


def test_command():
    """Verify simplest functionality."""
    operator_output, delayed_output = run_operator(
        context['cookiecutter']['details'], context
    )
    assert operator_output == 'here\n'
    assert not delayed_output

    cookiecutter_dict = parse_operator(context, 'details', {})
    assert cookiecutter_dict == {'details': 'here\n'}
