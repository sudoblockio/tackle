# -*- coding: utf-8 -*-

"""Tests dict input objects for `cookiecutter.prompt` module."""
from cookiecutter.operator import run_operator, parse_operator
import os

base_dir = os.path.dirname(__file__)

context = {
    'cookiecutter': {
        'project_name': "Slartibartfast",
        'details': {"type": "listdir", "directory": os.path.join(base_dir, "dir")},
        'hidden': {
            "type": "listdir",
            "directory": os.path.join(base_dir, "dir"),
            "ignore_hidden_files": True,
        },
        'list_directories': {
            "type": "listdir",
            "directories": [
                os.path.join(base_dir, "dir"),
                os.path.join(base_dir, "dirs"),
            ],
            "ignore_hidden_files": True,
        },
    }
}


def test_listdir_operator(monkeypatch):
    """Verify simplest functionality."""
    monkeypatch.chdir(os.path.abspath(os.path.dirname(__file__)))
    operator_output, delayed_output = run_operator(
        context['cookiecutter']['details'], context
    )

    assert len(operator_output) == 3

    cookiecutter_dict = parse_operator(context, 'details', {})
    assert len(cookiecutter_dict['details']) == 3


def test_listdir_operator_ignore_hidden(monkeypatch):
    """Verify simplest functionality."""
    monkeypatch.chdir(os.path.abspath(os.path.dirname(__file__)))

    operator_output, delayed_output = run_operator(
        context['cookiecutter']['hidden'], context
    )

    assert len(operator_output) == 2

    cookiecutter_dict = parse_operator(context, 'hidden', {})
    assert len(cookiecutter_dict['hidden']) == 2


# def test_listdir_operator_directories_list(monkeypatch):
#     """Verify simplest functionality."""
#     monkeypatch.chdir(os.path.abspath(os.path.dirname(__file__)))
# operator_output, delayed_output = run_operator(
#     context['cookiecutter']['list_directories'], context
# )
#
# expected_output = {
#     os.path.join(base_dir, "dir"): ['things.py', 'stuff.txt', '.hidden-stuff'],
#     os.path.join(base_dir, "dirs"): [
#         'dir2',
#         'dir1',
#         'things.py',
#         'stuff.txt',
#         '.hidden-stuff',
#     ],
# }
# Breaking in travis
# assert operator_output == expected_output

# cookiecutter_dict = parse_operator(context, 'list_directories', {})
# assert cookiecutter_dict == {'list_directories': expected_output}
