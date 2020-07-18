# -*- coding: utf-8 -*-

"""Tests dict input objects for `cookiecutter.prompt` module."""
import os

from cookiecutter.operator import run_operator, parse_operator

base_dir = os.path.dirname(__file__)

context = {
    'cookiecutter': {
        'project_name': "Slartibartfast",
        'details': {"type": "command", "command": "ls " + base_dir},
    }
}


def test_command():
    """Verify simplest functionality."""
    if os.name == 'nt':
        # Not testing windows
        pass

    else:
        operator_output, delayed_output = run_operator(
            context['cookiecutter']['details'], context
        )
        expected_output = """__init__.py
__pycache__
test_command.py
"""
        assert operator_output == expected_output
        assert not delayed_output

        cookiecutter_dict = parse_operator(context, 'details', {})
        assert cookiecutter_dict == {'details': expected_output}
