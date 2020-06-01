# -*- coding: utf-8 -*-

"""Tests dict input objects for `cookiecutter.prompt` module."""

# import pytest
import cookiecutter.operator
from cookiecutter import prompt


# Only tests for the basic logic of the parsing of the operator calls


def test_operator_when_false_no_input_no_default():
    """Verify `prompt_for_config` call `read_user_variable` on dict request."""
    context = {
        'cookiecutter': {
            'project_name': "Slartibartfast",
            'details': {
                "message": "what foo?",
                "type": "checkbox",
                "choices": [{"name": "value 1"}, {"name": "value 2"},],
                'when': "{{ cookiecutter.project_name != 'Slartibartfast' }}",
            },
        }
    }

    cookiecutter_dict = {
        'project_name': "Slartibartfast",
    }

    out_dict = cookiecutter.operator.parse_operator(
        context, 'details', cookiecutter_dict, no_input=True
    )
    assert out_dict == cookiecutter_dict


def test_operator_when_true_no_input_no_default():
    """Verify `prompt_for_config` call `read_user_variable` on dict request."""
    context = {
        'cookiecutter': {
            'project_name': "Slartibartfast",
            'details': {
                "message": "what foo?",
                "type": "checkbox",
                "choices": [{"name": "value 1"}, {"name": "value 2"},],
                'when': "{{ cookiecutter.project_name == 'Slartibartfast' }}",
            },
        }
    }

    cookiecutter_dict = {
        'project_name': "Slartibartfast",
    }

    out_dict = cookiecutter.operator.parse_operator(
        context, 'details', cookiecutter_dict, no_input=True
    )
    assert out_dict == cookiecutter_dict
    assert out_dict != {'project_name': "Slartibartfast"}


def test_operator_when_true_no_input_with_default():
    """Verify `prompt_for_config` call `read_user_variable` on dict request."""
    context = {
        'cookiecutter': {
            'project_name': "Slartibartfast",
            'details': {
                "message": "what fooss?",
                "type": "checkbox",
                "choices": [{"name": "value 1"}, {"name": "value 2"},],
                'when': "{{ cookiecutter.project_name == 'Slartibartfast' }}",
                'default': 'stuff',
            },
        }
    }

    cookiecutter_dict = {
        'project_name': "Slartibartfast",
    }

    out_dict = cookiecutter.operator.parse_operator(
        context, 'details', cookiecutter_dict, no_input=True
    )
    assert out_dict == {'project_name': 'Slartibartfast', 'details': 'stuff'}


def test_operator_when_true_no_input_loop():
    """Verify `prompt_for_config` call `read_user_variable` on dict request."""
    context = {
        'cookiecutter': {
            'details': {
                "message": "what details?",
                "type": "checkbox",
                "choices": [{"name": "value 1"}, {"name": "value 2"},],
                'when': "{{ cookiecutter.project_name == 'Slartibartfast' }}",
                'loop': ['foo', 'bar'],
                'default': '{{ cookiecutter.item }}',
            },
        }
    }

    cookiecutter_dict = {
        'project_name': "Slartibartfast",
    }

    out_dict = cookiecutter.operator.parse_operator(
        context, 'details', cookiecutter_dict, no_input=True
    )
    assert out_dict == {'project_name': 'Slartibartfast', 'details': ['foo', 'bar']}


def test_prompt_operator_when_true_no_input_loop():
    """Verify `prompt_for_config` call `read_user_variable` on dict request."""
    context = {
        'cookiecutter': {
            'project_name': "Slartibartfast",
            'details': {
                "message": "what details?",
                "type": "checkbox",
                "choices": [{"name": "value 1"}, {"name": "value 2"}],
                'when': "{{ cookiecutter.project_name == 'Slartibartfast' }}",
                'loop': ['foo', 'bar'],
                'default': 'stuff',
            },
            'things': {
                "message": "what things?",
                "type": "checkbox",
                "choices": [{"name": "value 1"}, {"name": "value 2"}],
                'when': "{{ 'stuff' in cookiecutter.details }}",
                'default': 'mo tings',
            },
        }
    }

    out_dict = prompt.prompt_for_config(context, no_input=True)
    assert out_dict == {
        'project_name': 'Slartibartfast',
        'details': ['stuff', 'stuff'],
        'things': 'mo tings',
    }


def test_prompt_operator_when_true_no_input_loop_item():
    """Verify `prompt_for_config` call `read_user_variable` on dict request."""
    context = {
        'cookiecutter': {
            'project_name': "Slartibartfast",
            'details': {
                "message": "what details?",
                "type": "checkbox",
                "choices": [{"name": "value 1"}, {"name": "value 2"},],
                'when': "{{ cookiecutter.project_name == 'Slartibartfast' }}",
                'loop': ['foo', 'bar'],
                'default': '{{ cookiecutter.item }}',
            },
            'things': {
                "message": "what things?",
                "type": "checkbox",
                "choices": [{"name": "value 1"}, {"name": "value 2"},],
                'when': "{{ 'foo' in cookiecutter.details }}",
                'default': 'mo tings',
            },
        }
    }

    out_dict = prompt.prompt_for_config(context, no_input=True)
    assert out_dict == {
        'project_name': 'Slartibartfast',
        'details': ['foo', 'bar'],
        'things': 'mo tings',
    }


def test_prompt_operator_when_true_no_input_loop_list():
    """Verify `prompt_for_config` call `read_user_variable` on dict request."""
    context = {
        'cookiecutter': {
            'project_name': "Slartibartfast",
            'details': {
                "message": "what details?",
                "type": "checkbox",
                "choices": [{"name": "value 1"}, {"name": "value 2"},],
                'when': "{{ cookiecutter.project_name == 'Slartibartfast' }}",
                'loop': ['foo', 'bar'],
                'default': '{{ cookiecutter.item }}',
            },
            'things': {
                "message": "what things?",
                "type": "checkbox",
                "choices": [{"name": "value 1"}, {"name": "value 2"},],
                'when': "{{ 'foo' in cookiecutter.details }}",
                'loop': "{{ cookiecutter.details }}",
                'default': '{{ cookiecutter.item }}',
            },
        }
    }

    out_dict = prompt.prompt_for_config(context, no_input=True)
    assert out_dict == {
        'project_name': 'Slartibartfast',
        'details': ['foo', 'bar'],
        'things': ['foo', 'bar'],
    }
