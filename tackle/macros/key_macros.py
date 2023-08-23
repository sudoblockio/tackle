import re

from tackle import Context, DocumentKeyType, DocumentValueType, exceptions


def raise_key_macro_type_error(
        context: Context,
        func_name: str,
        type_: str, msg: str = None
):
    if msg is None:
        msg = f"{func_name} {type_}"

    raise exceptions.UnknownInputArgumentException(msg, context=context)


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
    if isinstance(value, str):
        return {
            arrow: 'import',
            'providers': [value]
        }
    elif isinstance(value, list):
        return {
            arrow: 'import',
            'providers': value
        }
    else:
        raise_key_macro_type_error()


def return_key_macro(
    *,
    context: 'Context',
    key: 'DocumentKeyType',
    value: 'DocumentValueType',
    arrow: str,
) -> 'DocumentValueType':
    return {
        arrow: 'return',
        'value': value,
        'skip_output': True,
    }


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
        'exception': value,
        'skip_output': True,
    }


def assert_key_macro(
        *,
        context: 'Context',
        key: 'DocumentKeyType',
        value: 'DocumentValueType',
        arrow: str,
) -> 'DocumentValueType':
    return {
        arrow: f'assert {value}',
        'skip_output': True,
    }


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
        return value = {arrow: value}
    """
    context.key_path = context.key_path[:-1] + [key]  # noqa
    return {arrow: value}


KEY_MACRO_IDS = {
    i.split('_key_macro')[0] for i in globals().keys()
    if i.__str__().endswith('_key_macro')
}
KEY_REGEX = f"^({'|'.join(KEY_MACRO_IDS)})"
KEY_PATTERN = re.compile(KEY_REGEX)

def key_macro(
        *,
        context: 'Context',
        key: 'DocumentKeyType',
        value: 'DocumentValueType',
        arrow: str,
) -> 'DocumentValueType':
    """
    Run the key macros by splitting any string keys with special keys and then calling
     the appropriate macro discarding any remaining chars used to make keys unique.
    """
    if key != '':
        # Fix the key if not already -> ie key->: value to key: {'->': value}
        value = key_to_dict_macro(context=context, key=key, value=value, arrow=arrow)
    if not isinstance(key, str):
        return value
    # Same as split_key = re.split(KEY_REGEX, key)
    split_key = KEY_PATTERN.split(key)
    split_key_len = len(split_key)
    if split_key_len == 1:
        # We don't have a special key
        return value
    elif split_key_len == 3:
        key_macro_function = globals().get(f"{split_key[1]}_key_macro", None)
        # Should never be None
        # if key is None: return
        return key_macro_function(context=context, key=key, value=value, arrow=arrow)
    else:
        raise Exception("Should never happen...")
