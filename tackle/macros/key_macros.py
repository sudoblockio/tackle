import re
from ruyaml.constructor import CommentedKeyMap, CommentedMap
from typing import TYPE_CHECKING

from tackle.render import render_variable
from tackle import exceptions
from tackle.models import HookCallInput

if TYPE_CHECKING:
    from tackle import Context, DocumentKeyType, DocumentValueType

def raise_key_macro_type_error(
        context: 'Context',
        func_name: str,
        type_: str, msg: str = None
):
    if msg is None:
        msg = f"{func_name} {type_}"

    raise exceptions.UnknownHookInputArgumentException(msg, context=context)


def expand_compact_hook_macro():
    """Takes string values and expands them to dicts."""
    pass


def import_key_macro(
        *,
        context: 'Context',
        key: 'DocumentKeyType',
        value: 'DocumentValueType',
        arrow: str,
) -> 'DocumentValueType':
    if isinstance(value, dict):
        return {
            arrow: 'import',
            **value
        }
    elif isinstance(value, list):
        return {
            arrow: 'import',
            'src': value
        }
    return {arrow: f'import {value}'}

    # else:
    #     raise exceptions.MalformedHookFieldException(
    #         f"The import hook special key needs to have a str, list, or dict input.",
    #         context=context, hook_name='import'
    #     )


def return_key_macro(
        *,
        context: 'Context',
        key: 'DocumentKeyType',
        value: 'DocumentValueType',
        arrow: str,
) -> 'DocumentValueType':
    from tackle.utils.command import unpack_args_kwargs_string

    if isinstance(value, str):
        args, kwargs, flags = unpack_args_kwargs_string(input_string=value)
    else:
        return {arrow: 'return', 'value': value}

    if len(args) == 1:
        return {arrow: 'return', 'value': args[0]} | kwargs | {k: True for k in flags}
    else:
        return {arrow: 'return', 'value': ' '.join(args)} | kwargs | {k: True for k in flags}

def exit_key_macro(
        *,
        context: 'Context',
        key: 'DocumentKeyType',
        value: 'DocumentValueType',
        arrow: str,
) -> 'DocumentValueType':
    return {
        arrow: 'exit',
        'value': value,
        'skip_output': True,
    }


def raise_key_macro(
        *,
        context: 'Context',
        key: 'DocumentKeyType',
        value: 'DocumentValueType',
        arrow: str,
) -> 'DocumentValueType':
    return {
        arrow: 'raise',
        'message': value,
        # 'skip_output': True,
    }


def assert_key_macro(
        context: 'Context',
        key: 'DocumentKeyType',
        value: 'DocumentValueType',
        arrow: str,
) -> 'DocumentValueType':
    return {arrow: f'assert {value}'}


def command_key_macro(
        *,
        context: 'Context',
        key: 'DocumentKeyType',
        value: 'DocumentValueType',
        arrow: str,
) -> 'DocumentValueType':
    return {
        arrow: 'command',
        'command': value,
        'skip_output': True,
    }


def print_key_macro(
        *,
        context: 'Context',
        key: 'DocumentKeyType',
        value: 'DocumentValueType',
        arrow: str,
) -> 'DocumentValueType':
    return {
        arrow: 'print',
        'objects': value,
        'skip_output': True,
    }


def debug_key_macro(
        *,
        context: 'Context',
        key: 'DocumentKeyType',
        value: 'DocumentValueType',
        arrow: str,
) -> 'DocumentValueType':
    return {
        arrow: 'debug',
    }


def key_to_dict_macro(
        *,
        context: 'Context',
        key: 'DocumentKeyType',
        value: 'DocumentValueType',
        arrow: str,
) -> 'DocumentValueType':
    """
    Takes in generic key with arrow, overwrites key path by replacing the last key_path
     item with the key. Returns the value as a dict with the arrow as the key.

    Ex:
        key_path = ['a', 'b', 'c->'] to ['a', 'b', 'c']
        return value = {'->': value}
    """
    context.key_path = context.key_path[:-1] + [key]  # noqa
    return {arrow: value}


# Both the keys and the aliases
HOOK_CALL_KEYS = {k for k, v in HookCallInput.model_fields.items()} | {
    v.alias for k, v in HookCallInput.model_fields.items() if v.alias is not None}


def block_hook_macro(
        *,
        context: 'Context',
        key: 'DocumentKeyType',
        value: 'DocumentValueType',
        arrow: str,
) -> 'DocumentValueType':
    context.key_path = context.key_path[:-1] + [key]  # noqa

    if isinstance(value, list):
        # When we have a hook with a list - we just render each item. Use the literal
        # hook here to preserve the access modifier of the hook call
        # TODO: https://github.com/sudoblockio/tackle/issues/185
        #  Apply unquoted_yaml_template_macro
        # TODO: https://github.com/sudoblockio/tackle/issues/189
        #  Figure out what lists really mean in blocks
        return {
            arrow: 'literal',
            'input': render_variable(context=context, raw=value)
        }
    # Separate the base hook fields from extra `items`
    items = {}
    hook_fields = {}
    for k, v in value.items():
        if k in HOOK_CALL_KEYS:
            hook_fields.update({k: v})
        else:
            items.update({k: v})
    output = {
        arrow: 'block',
        'items': items
    }
    output.update(hook_fields)

    return output


KEY_MACRO_IDS = {
    i.split('_key_macro')[0]
    for i in globals().keys()
    if i.__str__().endswith('_key_macro')

}
KEY_REGEX = f"^({'|'.join(KEY_MACRO_IDS)})"
KEY_PATTERN = re.compile(KEY_REGEX)


def key_macro(
        *,
        context: 'Context',
        # key: 'DocumentKeyType',
        value: 'DocumentValueType',
        # arrow: str,
) -> 'DocumentValueType':
    """
    Key macros are run when parse a key.
    Run the key macros by splitting any string keys with special keys and then calling
     the appropriate macro discarding any remaining chars used to make keys unique.
    """
    last_key = context.key_path[-1]
    arrow = last_key[-2:]
    is_hook = arrow in ('->', '_>')
    if not is_hook:
        return value

    # Fix unquoted template error in yaml inputs
    # value = unquoted_yaml_template_macro(value=value)

    key = last_key[:-2]
    fixed_key = False  # Hacky var to know if we are indented TODO: Fix me
    # if key != '' and isinstance(value, (str, int, float, bool)):
    #     # Fix the key if not already -> ie key->: value to key: {'->': value}
    value = key_to_dict_macro(context=context, key=key, value=value, arrow=arrow)
        # fixed_key = True

    # elif key != '' and isinstance(value, (dict, list)):
    #     # We have some kind block hook
    #     return block_hook_macro(
    #         context=context,
    #         key=key,
    #         value=value.copy(),
    #         arrow=arrow
    #     )

    # if not isinstance(key, str):
    #     return value
    # Same as split_key = re.split(KEY_REGEX, key)
    split_key = KEY_PATTERN.split(key)
    split_key_len = len(split_key)
    if split_key_len == 1:
        # We don't have a special key
        if key != '' and isinstance(value[arrow], (dict, list)):
            # We have some kind block hook
            return block_hook_macro(
                context=context,
                key=key,
                value=value.copy()[arrow],
                arrow=arrow
            )
        # We don't have a special key but could have a var hook which is handled later
        return value
    elif split_key_len == 3:
        key_macro_function = globals().get(f"{split_key[1]}_key_macro")
        # Right now we don't support special key arguments so when we split this we need
        # to additionally check if the first and last split_key are empty (ie '')
        if split_key[0] != '' or split_key[2] != '':
            return value

        # Should always exist
        if value is not None:
            return key_macro_function(
                context=context,
                key=key,
                value=value[arrow],
                arrow=arrow
            )
        else:
            return key_macro_function(
                context=context,
                key=key,
                value=value,
                arrow=arrow
            )

    else:
        raise Exception("Should never happen...")


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
                    other_args = args[(i + 1):]
                    args = ['var'] + [joined_template] + other_args
                    break

    return args
