import pytest

from tackle.main import tackle
from tackle.utils.files import read_config_file


def test_parser_duplicate_values(cd_fixtures):
    """
    Validate that when we give a hook with duplicate values as what was set in the
     initial run (ie a tackle hook with `no_input` set), that we take the value from the
     hook.
    """
    output = tackle('duplicate-values.yaml', verbose=True)
    assert output['local']['two_args']


def test_parser_hook_args_not_copied(cd_fixtures):
    """
    When calling a hook with an arg, there was an issue with the hook's args being
     copied from one hook call to the next of the same hook suggesting the hook was not
     copied when called. This is to check that.
    """
    output = tackle('copied-hook-args.yaml')
    assert output['upper'].isupper()
    assert output['lower'].islower()
    assert output['lower_default'].islower()
