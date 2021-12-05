"""Main tests."""
import os


def test_main_cli_call(mocker, cli_runner):
    """Check the main function runs properly."""
    mock = mocker.patch("tackle.main.update_source")
    result = cli_runner("stuff")

    assert result.exit_code == 0
    assert mock.called


def test_main_cli_call_empty(change_dir, mocker, cli_runner):
    """
    Check that when no arg is given that we find the closes tackle file which
    could be in the parent directory.
    """
    mock = mocker.patch("tackle.main.update_source")
    result = cli_runner()

    assert result.exit_code == 0
    assert mock.called

    local_tackle = os.path.join(os.path.abspath('.'), '.tackle.yaml')
    assert mock.call_args.args[0].input_string == local_tackle
