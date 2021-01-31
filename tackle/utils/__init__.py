"""Utils."""
import copy
from functools import wraps
import errno
import os
import signal


# import _collections
#
# def merge_configs(base_dct, merge_dct, add_keys=True):
#     rtn_dct = base_dct.copy()
#     if add_keys is False:
#         merge_dct = {key: merge_dct[key] for key in set(rtn_dct).intersection(set(merge_dct))}
#
#     rtn_dct.update({
#         key: merge_configs(rtn_dct[key], merge_dct[key], add_keys=add_keys)
#         if isinstance(rtn_dct.get(key), dict) and isinstance(merge_dct[key], dict)
#         else merge_dct[key]
#         for key in merge_dct.keys()
#     })
#     return rtn_dct


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
