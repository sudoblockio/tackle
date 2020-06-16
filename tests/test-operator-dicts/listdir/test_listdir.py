# -*- coding: utf-8 -*-

"""Tests dict input objects for `cookiecutter.prompt` module."""
from cookiecutter.operator import run_operator, parse_operator

context = {
    'cookiecutter': {
        'project_name': "Slartibartfast",
        'details': {"type": "listdir", "directory": "dir",},
    }
}


def test_listdir_operator():
    """Verify simplest functionality."""
    operator_output, delayed_output = run_operator(
        context['cookiecutter']['details'], context
    )

    expected_output = ['things.py', 'stuff.txt']
    assert operator_output == expected_output

    cookiecutter_dict = parse_operator(context, 'details', {})
    assert cookiecutter_dict == {'details': expected_output}
