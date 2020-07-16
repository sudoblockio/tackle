# -*- coding: utf-8 -*-

"""Tests dict input objects for `cookiecutter.prompt` module."""
import os

from cookiecutter.operator import parse_operator
from cookiecutter.main import cookiecutter


base_dir = os.path.dirname(__file__)

context = {
    'nuki': {
        'project_name': "Slartibartfast",
        'details': {
            "type": "jinja",
            # "template_path": tpl_file,
            # "output_path": output_file,
            "template_path": "templates/things.py.j2",
            "output_path": "things.py",
            "file_system_loader": base_dir,
        },
    }
}


def test_jinja_operator(monkeypatch, tmpdir):
    """Verify simplest functionality."""
    if os.path.exists('things.py'):
        os.remove('things.py')

    monkeypatch.chdir(os.path.abspath(os.path.dirname(__file__)))

    context = cookiecutter('.', no_input=True, output_dir=str(tmpdir))

    assert context
    expected_output = 'things.py'
    assert expected_output in os.listdir()

    # os.remove('things.py')


def test_jinja_parse_operator():
    """Verify simplest functionality."""
    if os.path.exists('things.py'):
        os.remove('things.py')

    cookiecutter_dict = parse_operator(context, 'details', {})
    assert cookiecutter_dict == {'details': "things.py"}
    with open("things.py") as f:
        output = f.read()
    expected_file_output = "project_name"

    assert expected_file_output in output
    os.remove('things.py')


def test_operator_dict(monkeypatch, tmpdir):
    """Verify Jinja2 time extension work correctly."""
    monkeypatch.chdir(os.path.abspath(os.path.dirname(__file__)))
    if os.path.exists('things.py'):
        os.remove('things.py')

    context = cookiecutter(
        '.', context_file='nuki.yaml', no_input=True, output_dir=str(tmpdir)
    )
    assert context['foo'] == 'things'
    if os.path.exists('things.py'):
        os.remove('things.py')
