import pytest

from tackle import tackle


def test_function_default_hook_no_context_help(change_curdir_fixtures, capsys):
    """Validate that we can run a default hook's help."""
    with pytest.raises(SystemExit):
        tackle('cli-default-hook-no-context.yaml', 'help')
    out, err = capsys.readouterr()
    assert "usage: tackle" in out
    with capsys.disabled():
        print(out)


def test_function_default_hook_no_context_method_call_help(
    change_curdir_fixtures, capsys
):
    """Validate that we can run a default hook's method help."""
    with pytest.raises(SystemExit):
        tackle('cli-default-hook-no-context.yaml', 'do', 'help')
    out, err = capsys.readouterr()
    assert "usage: tackle" in out
    with capsys.disabled():
        print(out)


def test_function_cli_hook_arg_help(change_curdir_fixtures, capsys):
    """Validate that we can run a hook's with an arg."""
    with pytest.raises(SystemExit):
        tackle('cli-hook-no-context.yaml', 'run', 'help')
    out, err = capsys.readouterr()
    assert "usage: tackle" in out
    with capsys.disabled():
        print(out)


# def test_function_hook_embedded_kwargs(change_curdir_fixtures):
#     """Validate that we can run a default hook embedded methods with kwargs."""
#     output = tackle(
#         'cli-default-hook-embedded.yaml', 'run', 'do', 'stuff', 'things', foo='bing'
#     )
#     assert output['t'] == 'bing'


# def test_function_cli_hook_arg_args(change_curdir_fixtures):
#     """Validate that we can run a default hook with an arg."""
#     output = tackle('cli-hook-no-context.yaml', 'run', 'do', 'bazzz')
#     assert output['d'] == 'bazzz'
#     assert output['t'] == 'things'
#     assert output['s']
#
#
# def test_function_cli_hook_arg_kwargs(change_curdir_fixtures):
#     """Validate that we can run a default hook with an arg."""
#     output = tackle('cli-hook-no-context.yaml', 'run', stuff='bazzz')
#     assert output['t'] == 'bazzz'
#     assert output['s']
#
#
# def test_function_cli_hook_arg_flags(change_curdir_fixtures):
#     """Validate that we can run a default hook with an arg."""
#     output = tackle('cli-hook-no-context.yaml', 'run', global_flags=['things'])
#     assert not output['s']
