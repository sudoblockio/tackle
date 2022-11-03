from typing import TYPE_CHECKING

from tackle.utils.dicts import (
    nested_get,
    nested_delete,
    nested_set,
    get_target_and_key,
    smush_key_path,
)

from tackle import exceptions
from tackle.models import BaseHook

if TYPE_CHECKING:
    from tackle.models import Context


def var_hook_macro(args) -> list:
    """
    Handler for cases where we have a hook call with a renderable string as the first
    argument which we rewrite as a var hook. For instance `foo->: foo-{{ bar }}-baz`
    would be rewritten as `foo->: var foo-{{bar}}-baz`.
    """
    if '{{' in args[0]:
        # We split up the string before based on whitespace so eval individually
        if '}}' in args[0]:
            # This is single templatable string -> key->: "{{this}}" => args: ['this']
            args.insert(0, 'var')
        else:
            # Situation where we have key->: "{{ this }}" => args: ['{{', 'this' '}}']
            for i in range(1, len(args)):
                if '}}' in args[i]:
                    joined_template = ' '.join(args[: (i + 1)])
                    other_args = args[(i + 1) :]
                    args = ['var'] + [joined_template] + other_args
                    break
    return args


def blocks_macro(context: 'Context'):
    """
    Handle keys appended with arrows and interpret them as `block` hooks. Value is
    re-written over with a `block` hook to support the following syntax.

    a-key->:
      if: stuff == 'things'
      foo->: print ...
    to
    a-key:
      ->: block
      if: stuff == 'things'
      items:
        foo->: print ...
    """
    # Break up key paths
    base_key_path = context.key_path[:-1]
    new_key = [context.key_path[-1][:-2]]
    # Handle embedded blocks which need to have their key paths adjusted
    key_path = (base_key_path + new_key)[len(context.key_path_block) :]
    arrow = [context.key_path[-1][-2:]]

    indexed_key_path = context.key_path[
        (len(context.key_path_block) - len(context.key_path)) :
    ]
    input_dict = nested_get(
        element=context.input_context,
        keys=indexed_key_path[:-1],
    )
    value = input_dict[indexed_key_path[-1]]

    for k, v in list(input_dict.items()):
        if k == indexed_key_path[-1]:
            nested_set(context.input_context, key_path, {arrow[0]: 'block'})
            nested_delete(context.input_context, indexed_key_path)
        else:
            input_dict[k] = input_dict.pop(k)

    # Iterate through the block keys except for the reserved keys like `for` or `if`
    aliases = [v.alias for _, v in BaseHook.__fields__.items()] + ['->', '_>']
    for k, v in value.copy().items():
        if k in aliases:
            nested_set(
                element=context.input_context,
                keys=key_path + [k],
                value=v,
            )
        else:
            # Set the keys under the `items` key per the block hook's input
            nested_set(
                element=context.input_context,
                keys=key_path + ['items', k],
                value=v,
            )


def compact_hook_call_macro(context: 'Context', element: str) -> dict:
    """
    Rewrite the input_context with an expanded expression on the called compact key.
     Returns the string element as a dict with the key as the arrow and element as
     value.
    """
    # TODO: Clean this up
    base_key_path = context.key_path[:-1]
    new_key = [context.key_path[-1][:-2]]
    key_path = (base_key_path + new_key)[len(context.key_path_block) :]
    arrow = context.key_path[-1][-2:]

    extra_keys = len(context.key_path) - len(context.key_path_block)
    old_key_path = context.key_path[-extra_keys:]

    value = nested_get(
        element=context.input_context,
        keys=smush_key_path(old_key_path)[:-1],
    )

    replacement = {context.key_path[-1]: new_key[0]}
    for k, v in list(value.items()):
        value[replacement.get(k, k)] = (
            value.pop(k) if k != context.key_path[-1] else {arrow: value.pop(k)}
        )

    # Reset the key_path without arrow
    context.key_path = context.key_path_block + key_path

    return {arrow: element}


def list_to_var_macro(context: 'Context', element: list) -> dict:
    """
    Convert arrow keys with a list as the value to `var` hooks via a re-write to the
    input.
    """
    # TODO: Convert this to a block. Issue is that keys are not rendered by default so
    #  when str items in a list are parsed, they are not rendered by default. Should
    #  have some validator or something on block to render str items in a list.
    base_key_path = context.key_path[:-1]
    new_key = [context.key_path[-1][:-2]]
    old_key_path = context.key_path[len(context.key_path_block) :]
    arrow = context.key_path[-1][-2:]

    _, key_path = get_target_and_key(context)
    if isinstance(context.input_context, dict):
        nested_set(
            element=context.input_context,
            keys=base_key_path[-(len(base_key_path) - len(context.key_path_block)) :]
            + new_key,
            value={arrow: 'var', 'input': element},
        )
        # Remove the old key
        nested_delete(context.input_context, old_key_path)
        context.key_path = base_key_path + new_key

    else:
        context.input_context = {arrow: 'var', 'input': element}
        context.key_path = base_key_path

    return {arrow: 'var'}


def raise_on_private_hook(k: str, context: 'Context', func_name: str):
    raise exceptions.MalformedFunctionFieldException(
        f"The field {k} can not be a private hook call (ie ending in '_>') as there is "
        f"no situation this makes sense.",
        function_name=func_name,
        context=context,
    )


FUNCTION_ARGS = {
    'help',
    'exec',
    'exec<-',
    'return',
    'args',
    'kwargs',
    'render_exclude',
    'extends',
}


def function_field_to_parseable_macro(
    func_dict: dict, context: 'Context', func_name: str
) -> dict:
    """
    Convert function field to parseable subclassed dict that can be caught later and
     parsed in the event that the value is not supplied via some arg / kwarg.
    """
    for k, v in func_dict.copy().items():
        if k in FUNCTION_ARGS:
            continue

        elif k[-2:] == '->':
            new_value = {'default': {k[-2:]: v}}
            func_dict = {
                key if key != k else k[:-2]: value if key != k else new_value
                for key, value in func_dict.items()
            }  # noqa

        elif k[-2:] == '_>':
            raise_on_private_hook(k, context=context, func_name=func_name)

        elif not isinstance(v, dict):
            continue

        elif '->' in v:
            func_dict[k] = {'default': v}

        elif '_>' in v:
            raise_on_private_hook(k, context=context, func_name=func_name)

        elif 'default->' in v:
            new_value = func_dict[k].pop('default->')
            func_dict[k]['default'] = {'->': new_value}

        elif 'default_>' in v:
            raise_on_private_hook(k, context=context, func_name=func_name)

    return func_dict
