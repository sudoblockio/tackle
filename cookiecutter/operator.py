# -*- coding: utf-8 -*-

"""Functions for discovering and executing various cookiecutter operators."""
from cookiecutter.environment import StrictEnvironment
from cookiecutter.exceptions import InvalidOperatorType
from cookiecutter.render import render_variable
from cookiecutter.operators import *  # noqa
from cookiecutter.operators import BaseOperator

import cookiecutter as cc

post_gen_operator_list = []


def run_operator(
    operator_dict: dict, context=None, no_input=False, context_key='cookiecutter'
):
    """Run operator."""
    if context is None:
        context = {}
    operator_output = None
    delayed_output = None
    operator_list = BaseOperator.__subclasses__()
    for o in operator_list:
        if operator_dict['type'] == o.type:  # noqa
            operator = o(operator_dict, context, context_key, no_input)
            if operator.post_gen_operator:
                delayed_output = operator
            else:
                operator_output = operator._execute()
            break
        if o == operator_list[-1]:
            msg = (
                "The operator %s is not available out of a list of "
                "the following operators." % operator_dict['type'],
                operator_list,
            )
            raise InvalidOperatorType(msg)

    return operator_output, delayed_output


def parse_operator(
    context,
    key,
    cookiecutter_dict,
    append_key: bool = False,
    no_input: bool = False,
    context_key=None,
):
    """Parse input dict for loop and when logic and calls hooks.

    :return: cookiecutter_dict # noqa
    """
    global post_gen_operator_list
    if not context_key:
        context_key = next(iter(context))

    env = StrictEnvironment(context=context)
    operator_dict = context[context_key][key]

    if 'when' in operator_dict:
        if not context:
            raise ValueError("Can't have when condition without establishing context")

        if 'block' in operator_dict:

            pass

        when_condition = (
            render_variable(env, operator_dict['when'], cookiecutter_dict, context_key)
            == 'True'
        )

        operator_dict.pop('when')
        if not isinstance(when_condition, bool):
            raise ValueError("When condition needs to render with jinja to boolean")

    else:
        when_condition = True

    if when_condition:
        # Extract loop
        if 'loop' in operator_dict:
            loop_targets = render_variable(
                env, operator_dict['loop'], cookiecutter_dict, context_key
            )
            operator_dict.pop('loop')

            loop_output = []
            for l in loop_targets:
                loop_cookiecutter = cookiecutter_dict
                loop_cookiecutter.update({'item': l})
                loop_output += [
                    parse_operator(
                        context,
                        key,
                        loop_cookiecutter,
                        append_key=True,
                        no_input=no_input,
                    )
                ]

            cookiecutter_dict.pop('item')
            cookiecutter_dict[key] = loop_output
            return cookiecutter_dict

        if 'block' in operator_dict['type']:
            return cc.prompt.prompt_for_config(
                context={context_key: operator_dict['items']},
                no_input=no_input,
                context_key=context_key,
                existing_context=cookiecutter_dict,
            )

        operator_dict = render_variable(
            env, operator_dict, cookiecutter_dict, context_key
        )
        cookiecutter_dict[key], post_gen_operator = run_operator(
            operator_dict, context, no_input, context_key
        )  # output is list
        if post_gen_operator:
            post_gen_operator_list.append(post_gen_operator)

        if append_key:
            return cookiecutter_dict[key]

    return cookiecutter_dict
