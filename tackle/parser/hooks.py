# -*- coding: utf-8 -*-

"""Functions for discovering and executing various cookiecutter hooks."""
from __future__ import print_function
import logging
from PyInquirer import prompt
from pydantic.error_wrappers import ValidationError

from tackle.render import render_variable
from tackle.parser.providers import get_hook
from tackle.exceptions import HookCallException
from tackle.models import BaseHook

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from tackle.models import Mode, Context, Source

logger = logging.getLogger(__name__)


def raise_hook_validation_error(e, Hook, context: 'Context', source: 'Source'):
    """Raise more clear of an error when pydantic fails to parse an object."""
    if 'extra fields not permitted' in e.__repr__():
        # Return all the fields in the hook by removing all the base fields.
        fields = '--> ' + ', '.join(
            [
                i
                for i in Hook().dict().keys()
                if i not in BaseHook().dict().keys() and i != 'type'
            ]
        )
        error_out = (
            f"Error: The field \"{e.raw_errors[0]._loc}\" is not permitted in "
            f"file=\"{source.context_file}\" and key=\"{context.key}\".\n"
            f"Only values accepted are {fields}, (plus base fields --> "
            f"type, when, loop, chdir, merge)"
        )
        raise HookCallException(error_out)
    # elif 'value is not a valid' in e.__repr__():
    #     error_out = (
    #         f"Error: The \"{e.raw_errors[0]._loc}\" {e.raw_errors[0].exc} "
    #         f"when parsing file=\"{context.context_file}\" and key=\"{context.key}\"."
    #     )
    #     raise HookCallException(error_out)
    else:
        raise e


def run_hook(context: 'Context', mode: 'Mode', source: 'Source'):
    """Run hook."""
    if context.input_dict is None:
        context.input_dict = {}

    Hook = get_hook(context.hook_dict['type'], context)

    try:
        # Take the items out of the global context and mode if they are
        # declared in the hook dict.
        exclude_context = {
            i for i in context.dict().keys() if i in context.hook_dict.keys()
        }
        exclude_context.update({'env'})
        exclude_mode = {i for i in mode.dict().keys() if i in context.hook_dict.keys()}
        exclude_mode = exclude_mode if exclude_mode != set() else {'tmp'}

        hook = Hook(
            **context.hook_dict,
            **context.dict(exclude=exclude_context),
            **mode.dict(exclude=exclude_mode),
        )

        if hook.post_gen_hook:
            return None, hook
        else:
            return hook.call(), None

    except ValidationError as e:
        raise_hook_validation_error(e, Hook, context, source=source)


def _evaluate_confirm(context: 'Context'):
    if 'confirm' in context.hook_dict:
        if isinstance(context.hook_dict['confirm'], str):
            return prompt(
                [
                    {
                        'type': 'confirm',
                        'name': 'tmp',
                        'message': context.hook_dict['confirm'],
                    }
                ]
            )['tmp']
        elif isinstance(context.hook_dict['confirm'], dict):
            when_condition = True
            if 'when' in context.hook_dict['confirm']:
                when_condition = evaluate_when(
                    self, self.env, self.cc_dict, self.context_key,  # noqa
                )
            if when_condition:
                return prompt(
                    [
                        {
                            'type': 'confirm',
                            'name': 'tmp',
                            'message': context.hook_dict['confirm']['message'],
                            'default': context.hook_dict['confirm']['default']
                            if 'default' in context.hook_dict['confirm'] else None,
                        }
                    ]
                )['tmp']


def evaluate_when(hook_dict: dict, context: 'Context'):
    """Evaluate the when condition and return bool."""
    if 'when' not in hook_dict:
        return True

    when_raw = hook_dict['when']
    when_condition = False
    if isinstance(when_raw, bool):
        when_condition = when_raw
    if isinstance(when_raw, str):
        when_condition = render_variable(context, when_raw)
    elif isinstance(when_raw, list):
        # Evaluate lists as successively evalutated 'and' conditions
        for i in when_raw:
            when_condition = render_variable(context, i)
            # If anything is false, then break immediately
            if not when_condition:
                break

    hook_dict.pop('when')

    return when_condition


def evaluate_loop(context: 'Context', mode: 'Mode', source: 'Source'):
    """Run the parse_hook function in a loop and return a list of outputs."""
    loop_targets = render_variable(context, context.hook_dict['loop'])
    context.hook_dict.pop('loop')

    if len(loop_targets) == 0:
        context.output_dict[context.key] = []
        return []

    reverse = False
    if 'reverse' in context.hook_dict:
        # Handle reverse boolean logic
        reverse = render_variable(context, context.hook_dict['reverse'])
        if not isinstance(reverse, bool):
            raise HookCallException("Parameter `reverse` should be boolean.")
        context.hook_dict.pop('reverse')

    loop_output = []
    for i, l in enumerate(loop_targets) if not reverse else \
            reversed(list(enumerate(loop_targets))):
        # Create temporary variables in the context to be used in the loop.
        context.output_dict.update({'index': i, 'item': l})
        loop_output += [parse_hook(context, mode, source, append_key=True)]

    # Remove temp variables
    context.output_dict.pop('item')
    context.output_dict.pop('index')
    context.output_dict[context.key] = loop_output
    return context.output_dict


def parse_hook(
        context: 'Context', mode: 'Mode', source: 'Source', append_key: bool = False,
):
    """Parse input dict for loop and when logic and calls hooks.

    :return: cc_dict
    """
    logger.debug(
        "Parsing context_key: %s and key: %s" % (context.context_key, context.key)
    )
    context.hook_dict = context.input_dict[context.context_key][context.key]

    else_object = None
    if 'else' in context.hook_dict:
        else_object = render_variable(context, context.hook_dict['else'])
        context.hook_dict.pop('else')

    if evaluate_when(context.hook_dict, context):
        # Extract loop
        if 'loop' in context.hook_dict:
            # This runs the current function in a loop and returns a list of results
            return evaluate_loop(context=context, mode=mode, source=source)

        # Block hooks are run independently. This prevents rest of the hook dict from
        # being rendered,
        if 'block' not in context.hook_dict['type']:
            context.hook_dict = render_variable(context, context.hook_dict)

        # Run the hook
        if context.hook_dict['merge'] if 'merge' in context.hook_dict else False:
            # Merging is for dict outputs only where the entire dict is inserted into the
            # output dictionary.
            to_merge, post_gen_hook = run_hook(context, mode, source)
            if not isinstance(to_merge, dict):
                # TODO: Raise better error with context
                raise ValueError(f"Error merging output from key='{context.key}' in "
                                 f"file='{source.context_file}'.")
            context.output_dict.update(to_merge)
        else:
            # Normal hook run
            context.output_dict[context.key], post_gen_hook = run_hook(context, mode, source)
        if post_gen_hook:
            # TODO: Update this per #4 hook-integration
            context.post_gen_hooks.append(post_gen_hook)

        if append_key:
            return context.output_dict[context.key]

    else:
        if else_object is not None:
            # Handle the false when condition if there is an `else` param.
            # if 'else' in context.hook_dict:
            if isinstance(else_object, dict):
                # If it is a dict, run it as another hook if type key exists, otherwise
                # fallback to dict
                if 'type' in else_object:
                    context.input_dict[context.context_key][context.key] = else_object
                    return parse_hook(context, mode, source, append_key=append_key)
            else:
                # If list or str return tha actual value
                context.output_dict[context.key] = render_variable(context, else_object)
                return context.output_dict

    # if 'callback' in context.hook_dict:
    #     # Call a hook var but don't return it's output
    #     context.input_dict[context.context_key][context.key] = context.hook_dict['callback']
    #     return parse_hook(context, mode, source, append_key=append_key)

    return context.output_dict
