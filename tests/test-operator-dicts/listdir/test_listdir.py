# -*- coding: utf-8 -*-

"""Tests dict input objects for `cookiecutter.prompt` module."""
from cookiecutter.operator import run_operator, parse_operator

context = {
    'cookiecutter': {
        'project_name': "Slartibartfast",
        'details': {"type": "listdir", "directory": "dir"},
        'hidden': {"type": "listdir", "directory": "dir", "ignore_hidden_files": True},
        'list_directories': {
            "type": "listdir",
            "directories": ["dir", "dirs"],
            "ignore_hidden_files": True,
        },
    }
}


def test_listdir_operator():
    """Verify simplest functionality."""
    operator_output, delayed_output = run_operator(
        context['cookiecutter']['details'], context
    )

    expected_output = ['things.py', 'stuff.txt', '.hidden-stuff']
    assert operator_output == expected_output

    cookiecutter_dict = parse_operator(context, 'details', {})
    assert cookiecutter_dict == {'details': expected_output}


def test_listdir_operator_ignore_hidden():
    """Verify simplest functionality."""
    operator_output, delayed_output = run_operator(
        context['cookiecutter']['hidden'], context
    )

    expected_output = ['things.py', 'stuff.txt']
    assert operator_output == expected_output

    cookiecutter_dict = parse_operator(context, 'hidden', {})
    assert cookiecutter_dict == {'hidden': expected_output}


def test_listdir_operator_directories_list():
    """Verify simplest functionality."""
    operator_output, delayed_output = run_operator(
        context['cookiecutter']['list_directories'], context
    )

    expected_output = {
        'dir': ['things.py', 'stuff.txt', '.hidden-stuff'],
        'dirs': ['dir2', 'dir1', 'things.py', 'stuff.txt', '.hidden-stuff'],
    }
    assert operator_output == expected_output

    cookiecutter_dict = parse_operator(context, 'list_directories', {})
    assert cookiecutter_dict == {'list_directories': expected_output}
