import shlex


def strip_dashes(raw_arg: str):
    while raw_arg.startswith('-'):
        raw_arg = raw_arg[1:]
    return raw_arg


def unpack_args_kwargs(input_string):
    """
    Take the input template and unpack the args and kwargs if they exist.
    Updates the command_args and command_kwargs with a list of strings and
    list of dicts respectively.
    """
    input_list = shlex.split(input_string)
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
