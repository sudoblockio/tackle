# -*- coding: utf-8 -*-

"""Prompts used in parsing."""
import json
from collections import OrderedDict
from PyInquirer import prompt
from cookiecutter.render import render_variable

from typing import TYPE_CHECKING
import click  # RM

if TYPE_CHECKING:
    from cookiecutter.models import Context, Mode

# def read_user_variable(var_name, default_value):
#     pass


def read_user_yes_no(question, default_value):
    """Ask user yes or no for generic question."""
    question = {
        'type': 'list',
        'name': 'tmp',
        'message': question,
        'default': default_value,
        'choices': ['yes', 'no'],
    }
    return prompt([question])['tmp']


def read_user_choice(var_name, options):
    """Ask user choice for generic question. Legacy."""
    question = {
        'type': 'list',
        'name': 'tmp',
        'message': var_name + ': ',
        'choices': options,
    }
    return prompt([question])['tmp']


def process_json(user_value):
    """Load user-supplied value as a JSON dict. Legacy.

    :param str user_value: User-supplied value to load as a JSON dict
    """
    try:
        user_dict = json.loads(user_value, object_pairs_hook=OrderedDict)
    except Exception:
        # Leave it up to click to ask the user again
        raise click.UsageError('Unable to decode to JSON.')

    if not isinstance(user_dict, dict):
        # Leave it up to click to ask the user again
        raise click.UsageError('Requires JSON dict.')

    return user_dict


def read_user_dict(var_name, default_value):
    """Prompt the user to provide a dictionary of data.

    :param str var_name: Variable as specified in the context
    :param default_value: Value that will be returned if no input is provided
    :return: A Python dictionary to use in the context.
    """
    # Please see https://click.palletsprojects.com/en/7.x/api/#click.prompt
    if not isinstance(default_value, dict):
        raise TypeError

    default_display = 'default'

    user_value = click.prompt(
        var_name, default=default_display, type=click.STRING, value_proc=process_json
    )

    if user_value == default_display:
        # Return the given default w/o any processing
        return default_value
    return user_value


def prompt_list(c: 'Context', m: 'Mode', raw):
    """Prompt user with a set of options to choose from.

    Each of the possible choices is rendered beforehand.
    """
    rendered_options = [render_variable(c, raw) for raw in raw]

    if m.no_input and c.tackle_gen == 'cookiecutter':
        return rendered_options[0]
    elif m.no_input and c.tackle_gen == 'tackle':
        return rendered_options

    question = {
        'type': 'list',
        'name': 'tmp',
        'message': c.key + ': ',
        'choices': rendered_options,
    }
    return prompt([question])['tmp']


def prompt_str(c: 'Context', m: 'Mode', raw):
    """Prompt user for simple imput."""
    val = render_variable(c, raw)
    if m.no_input:
        return val
    else:
        question = {
            'type': 'input',
            'name': 'tmp',
            'message': c.key + ': ',
            'default': val,
        }
        return prompt([question])['tmp']

    pass
