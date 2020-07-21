# -*- coding: utf-8 -*-

"""Tests dict input objects for `cookiecutter.prompt` module."""
import os

from cookiecutter.operator import run_operator, parse_operator
from cookiecutter.main import cookiecutter


def test_operator_command(monkeypatch, tmpdir):
    """Verify the operator call works successfully."""
    monkeypatch.chdir(os.path.abspath(os.path.dirname(__file__)))

    context = cookiecutter('.', no_input=True, output_dir=str(tmpdir))

    assert context


base_name = os.path.abspath(os.path.dirname(__file__))

# TODO: This does not work in testing but does when you run it live
#  Fix this....
context = {
    'cookiecutter': {
        'project_name': "Slartibartfast",
        'details': {"type": "nukikata", "template": base_name, "no_input": True},
    },
}

context_prompt = {
    'cookiecutter': {
        'project_name': "Slartibartfast",
        'details': {"type": "nukikata_prompt", "context": context, "no_input": True},
    },
}


def test_nukikata_operator(monkeypatch):
    """Verify simplest functionality."""
    # TODO: Get this to run in IDE - import error
    monkeypatch.chdir(os.path.abspath(os.path.dirname(__file__)))
    operator_output, delayed_output = run_operator(
        context['cookiecutter']['details'], context, no_input=True
    )

    assert type(operator_output) == dict
    assert not delayed_output
    prompt_output = parse_operator(context, 'details', {}, no_input=True)
    assert type(prompt_output) == dict


# def test_nukikata_prompt_operator():
#     """Verify simplest functionality."""
#     operator_output, delayed_output = run_operator(
#         context_prompt['cookiecutter']['details'], context_prompt, no_input=True
#     )
#
#     assert type(operator_output) == OrderedDict
#     assert not delayed_output
#     prompt_output = parse_operator(context_prompt, 'details', {}, no_input=True)
#     assert type(prompt_output) == dict
