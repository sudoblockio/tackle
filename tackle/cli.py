"""Main `tackle` CLI."""
import sys
import argparse

from tackle import __version__
from tackle.utils.log import configure_logger
from tackle.main import tackle
from tackle.utils.command import unpack_args_kwargs_list


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
        dest='input_string',
        nargs="?",
        type=str,
        default=None,
        help="The input to parse as a source either to a local file / directory or "
        "remote location - ie github.com/robcxyz/tackle-demos or "
        "robcxyz/tackle-demos. \n"
        # "If no source is matched then the tool defaults to searching in parent "
        # "directories for a .tackle.yaml file using this argument in for running "
        # "that file.",
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
        '--override',
        '-o',
        type=str,
        default=None,
        metavar="",
        help="A string to a file to use as overrides when parsing a tackle file or "
        "some dict to use with keys to additionally use when parsing a file.",
    )
    parser.add_argument(
        '--version', action='version', version=f'tackle {__version__}'
    )

    args, unknown_args = parser.parse_known_args(raw_args)

    # Handle printing variable which isn't needed in core logic
    print_format = args.print_format
    if print_format is not None:
        print_enabled = True
        if print_format not in ['json', 'yaml', 'toml']:
            print(
                f"Invalid `--print-format` / `-pf` input \"{print_format}\". "
                f"Must be one of json (default) / yaml / toml."
            )
            sys.exit(1)
    else:
        print_enabled = args.print
        print_format = 'json'
    del args.print_format
    del args.print

    # Breakup the unknown arguments which are added later into the runtime's args/kwargs
    global_args, global_kwargs, global_flags = unpack_args_kwargs_list(unknown_args)

    configure_logger(
        stream_level='DEBUG' if getattr(args, "verbose", False) else 'INFO',
        debug_file=getattr(args, "debug_file", None),
    )

    output = tackle(
        **vars(args),
        global_args=global_args,
        global_kwargs=global_kwargs,
        global_flags=global_flags,
    )
    if print_enabled:
        if isinstance(output, (dict, list)):
            if print_format == 'json':  # noqa
                import json

                print(json.dumps(dict(output)))
            elif print_format == 'yaml':
                from ruamel.yaml import YAML

                yaml = YAML()
                yaml.dump(output, sys.stdout)
            elif print_format == 'toml':
                from toml import dumps as toml_dumps

                print(toml_dumps(dict(output)))
        else:
            print(output)


if __name__ == "__main__":
    main(sys.argv[1:])
