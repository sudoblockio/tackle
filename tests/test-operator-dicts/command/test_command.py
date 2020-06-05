# -*- coding: utf-8 -*-

"""Tests dict input objects for `cookiecutter.prompt` module."""

from cookiecutter.operators.command import CommandOperator
import os

context = {
    'cookiecutter': {
        'project_name': "Slartibartfast",
        'details': {"type": "command", "command": "pwd"},
    }
}


def test_command():
    """Verify simplest functionality."""
    c = CommandOperator(context['cookiecutter']['details'], context)
    d = c.execute()
    assert d.rstrip() == os.path.abspath(os.path.dirname(__file__))
