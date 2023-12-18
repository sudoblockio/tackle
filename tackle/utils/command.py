"""
Utils for handling command arguments along with unpacking hook arguments. Used in cli
to unpack input args/kwargs and in parser to unpack hook calls -

i.e. key->: hook arg --kwarg thing --flag
Parsed into args=['arg'], kwargs={'kwarg':'thing'}, flags=['flag']

NOTE: This is dirty code but works. Should be replaced by PEG parser. See proposals
"""
import ast
import re

from tackle.types import DocumentValueType


def get_global_kwargs(kwargs: dict, model_fields: dict):
    """Check for unknown kwargs and return so that they can be consumed later."""
    global_kwargs = {}
    for k, v in kwargs.items():
        if k not in model_fields and k != 'override':
            global_kwargs.update({k: v})
    if global_kwargs == {}:
        return None
    return global_kwargs


def strip_dashes(raw_arg: str) -> str:
    """Remove dashes prepended to string for arg splitting."""
    while raw_arg.startswith('-'):
        raw_arg = raw_arg[1:]
    return raw_arg


def literal_eval(input_value):
    """
    Wrapper for ast.literal eval that accounts for hex and bools which it normally
     coerces to int/string respectively.
    """
    if isinstance(input_value, str) and input_value.startswith('0x'):
        # Prevent hex from being coerced to int type
        return input_value
    elif isinstance(input_value, str) and input_value.lower() in ('true', 'false'):
        # Prevent bools from being coerced to strings
        return input_value.lower() == 'true'
    else:
        try:
            return ast.literal_eval(input_value)
        except (ValueError, SyntaxError):
            # Fix ast.literal_eval coercing bools to strings
            if input_value == 'true':
                return True
            elif input_value == 'false':
                return False
            else:
                return input_value


# Inspired from https://stackoverflow.com/a/524796/12642712
# Split on whitespace or `=`
# When quotes are preceded by `,:{[(=`, ignore
# Don't split between quotes with `,:]})`
# Otherwise split on quotes
# Repeated for single quotes
SPLIT_PATTERN = re.compile(
    "( |(?<!,|\:|\(|\{|\[|=)\\\"(?!\,|\:|\)|\}|\]).*?\\\"(?!\}|\])|(?<!\,|\:|\(|\{|\[|=)'(?!,|\:|\)|\}|\]).*?'(?!\}|\]))"  # noqa
)


def split_input_string(input_string: str) -> list:
    """
    Split first on whitespace then regex each item to qualify if it needs to be
     interpreted as literal.
    """
    input_list = [
        i
        for i in re.split(
            SPLIT_PATTERN,
            str(input_string),
        )
        if i.strip()
    ]

    # Remove the '=' that are split out into their own item
    input_list = [i for i in input_list if i != '=']

    output = []
    for i in input_list:
        output.append(literal_eval(i))
    return output


def unpack_args_kwargs_string(input_string: str) -> (list, dict, list):
    """Split up based on whitespace input args and pass to unpack_args_kwargs_list."""
    input_list = split_input_string(input_string)

    args, kwargs, flags = unpack_args_kwargs_list(input_list)

    clean_kwargs = {k.replace('-', '_'): v for k, v in kwargs.items()}
    clean_flags = [i.replace('-', '_') for i in flags]

    return args, clean_kwargs, clean_flags
    # return unpack_args_kwargs_list(input_list)


def assert_if_flag(arg: str):
    FLAG_REGEX = re.compile(
        r"""^[\-|\-\-]+[a-zA-Z0-9]""",
        re.VERBOSE,
    )
    return bool(FLAG_REGEX.match(str(arg)))


def get_kwargs_till_flag(
    input_list: list, i: int, input_list_length: int
) -> (list, int):
    """
    Get the remaining kwargs till we hit another flag (ie kwarg or flag - something
     with `--` in it). Need this so that we can join the kwarg in order into a single
     string.
    """
    kwargs = []
    i += 1
    while i < input_list_length:
        raw_arg = input_list[i]
        if assert_if_flag(raw_arg):
            return ' '.join(kwargs), i - 1

        # Look ahead for if the last item is a flag
        if i + 1 > input_list_length:
            next_raw_arg = input_list[i + 1]
            if assert_if_flag(next_raw_arg):
                return ' '.join(kwargs), i
        else:
            kwargs.append(str(raw_arg))
            i += 1
    return ' '.join(kwargs), i


def unpack_args_kwargs_list(input_list: list) -> (list[DocumentValueType], dict, list):
    """Take the input_list of strings and unpack the args, kwargs, and flags."""
    input_list_length = len(input_list)
    args = []
    kwargs = {}
    flags = []

    i = 0
    while i < input_list_length:
        raw_arg = input_list[i]

        # Look ahead for if the last item is a flag
        if i + 1 < input_list_length:
            next_raw_arg = input_list[i + 1]
        else:
            # Hack for asserting if a flag - two items starting with a dash or last item
            next_raw_arg = "--hack"

        if isinstance(raw_arg, str):
            # if raw_arg.startswith('-'):
            if assert_if_flag(raw_arg):
                if isinstance(next_raw_arg, str):
                    # if next_raw_arg.startswith('-'):
                    if assert_if_flag(next_raw_arg):
                        # Field is a flag
                        flags.append(strip_dashes(raw_arg))
                    else:
                        # Field is a kwarg
                        new_kwarg, new_index = get_kwargs_till_flag(
                            input_list=input_list,
                            i=i,
                            input_list_length=input_list_length,
                        )
                        kwargs.update({strip_dashes(raw_arg): new_kwarg})
                        i = new_index
                else:
                    # Field is a kwarg
                    # TODO: Should this be part of joining logic?
                    kwargs.update({strip_dashes(raw_arg): input_list[i + 1]})
                    i += 1
            else:
                # Field is an argument
                args.append(raw_arg)
        else:
            # Field is an argument
            args.append(raw_arg)

        i += 1
    return args, kwargs, flags
