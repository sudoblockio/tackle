"""Utils."""
import copy
from functools import wraps
import errno
import os
import signal
import ast
import re


def merge_configs(default, overwrite):
    """Recursively update a dict with the key/value pair of another.

    Dict values that are dictionaries themselves will be updated, whilst
    preserving existing keys.
    """
    new_config = copy.deepcopy(default)

    for k, v in overwrite.items():
        # Make sure to preserve existing items in
        # nested dicts, for example `abbreviations`
        if isinstance(v, dict):
            new_config[k] = merge_configs(default[k], v)
        else:
            new_config[k] = v

    return new_config


# https://stackoverflow.com/a/2282656/12642712
class TimeoutError(Exception):
    """Exception for timeouts."""

    pass


def timeout(seconds=10, error_message=os.strerror(errno.ETIME)):
    """Timeout for any requests that need decorator."""

    def decorator(func):
        def _handle_timeout(signum, frame):
            raise TimeoutError(error_message)

        def wrapper(*args, **kwargs):
            signal.signal(signal.SIGALRM, _handle_timeout)
            signal.alarm(seconds)
            try:
                result = func(*args, **kwargs)
            finally:
                signal.alarm(0)
            return result

        return wraps(func)(wrapper)

    return decorator


def literal_type(input):
    """Take in any serializable argument as string and returns the literal."""
    if isinstance(input, str):
        REGEX = [
            r'^\[.*\]$',  # List
            r'^\{.*\}$',  # Dict
            r'^True$|^False$',  # Boolean
            r'^\d+$',  # Integer
            r'^[+-]?([0-9]+([.][0-9]*)?|[.][0-9]+)$',  # Float
        ]
        for r in REGEX:
            # First try to match on a list of regexs that can be evaluated by ast
            if re.match(r, input):
                """If variable looks like list, return literal list."""
                return ast.literal_eval(input)
        return input
    return input
