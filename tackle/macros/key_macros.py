from typing import TYPE_CHECKING

from tackle.models import HookCallInput
from tackle.render import render_variable

if TYPE_CHECKING:
    from tackle import Context, DocumentKeyType, DocumentValueType


def import_key_macro(value: 'DocumentValueType', arrow: str) -> 'DocumentValueType':
    if isinstance(value, dict):
        return {arrow: 'import', **value}
    elif isinstance(value, list):
        return {arrow: 'import', 'src': value}
    return {arrow: f'import {value}'}


def _return_macros(
    return_str: str, value: 'DocumentValueType', arrow: str
) -> 'DocumentValueType':
    from tackle.utils.command import unpack_args_kwargs_string

    if isinstance(value, str):
        args, kwargs, flags = unpack_args_kwargs_string(input_string=value)
    else:
        return {arrow: return_str, 'value': value}

    if len(args) == 1:
        return {arrow: return_str, 'value': args[0]} | kwargs | {k: True for k in flags}
    else:
        return (
            {arrow: return_str, 'value': ' '.join(args)}
            | kwargs
            | {k: True for k in flags}
        )


def return_key_macro(value: 'DocumentValueType', arrow: str) -> 'DocumentValueType':
    return _return_macros(return_str='return', value=value, arrow=arrow)


def returns_key_macro(value: 'DocumentValueType', arrow: str) -> 'DocumentValueType':
    return _return_macros(return_str='returns', value=value, arrow=arrow)


def exit_key_macro(value: 'DocumentValueType', arrow: str) -> 'DocumentValueType':
    return {arrow: 'exit', 'value': value, 'skip_output': True}


def raise_key_macro(value: 'DocumentValueType', arrow: str) -> 'DocumentValueType':
    return {arrow: 'raise', 'message': value}
    # 'skip_output': True,


def assert_key_macro(value: 'DocumentValueType', arrow: str) -> 'DocumentValueType':
    return {arrow: f'assert {value}'}


def command_key_macro(value: 'DocumentValueType', arrow: str) -> 'DocumentValueType':
    return {arrow: 'command', 'command': value, 'skip_output': True}


def print_key_macro(value: 'DocumentValueType', arrow: str) -> 'DocumentValueType':
    return {arrow: 'print', 'objects': value, 'skip_output': True}


def debug_key_macro(value: 'DocumentValueType', arrow: str) -> 'DocumentValueType':
    return {arrow: 'debug', 'key': value[arrow]}


def generate_key_macro(value: 'DocumentValueType', arrow: str) -> 'DocumentValueType':
    if isinstance(value, str):
        return {arrow: f'generate {value}'}
    elif isinstance(value, dict):
        return {arrow: 'generate'} | value
    return {arrow: 'generate', 'templates': value}  # Will error upstream


# Both the keys and the aliases
HOOK_CALL_KEYS = {k for k, v in HookCallInput.model_fields.items()} | {
    v.alias for k, v in HookCallInput.model_fields.items() if v.alias is not None
}


def block_hook_macro(
    context: 'Context',
    value: 'DocumentValueType',
    arrow: str,
) -> 'DocumentValueType':
    if isinstance(value, list):
        # When we have a hook with a list - we just render each item. Use the literal
        # hook here to preserve the access modifier of the hook call
        # TODO: https://github.com/sudoblockio/tackle/issues/189
        #  Figure out what lists really mean in blocks
        return {arrow: 'literal', 'input': render_variable(context=context, raw=value)}
    # Separate the base hook fields from extra `items`
    items = {}
    hook_fields = {}
    for k, v in value.items():
        if k in HOOK_CALL_KEYS:
            hook_fields.update({k: v})
        else:
            items.update({k: v})
    output = {arrow: 'block', 'items': items}
    output.update(hook_fields)

    return output


KEY_MACRO_IDS = {
    i.split('_key_macro')[0]
    for i in globals().keys()
    if i.__str__().endswith('_key_macro')
}


def key_macro(
    context: 'Context',
    key: 'DocumentKeyType',
    value: 'DocumentValueType',
) -> 'DocumentKeyType | DocumentValueType':
    """
    Key macros are run every time we parse a key in an object. They run by splitting
     any string keys with special keys and then calling the appropriate macro.

    TODO: Update key macros to parse var / args
    """
    arrow = key[-2:]
    if arrow not in ('->', '_>'):
        return key, value

    key = key[:-2]
    # Check if key is compact and expand it if so
    if key == '':
        return arrow, value

    if key in KEY_MACRO_IDS:
        key_macro_function = globals().get(f"{key}_key_macro")
        # Should always exist
        if value is not None:
            return key, key_macro_function(value=value, arrow=arrow)
        else:
            return key, key_macro_function(value={arrow: value}, arrow=arrow)
    else:
        if key != '' and isinstance(value, (dict, list)):
            # We have some kind block hook
            return key, block_hook_macro(context, value=value, arrow=arrow)
        # We don't have a special key but could have a var hook which is handled later
        return key, {arrow: value}


def var_hook_macro(args: list) -> list:
    """
    Macro for when we have a hook call with a renderable string as the first argument
     which we rewrite as a var hook. This is not called in the normal hook macros since
     we want to split the input arguments first with unpack_args_kwargs_string in the


    Ex. `foo->: foo-{{ bar }}-baz` would be rewritten as `foo->: var foo-{{bar}}-baz`
    """
    if not isinstance(args[0], str):
        return args
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
