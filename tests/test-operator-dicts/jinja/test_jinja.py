# -*- coding: utf-8 -*-

"""Tests dict input objects for `cookiecutter.prompt` module."""
import os

from cookiecutter.operator import run_operator, parse_operator

context = {
    'cookiecutter': {
        'project_name': "Slartibartfast",
        'details': {
            "type": "jinja",
            "template_path": "templates/things.py.j2",
            "output_path": "things.py",
        },
    }
}


def test_jinja_operator():
    """Verify simplest functionality."""
    operator_output, delayed_output = run_operator(
        context['cookiecutter']['details'], context
    )

    expected_output = 'things.py'
    dir_output = os.listdir()
    expected_dir_output = ['templates', 'test_jinja.py', 'things.py', '__init__.py']

    assert operator_output == expected_output
    assert dir_output == expected_dir_output
    assert not delayed_output

    cookiecutter_dict = parse_operator(context, 'details', {})
    assert cookiecutter_dict == {'details': "things.py"}
    with open("things.py") as f:
        output = f.read()
    expected_file_output = 'x = {\'project_name\': \'Slartibartfast\', \'details\': {\'type\': \'jinja\', \'template_path\': \'templates/things.py.j2\', \'output_path\': \'things.py\'}}'  # noqa
    assert output == expected_file_output
    os.remove('things.py')
