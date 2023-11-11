"""Main tests."""
import pytest
import os
import sys

from tackle import tackle
from tackle.cli import main
from tackle import exceptions


def test_main_cli_call_mock(mocker):
    """Check the main function runs properly."""
    mock = mocker.patch("tackle.main.parse_context")
    main("stuff")
    assert mock.called


def test_main_cli_call_empty(mocker):
    """
    Check that when no arg is given that we find the closes tackle file which
    could be in the parent directory.
    """
    mock = mocker.patch("tackle.main.parse_context")
    main([])
    assert mock.called
    local_tackle = os.path.join(os.path.abspath('.'), '.tackle.yaml')

    if sys.version_info.minor > 7:
        assert mock.call_args.args[0].path.calling.file == local_tackle
    # test was failing in 3.7/6
    else:
        assert mock.call_args[0][0].path.calling.file == local_tackle


def test_main_cli_call_empty_no_parent_tackle_raises(cd):
    """
    Check that when no arg is given that we find the closes tackle file which
    could be in the parent directory.
    """
    if os.name != 'nt':
        cd('/')
    else:
        cd('\\')
    with pytest.raises(exceptions.UnknownSourceException):
        tackle()


def test_main_input_dict_to_overrides(mocker):
    """
    Test bringing in an input dict along with a target which should be interpreted as
     overriding keys to the target.
    """
    mock = mocker.patch("tackle.main.parse_context")
    input_dict = {'this': 1}

    ctx = tackle(return_context=True, **input_dict)
    assert mock.called
    assert ctx.data.overrides == input_dict



def test_main_overrides_str(cd_fixtures):
    """Test that we can override inputs."""
    o = tackle("dict-input.yaml", overrides="dict-input-overrides.yaml")
    # Should normally throw error with prompt
    assert o['this'] == "stuff"
    # Again, should raise error w/o override
    main(["dict-input.yaml", "--override", "dict-input-overrides.yaml"])


@pytest.mark.parametrize("input_file", [
    "func-input.yaml",
    "func-exec-input.yaml",
])
def test_main_overrides_str_for_func(cd_fixtures, input_file):
    """Test that we can override inputs for a default hook."""
    o = tackle(input_file, overrides="dict-input-overrides.yaml")
    # Should normally throw error with prompt
    assert o['this'] == "stuff"


def test_main_overrides_str_for_block(cd_fixtures):
    """Test that we can override inputs in a block."""
    o = tackle("block-input.yaml", overrides="block-input-overrides.yaml")
    # Should normally throw error with prompt
    assert o['foo']['this'] == "stuff"
    assert o['bar'] == 'baz'


def test_main_overrides_str_not_found_error(cd_fixtures):
    """Test that we get error on ."""
    with pytest.raises(exceptions.UnknownInputArgumentException):
        tackle("dict-input.yaml", override="not-exists")
