# -*- coding: utf-8 -*-

"""Tests dict input objects for `cookiecutter.prompt` module."""
import os

from cookiecutter.operator import parse_operator

# from cookiecutter.operator import run_operator

base_dir = os.path.dirname(__file__)
# tpl_file = os.path.join(base_dir, "tpl", "things.py.j2")
# output_file = os.path.join(base_dir, "things.py")

context = {
    'cookiecutter': {
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


# def test_jinja_operator():
#     """Verify simplest functionality."""
#     if os.path.exists('things.py'):
#         os.remove('things.py')
#
#     operator_output, delayed_output = run_operator(
#         context['cookiecutter']['details'], context
#     )
#
#     expected_output = 'things.py'
#     dir_output = os.listdir(base_dir)
#     expected_dir_output = ['templates', 'test_jinja.py', 'things.py', '__pycache__', '__init__.py'] # noqa
#
#     assert operator_output == expected_output
#     assert dir_output == expected_dir_output
#     assert not delayed_output
#     os.remove('things.py')


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
