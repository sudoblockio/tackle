# -*- coding: utf-8 -*-

"""Functions for discovering and executing various cookiecutter operators."""
from __future__ import print_function
import logging
import inspect

from cookiecutter.exceptions import InvalidOperatorType
from cookiecutter.render import render_variable

from cookiecutter.operators import *  # noqa
from cookiecutter.operators import BaseOperator

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from cookiecutter.models import Mode, Context
    from cookiecutter.configs import Settings


logger = logging.getLogger(__name__)
post_gen_operator_list = []

# hook_dict: Dict,
# context: Dict,
# no_input: bool,
# context_key: Dict,
# cc_dict: Dict,
# key: str,


def run_operator(
    c: 'Context', m: 'Mode',
):
    """Run operator."""
    if c.input_dict is None:
        c.input_dict = {}
    operator_output = None
    delayed_output = None
    operator_list = BaseOperator.__subclasses__()

    for o in operator_list:
        if (
            c.hook_dict['type'] == inspect.signature(o).parameters['type'].default
        ):  # noqa
            logger.debug("Using the %s operator" % c.hook_dict['type'])

            overrides = ['context', 'context_key', 'no_input', 'cc_dict']
            for override in overrides:
                if override in c.hook_dict:
                    exec(override + " = hook_dict[override]")
                    c.hook_dict.pop(override)

            operator = o(
                **c.hook_dict,
                context=c.input_dict,
                context_key=c.context_key,
                no_input=m.no_input,
                cc_dict=c.output_dict,
                key=c.key,
            )

            if operator.post_gen_operator:
                delayed_output = operator
            else:
                operator_output = operator.call()
            break
        if o == operator_list[-1]:
            msg = (
                "The operator %s is not available out of a list of "
                "the following operators." % c.hook_dict['type'],
                operator_list,
            )
            raise InvalidOperatorType(msg)

    return operator_output, delayed_output


def parse_hook(
    c: 'Context', m: 'Mode', s: 'Settings', append_key: bool = False,
):
    """Parse input dict for loop and when logic and calls hooks.

    :return: cc_dict
    """
    # global post_gen_operator_list
    if not c.context_key:
        c.context_key = next(iter(c.input_dict))  # TODO -> wtf

    # env = StrictEnvironment(context=context)
    logger.debug("Parsing context_key: %s and key: %s" % (c.context_key, c.key))
    c.hook_dict = c.input_dict[c.context_key][c.key]

    when_condition = evaluate_when(c)

    if when_condition:
        # Extract loop
        if 'loop' in c.hook_dict:
            loop_targets = render_variable(c, c.hook_dict['loop'])
            c.hook_dict.pop('loop')

            loop_output = []
            for i, l in enumerate(loop_targets):
                c.output_dict.update({'index': i, 'item': l})
                loop_output += [parse_hook(c, m, s, append_key=True)]

            c.output_dict.pop('item')
            c.output_dict.pop('index')
            c.output_dict[c.key] = loop_output
            return c.output_dict

        if 'block' not in c.hook_dict['type']:
            c.hook_dict = render_variable(c, c.hook_dict)

        # Run the operator
        if c.hook_dict['merge'] if 'merge' in c.hook_dict else False:
            to_merge, post_gen_hook = run_operator(c, m)
            c.output_dict.update(to_merge)
        else:
            c.output_dict[c.key], post_gen_hook = run_operator(c, m)

            #     hook_dict, context, no_input, context_key, cc_dict, key
            # )
        if post_gen_hook:
            c.post_gen_hooks.append(post_gen_hook)

        if append_key:
            return c.output_dict[c.key]

    return c.output_dict


def evaluate_when(c: 'Context'):
    """Evaluate the when condition and return bool."""
    if 'when' not in c.hook_dict:
        return True

    when_raw = c.hook_dict['when']
    when_condition = False
    if isinstance(when_raw, str):
        when_condition = render_variable(c, when_raw)
    elif isinstance(when_raw, list):
        # Evaluate lists as successively evalutated 'and' conditions
        for i in when_raw:
            when_condition = render_variable(c, i)
            # If anything is false, then break immediately
            if not when_condition:
                break

    c.hook_dict.pop('when')

    return when_condition
