"""
Utils for handling command arguments along with unpacking hook arguments. Used in cli
to unpack input args/kwargs and in parser to unpack hook calls -
i.e. key->: hook arg --kwarg thing
"""
import shlex


def strip_dashes(raw_arg: str) -> str:
    """Remove dashes prepended to string for arg splitting."""
    while raw_arg.startswith('-'):
        raw_arg = raw_arg[1:]
    return raw_arg


def unpack_input_string(input_string: str) -> (list, dict, list):
    """Unpack args and"""
    args, kwargs, flags = unpack_args_kwargs_string(input_string)
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

    return args, kwargs, flags


def unpack_args_kwargs_string(input_string: str) -> (list, dict, list):
    """Split up based on whitespace input args and pass to unpack_args_kwargs_list."""
    input_list = shlex.split(input_string)
    return unpack_args_kwargs_list(input_list)


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
        if i + 1 < input_list_length:
            next_raw_arg = input_list[i + 1]
        else:
            # Allows logic for if last item has `--` in it then it is a flag
            next_raw_arg = "-"

        if (
            raw_arg.startswith('--') or raw_arg.startswith('-')
        ) and not next_raw_arg.startswith('-'):
            # Field is a kwarg
            kwargs.update({strip_dashes(raw_arg): input_list[i + 1]})
            i += 1
        elif (
            raw_arg.startswith('--') or raw_arg.startswith('-')
        ) and next_raw_arg.startswith('-'):
            # Field is a flag
            flags.append(strip_dashes(raw_arg))
        else:
            # Field is an argument
            args.append(strip_dashes(raw_arg))
        i += 1
    return args, kwargs, flags
