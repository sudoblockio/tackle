import pytest
from ruyaml import YAML

from tackle.cli import main
from tackle import tackle

FIXTURES = [
    (
        'cli-call-func.yaml',
        'cli-call-func-output.yaml',
        'func_a',
    ),
]


@pytest.mark.parametrize("fixture,expected_output,argument", FIXTURES)
def test_hooks_model_extraction(chdir, fixture, expected_output, argument, capsys):
    main([fixture, argument, "-p"])
    output = capsys.readouterr().out

    yaml = YAML()
    with open(expected_output) as f:
        expected_output = yaml.load(f)

    assert yaml.load(output) == expected_output


# TODO: https://github.com/sudoblockio/tackle/issues/181
# This broke in 0.6.x
# @pytest.mark.parametrize("fixture,expected_output,argument", FIXTURES)
# def test_hooks_model_extraction_in_directory(
#     fixture, expected_output, argument, capsys
# ):
#     yaml = YAML()
#     with open(expected_output) as f:
#         expected_output = yaml.load(f)
#
#     os.chdir("a-dir")
#     main([fixture, argument])
#     output = capsys.readouterr().out
#
#     assert yaml.load(output) == expected_output


def test_hooks_cli_multiple_args(capsys):
    """
    When multiple args are given and there is a sincle args argument, then they are
     joined together.
    """
    main(['supplied-args-param-str.yaml', 'foo', 'bing', 'bang', '-pf', 'yaml'])
    output = capsys.readouterr().out

    assert 'bar: bing bang' in output


def test_hooks_default_hook_no_context():
    """Validate that we can run a default hook."""
    output = tackle('cli-default-hook-no-context.yaml')
    assert output['p'] == 'things'


def test_hooks_default_hook_no_context_kwargs():
    """Validate that we can run a default hook with a kwarg."""
    output = tackle('cli-default-hook-no-context.yaml', stuff='bar')
    assert output['p'] == 'bar'
    assert output['b']


def test_hooks_default_hook_no_context_flags():
    """
    Validate that flags are interpreted properly. In this case the default is true so
    when setting the flag, it should be false.
    """
    output = tackle('cli-default-hook-no-context.yaml', global_flags=['things'])
    assert isinstance(output['b'], bool)
    assert not output['b']


def test_hooks_default_hook_context():
    """Test that outer context is additionally parsed with the default hook."""
    output = tackle('cli-default-hook-context.yaml')
    assert output['p'] == 'things'
    assert output['foo'] == 'bar'


def test_hooks_default_hook_no_context_method_call():
    """Validate that we can run a default hook."""
    output = tackle('cli-default-hook-no-context.yaml', 'do')
    assert output['d'] == 'baz'


def test_hooks_default_hook_no_context_method_call_args():
    """Validate that we can run a default hook."""
    output = tackle('cli-default-hook-no-context.yaml', 'do', 'bizz')
    assert output['d'] == 'bizz'


def test_hooks_default_hook_embedded():
    """Validate that we can run a default hook embedded methods."""
    output = tackle('cli-default-hook-embedded.yaml', 'do', 'stuff', 'things')
    assert output['t'] == 'bar'


def test_hooks_default_hook_embedded_kwargs():
    """Validate that we can run a default hook embedded methods with kwargs."""
    output = tackle(
        'cli-default-hook-embedded.yaml', 'do', 'stuff', 'things', foo='bing'
    )
    assert output['t'] == 'bing'


def test_hooks_default_hook_embedded_kwargs_full():
    """Validate that we can run a default hook embedded methods with kwargs schema."""
    output = tackle('cli-default-hook-embedded.yaml', 'do', 'stuff', foo_full='bing')
    assert output['t'] == 'bing'


#############
# Non-default
#############
def test_hooks_cli_hook_arg():
    """Validate that we can run a default hook with an arg."""
    output = tackle('cli-hook-no-context.yaml', 'run')
    assert output['t'] == 'things'
    assert output['s']


def test_hooks_cli_hook_arg_args():
    """Validate that we can run a default hook with an arg."""
    output = tackle('cli-hook-no-context.yaml', 'run', 'do', 'bazzz')
    assert output['d'] == 'bazzz'
    assert output['t'] == 'things'
    assert output['s']


def test_hooks_cli_hook_arg_kwargs():
    """Validate that we can run a default hook with an arg."""
    output = tackle('cli-hook-no-context.yaml', 'run', stuff='bazzz')
    assert output['t'] == 'bazzz'
    assert output['s']


def test_hooks_cli_hook_arg_flags():
    """Validate that we can run a default hook with an arg."""
    output = tackle('cli-hook-no-context.yaml', 'run', global_flags=['things'])
    assert not output['s']


def test_hooks_hook_embedded_kwargs():
    """Validate that we can run a default hook embedded methods with kwargs."""
    output = tackle(
        'cli-default-hook-embedded.yaml', 'run', 'do', 'stuff', 'things', foo='bing'
    )
    assert output['t'] == 'bing'
