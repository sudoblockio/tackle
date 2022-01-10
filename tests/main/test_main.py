"""Main tests."""
import os
import sys

import pytest

from tackle import tackle
from tackle.cli import main
from tackle.exceptions import NoInputOrParentTackleException


def test_main_cli_call_mock(mocker):
    """Check the main function runs properly."""
    mock = mocker.patch("tackle.main.update_source")
    main("stuff")
    assert mock.called


def test_main_cli_call_empty(change_curdir_fixtures, mocker):
    """
    Check that when no arg is given that we find the closes tackle file which
    could be in the parent directory.
    """
    mock = mocker.patch("tackle.main.update_source")
    main([])
    assert mock.called
    local_tackle = os.path.join(os.path.abspath('.'), '.tackle.yaml')

    if sys.version_info.minor > 7:
        assert mock.call_args.args[0].input_string == local_tackle
    # test was failing in 3.7/6
    else:
        assert mock.call_args[0][0].input_string == local_tackle


def test_main_cli_call_empty_no_parent_tackle_raises(chdir):
    """
    Check that when no arg is given that we find the closes tackle file which
    could be in the parent directory.
    """
    if os.name != 'nt':
        chdir('/')
    else:
        chdir('\\')
    with pytest.raises(NoInputOrParentTackleException):
        tackle()


def test_main_input_dict(change_curdir_fixtures):
    """
    Test bringing in an input dict along with a target which should be interpreted as
    overriding keys to the target.
    """
    input_dict = {
        'this': 1,
        'that': 2,
        'stuff': 'things',  # Missing key
        'foo': 2,  # Non-hook key
    }

    output = tackle('dict-input.yaml', **input_dict)
    assert output['this'] == 1


def test_main_from_cli_input_dict(change_curdir_fixtures, capsys):
    """Test same as above but from command line."""
    main(["dict-input.yaml", "--this", "1", "--that", "2", "--print"])
    assert 'this' in capsys.readouterr().out
