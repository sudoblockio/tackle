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
    operator_dict: dict,
    context=None,
    no_input=False,
    context_key='cookiecutter',
    cc_dict=None,
    env=None,
    key=None,
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
            operator = o(
                operator_dict=operator_dict,
                context=context,
                context_key=context_key,
                no_input=no_input,
                cc_dict=cc_dict,
                env=env,
                key=key,
            )
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
    cc_dict,
    append_key: bool = False,
    no_input: bool = False,
    context_key=None,
):
    """Parse input dict for loop and when logic and calls hooks.

    :return: cc_dict
    """
    global post_gen_operator_list
    if not context_key:
        context_key = next(iter(context))

    env = StrictEnvironment(context=context)
    logger.debug("Parsing context_key: %s and key: %s" % (context_key, key))
    operator_dict = context[context_key][key]

    when_condition = evaluate_when(operator_dict, env, cc_dict, context_key)

    if when_condition:
        # Extract loop
        if 'loop' in operator_dict:
            loop_targets = render_variable(
                env, operator_dict['loop'], cc_dict, context_key
            )
            operator_dict.pop('loop')

            loop_output = []
            for i, l in enumerate(loop_targets):
                loop_cookiecutter = cc_dict
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

            cc_dict.pop('item')
            cc_dict.pop('index')
            cc_dict[key] = loop_output
            return cc_dict

        if 'block' not in operator_dict['type']:
            operator_dict = render_variable(env, operator_dict, cc_dict, context_key)

        # Run the operator
        if operator_dict['merge'] if 'merge' in operator_dict else False:
            to_merge, post_gen_operator = run_operator(
                operator_dict, context, no_input, context_key, cc_dict, env
            )
            cc_dict.update(to_merge)
        else:
            cc_dict[key], post_gen_operator = run_operator(
                operator_dict, context, no_input, context_key, cc_dict, env, key
            )
        if post_gen_operator:
            post_gen_operator_list.append(post_gen_operator)

        if append_key:
            return cc_dict[key]

    return cc_dict


def evaluate_when(
    operator_dict, env, cc_dict, context_key,
):
    """Evaluate the when condition and return bool."""
    if 'when' not in operator_dict:
        return True

    when_raw = operator_dict['when']
    when_condition = False
    if isinstance(when_raw, str):
        when_condition = render_variable(env, when_raw, cc_dict, context_key)
    elif isinstance(when_raw, list):
        # Evaluate lists as successively evalutated 'and' conditions
        for i in when_raw:
            when_condition = render_variable(env, i, cc_dict, context_key)
            # If anything is false, then break immediately
            if not when_condition:
                break

    operator_dict.pop('when')

    return when_condition
