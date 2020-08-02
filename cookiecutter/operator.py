# -*- coding: utf-8 -*-

"""Functions for discovering and executing various cookiecutter operators."""
from __future__ import print_function
import logging

from cookiecutter.environment import StrictEnvironment
from cookiecutter.exceptions import InvalidOperatorType
from cookiecutter.render import render_variable
from cookiecutter.operators import *  # noqa
from cookiecutter.operators import BaseOperator

logger = logging.getLogger(__name__)
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
            logger.debug("Using the %s operator" % o.type)  # noqa
            operator = o(operator_dict, context, context_key, no_input)
            if operator.post_gen_operator:
                delayed_output = operator
            else:
                operator_output = operator.execute()
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

    :return: cookiecutter_dict
    """
    global post_gen_operator_list
    if not context_key:
        context_key = next(iter(context))

    env = StrictEnvironment(context=context)
    logger.debug("Parsing context_key: %s and key: %s" % (context_key, key))
    operator_dict = context[context_key][key]

    when_condition = _evaluate_when(operator_dict, env, cookiecutter_dict, context_key)

    if when_condition:
        # Extract loop
        if 'loop' in operator_dict:
            loop_targets = render_variable(
                env, operator_dict['loop'], cookiecutter_dict, context_key
            )
            operator_dict.pop('loop')

            loop_output = []
            for i, l in enumerate(loop_targets):
                loop_cookiecutter = cookiecutter_dict
                loop_cookiecutter.update({'index': i, 'item': l})
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
            cookiecutter_dict.pop('index')
            cookiecutter_dict[key] = loop_output
            return cookiecutter_dict

        if 'block' not in operator_dict['type']:
            operator_dict = render_variable(
                env, operator_dict, cookiecutter_dict, context_key
            )

        # Run the operator
        if operator_dict['merge'] if 'merge' in operator_dict else False:
            to_merge, post_gen_operator = run_operator(
                operator_dict, context, no_input, context_key
            )
            cookiecutter_dict.update(to_merge)
        else:
            cookiecutter_dict[key], post_gen_operator = run_operator(
                operator_dict, context, no_input, context_key
            )
        if post_gen_operator:
            post_gen_operator_list.append(post_gen_operator)

        if append_key:
            return cookiecutter_dict[key]

    return cookiecutter_dict


def _evaluate_when(
    operator_dict, env, cookiecutter_dict, context_key,
):
    if 'when' not in operator_dict:
        return True

    when_raw = operator_dict['when']
    when_condition = False
    if isinstance(when_raw, str):
        when_condition = (
            render_variable(env, when_raw, cookiecutter_dict, context_key) == 'True'
        )
    elif isinstance(when_raw, list):
        # Evaluate lists as successively evalutated 'and' conditions
        for i in when_raw:
            when_condition = (
                render_variable(env, i, cookiecutter_dict, context_key) == 'True'
            )
            # If anything is false, then break immediately
            if not when_condition:
                break

    operator_dict.pop('when')

    return when_condition
