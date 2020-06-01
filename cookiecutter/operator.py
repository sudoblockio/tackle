# -*- coding: utf-8 -*-

"""Functions for discovering and executing various cookiecutter operators."""
from cookiecutter.environment import StrictEnvironment, render_variable
from cookiecutter.operators import *  # noqa

from cookiecutter.operators import BaseOperator


def run_operator(operator_dict: dict, no_input: bool = False) -> list:
    """Run operator."""
    operator_output = None
    operator_list = BaseOperator.__subclasses__()
    for o in operator_list:
        if operator_dict['type'] == o.type:  # noqa
            operator = o(operator_dict)
            # TODO: Determine if default method is needed across all operators
            # If so, need to feed in `no_input` from both cases in call
            operator_output = operator.execute()

    return operator_output


def parse_operator(
    context, key, cookiecutter_dict, append_key: bool = False, no_input: bool = False,
):
    """Parse input dict for loop and when logic and calls hooks.

    :return: cookiecutter_dict # noqa
    """
    env = StrictEnvironment(context=context)
    operator_dict = context['cookiecutter'][key]

    # Extract loop
    if 'loop' in operator_dict:
        loop_targets = render_variable(env, operator_dict['loop'], cookiecutter_dict)
        operator_dict.pop('loop')

        loop_output = []
        for l in loop_targets:
            loop_cookiecutter = cookiecutter_dict
            loop_cookiecutter.update({'item': l})
            loop_output += [
                parse_operator(
                    context, key, loop_cookiecutter, append_key=True, no_input=no_input
                )
            ]

        cookiecutter_dict.pop('item')
        cookiecutter_dict[key] = loop_output
        return cookiecutter_dict

    if 'when' in operator_dict:
        if not context:
            raise ValueError("Can't have when condition without establishing context")

        when_condition = (
            render_variable(env, operator_dict['when'], cookiecutter_dict) == 'True'
        )

        operator_dict.pop('when')
        if not isinstance(when_condition, bool):
            raise ValueError("When condition needs to render with jinja to boolean")

    else:
        when_condition = True

    if when_condition:
        operator_dict = render_variable(env, operator_dict, cookiecutter_dict)
        if not no_input:
            # Run prompt
            cookiecutter_dict[key] = run_operator(operator_dict)  # output is list
        elif 'default' in operator_dict and no_input:
            cookiecutter_dict[key] = operator_dict['default']
        else:
            # Case where no default is defined and no input - last case
            cookiecutter_dict[key] = operator_dict

        if append_key:
            return cookiecutter_dict[key]

    return cookiecutter_dict
