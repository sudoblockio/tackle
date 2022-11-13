"""
Utils for handling command arguments along with unpacking hook arguments. Used in cli
to unpack input args/kwargs and in parser to unpack hook calls -
i.e. key->: hook arg --kwarg thing
"""
import ast
import re


def strip_dashes(raw_arg: str) -> str:
    """Remove dashes prepended to string for arg splitting."""
    while raw_arg.startswith('-'):
        raw_arg = raw_arg[1:]
    return raw_arg


def literal_eval(input):
    """
    Wrapper for ast.literal eval that accounts for hex and bools which it normally
     coerces to int/string respectively.
    """
    if isinstance(input, str) and input.startswith('0x'):
        # Prevent hex from being coerced to int type
        return input
    else:
        try:
            return ast.literal_eval(input)
        except (ValueError, SyntaxError):
            # Fix ast.literal_eval coercing bools to strings
            if input == 'true':
                return True
            elif input == 'false':
                return False
            else:
                return input


def split_input_string(input_string: str) -> list:
    """
    Split first on whitespace then regex each item to qualify if it needs to be
    interpreted as literal.
    """
    # Inspired from https://stackoverflow.com/a/524796/12642712
    # Split on whitespace or `=`
    # When quotes are preceded by `,:{[(=`, ignore
    # Don't split between quotes with `,:]})`
    # Otherwise split on quotes
    # Repeated for single quotes
    input_list = [
        i
        for i in re.split(
            "( |(?<!,|\:|\(|\{|\[|=)\\\"(?!\,|\:|\)|\}|\]).*?\\\"(?!\}|\])|(?<!\,|\:|\(|\{|\[|=)'(?!,|\:|\)|\}|\]).*?'(?!\}|\]))",  # noqa
            input_string,
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
    return unpack_args_kwargs_list(input_list)


def assert_if_flag(arg: str):
    FLAG_REGEX = re.compile(
        r"""^[\-|\-\-]+[a-zA-Z0-9]""",
        re.VERBOSE,
    )
    return bool(FLAG_REGEX.match(arg))


def unpack_args_kwargs_list(input_list: list) -> (list, dict, list):
    """
    Take the input template and unpack the args and kwargs if they exist.
    Updates the command_args and command_kwargs with a list of strings and
    list of dicts respectively.
    """
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
                        kwargs.update({strip_dashes(raw_arg): input_list[i + 1]})
                        i += 1
                else:
                    # Field is a kwarg
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
