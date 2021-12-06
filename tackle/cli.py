"""Main `tackle` CLI."""
import json
import sys
import argparse

from tackle import __version__
from tackle.exceptions import (
    FailedHookException,
    InvalidModeException,
    InvalidZipRepository,
    OutputDirExistsException,
    RepositoryCloneFailed,
    RepositoryNotFound,
    UndefinedVariableInTemplate,
    UnknownExtension,
)
from tackle.utils.log import configure_logger
from tackle.main import tackle


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
        help="The input to parse as a source either to a local file or directory or remote location - ie github.com/robcxyz/tackle-demos or robcxyz/tackle-demos.",
    )
    parser.add_argument(
        '--no-input', '-n', action='store_true', help="Do not prompt for anything."
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
        help="The file to run. Only relevent for remote sources as otherwise you can just give directly as input.",
    )

    # parser.add_argument('--verbose', '-v',  # TODO: Implement in logger?
    #                     help="Verbose mode")
    parser.add_argument(
        '--version', action='version', version=f'tackle-box {__version__}'
    )

    args, unknown_args = parser.parse_known_args(raw_args)

    # print(vars(args))
    # print(args, unknown_args)

    configure_logger(
        stream_level='DEBUG' if getattr(args, "verbose", False) else 'INFO',
        debug_file=getattr(args, "debug_file", None),
    )

    try:
        output_dict = tackle(**vars(args))

        # TODO: Print based on local format.
        print(json.dumps(dict(output_dict)))
        return output_dict
    except (
        OutputDirExistsException,
        InvalidModeException,
        FailedHookException,
        UnknownExtension,
        InvalidZipRepository,
        RepositoryNotFound,
        RepositoryCloneFailed,
    ) as e:
        print(e)
        sys.exit(1)
    except UndefinedVariableInTemplate as undefined_err:
        print('{}'.format(undefined_err.message))
        print('Error message: {}'.format(undefined_err.error.message))

        context_str = json.dumps(undefined_err.context, indent=4, sort_keys=True)
        print('Context: {}'.format(context_str))
        sys.exit(1)


if __name__ == "__main__":
    main(sys.argv[1:])
