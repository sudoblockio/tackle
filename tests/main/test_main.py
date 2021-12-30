"""Main tests."""
import os

from tackle.cli import main


def test_main_cli_call_mock(mocker):
    """Check the main function runs properly."""
    mock = mocker.patch("tackle.main.update_source")
    main("stuff")
    assert mock.called


def test_main_cli_call_empty(change_dir, mocker):
    """
    Check that when no arg is given that we find the closes tackle file which
    could be in the parent directory.
    """
    mock = mocker.patch("tackle.main.update_source")
    main([])
    assert mock.called
    local_tackle = os.path.join(os.path.abspath('.'), '.tackle.yaml')
    assert mock.call_args.args[0].input_string == local_tackle
