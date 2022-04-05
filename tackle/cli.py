"""Main `tackle` CLI."""
import json
import sys
import argparse

from tackle import __version__
from tackle.utils.log import configure_logger
from tackle.main import tackle
from tackle.utils.command import unpack_args_kwargs_list


def main(raw_args=None):
    """Run a tackle box."""
    if raw_args is None:
        raw_args = sys.argv[1:]

    parser = argparse.ArgumentParser(description="Tackle Box")

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
        '--checkout',
        '-c',
        dest='checkout',
        type=str,
        metavar="",
        help="The branch or version to checkout if a remote source is given.",
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
        help="The file to run. Only relevent for remote sources as otherwise you can just give full path to file as input.",
    )
    parser.add_argument(
        '--find-in-parent',
        '-fp',
        action='store_true',
        help="Search for target in parent directory. Only relevant for local targets.",
    )
    parser.add_argument(
        '--version', action='version', version=f'tackle-box {__version__}'
    )

    args, unknown_args = parser.parse_known_args(raw_args)

    # Handle printing variable which isn't needed in core logic
    print_enabled = args.print
    del args.print

    # Breakup the unknown arguments which are added later into the runtime's args/kwargs
    global_args, global_kwargs, global_flags = unpack_args_kwargs_list(unknown_args)

    configure_logger(
        stream_level='DEBUG' if getattr(args, "verbose", False) else 'INFO',
        debug_file=getattr(args, "debug_file", None),
    )

    output_dict = tackle(
        **vars(args),
        global_args=global_args,
        global_kwargs=global_kwargs,
        global_flags=global_flags,
    )
    if print_enabled:
        print(json.dumps(dict(output_dict)))


if __name__ == "__main__":
    main(sys.argv[1:])
