"""Main `tackle` CLI."""
import sys
import argparse

from tackle import tackle, __version__
from tackle.utils.log import configure_logger
from tackle.utils.command import unpack_args_kwargs_list
from tackle.context import Context


def _validate_print_format(print_format: str):
    if print_format not in ['json', 'yaml', 'yml', 'toml']:
        print(
            f"Invalid `--print-format` / `-pf` input \"{print_format}\". "
            f"Must be one of json (default) / yaml / toml."
        )
        sys.exit(1)


def print_public_data(context: 'Context', print_format: str):
    output = context.data.public
    if print_format is None:
        if context.source.file is not None:
            print_format = context.source.file.split('.')[-1]
            _validate_print_format(print_format=print_format)
        else:
            # Assume yaml?
            print_format = 'yaml'

    if isinstance(output, (dict, list)):
        if print_format == 'json':  # noqa
            import json

            print(json.dumps(output))
        elif print_format in ['yaml', 'yml']:
            from ruyaml import YAML

            yaml = YAML()
            yaml.dump(output, sys.stdout)
        elif print_format == 'toml':
            # From https://realpython.com/python-toml/#load-toml-with-python
            try:
                from tomli import dumps as toml_dumps
            except ModuleNotFoundError:
                from tomllib import dumps as toml_dumps

            print(toml_dumps(output))
    else:
        # Simply a value - not object or array
        print(output)


def main(raw_args=None):
    """Run a tackle."""
    if raw_args is None:
        raw_args = sys.argv[1:]

    parser = argparse.ArgumentParser(
        description="tackle is a DSL for creating declarative CLIs. Call tackle "
                    "against files, directories, or repos with yaml/toml/json tackle "
                    "files."
    )

    parser.add_argument(
        dest='inputs',
        nargs="?",
        type=str,
        default=None,
        help="Inputs to tackle in the form of args, key value arguments or flags. The "
             "first argument is typically pointing to a tackle provider which can be "
             "local files/directories or remote (ie github_org/repo). If no source is "
             "matched then the tool defaults to searching in parent directories for a "
             "tackle file (ie ./[.]tackle.[yaml|json|toml]). The remaining arguments "
             "and flags are passed in to the tackle call for calling hooks within the "
             "target tackle provider.",
    )
    parser.add_argument(
        '--no-input',
        '-n',
        action='store_true',
        help="Do not prompt for anything resulting in default choices.",
    )
    parser.add_argument(
        '--verbose', '-v', action='store_true', help="Execute in verbose mode."
    )
    parser.add_argument(
        '--checkout',
        '-c',
        dest='checkout',
        type=str,
        metavar="",
        help="The branch or version to checkout if a remote source is given.",
    )
    parser.add_argument(
        '--latest',
        '-l',
        action='store_true',
        help="When using version controlled providers (ie in github), use the latest "
             "commit in the default branch.",
    )
    parser.add_argument(
        '--directory',
        '-d',
        default=None,
        type=str,
        metavar="",
        help="The directory to run from if given a remote source.",
    )
    parser.add_argument(
        '--file',
        '-f',
        type=str,
        metavar="",
        dest="context_file",
        help="The file to run. Only relevent for remote sources as otherwise you can "
             "just give full path to file as input.",
    )
    parser.add_argument(
        '--find-in-parent',
        '-fp',
        action='store_true',
        help="Search for target in parent directory. Only relevant for local targets.",
    )
    parser.add_argument(
        '--hooks-dir',
        '-hd',
        type=str,
        default=None,
        metavar="",
        help="Path to hooks directory to import.",
    )
    parser.add_argument(
        '--override',
        '-o',
        type=str,
        default=None,
        metavar="",
        help="A string to a file to use as overrides when parsing a tackle file or "
             "some dict to use with keys to additionally use when parsing a file.",
    )
    # Args that are not passed into main
    parser.add_argument(
        '--print', '-p', action='store_true', help="Print the resulting output."
    )
    parser.add_argument(
        '--print-format',
        '-pf',
        default=None,
        dest='print_format',
        type=str,
        metavar="",
        help="The format to print to output. Defaults to json.",
    )
    parser.add_argument('--version', action='version', version=f'tackle {__version__}')

    # Decompose args. Unknown args are later passed in as `global_[args|kwargs|flags]`
    # to be consumed by the tackle script.
    args, unknown_args = parser.parse_known_args(raw_args)
    expanded_unknown_args = []
    for v in unknown_args:
        # Unknown args are not split up based on `=` so we need to do that manually
        if '=' in v:
            split_args = v.split('=')
            if len(split_args) != 2:
                raise Exception(f"The input `{v}` is malformed.")
            expanded_unknown_args += split_args
        else:
            expanded_unknown_args.append(v)

    # Unpack into global_ vars
    input_args, input_kwargs, input_flags = unpack_args_kwargs_list(
        input_list=expanded_unknown_args,
    )

    # Hack to take the first arg and make a list of args with every unknown arg
    input_args = [args.inputs] + input_args
    input_kwargs.update({i: True for i in input_flags})  # Same for kwargs

    # Handle printing variable which isn't needed in core logic
    print_format = args.print_format
    if print_format is not None:
        print_enabled = True
        _validate_print_format(print_format=print_format)
    else:
        print_enabled = args.print
        print_format = None  # Gathered later from context.source.file extension

    configure_logger(
        stream_level='DEBUG' if getattr(args, "verbose", False) else 'INFO',
        debug_file=getattr(args, "debug_file", None),
    )

    context = tackle(
        *input_args,
        **input_kwargs,
        # input_string=args.input_string,
        checkout=args.checkout,
        latest=args.latest,
        directory=args.directory,
        # file=args.file,
        find_in_parent=args.find_in_parent,
        return_context=True
    )

    if print_enabled:
        print_public_data(context=context, print_format=print_format)


if __name__ == "__main__":
    main(sys.argv[1:])
