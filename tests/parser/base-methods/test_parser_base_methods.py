import pytest

from tackle import exceptions, tackle


def test_parser_methods_chdir():
    """Go into a dir and read a file and verify its output."""
    output = tackle('chdir.yaml')

    assert output['normal']['foo'] == 'bar'
    assert output['aliased']['foo'] == 'bar'


def test_parser_methods_chdir_loop():
    """In a loop, go into a dir and read two files and verify output."""
    output = tackle('chdir-loop.yaml')

    assert output['stuff'] == [{'foo': 'bar'}, {'foo': 'baz'}]


def test_parser_methods_chdir_error():
    """Raise when dir not found."""
    with pytest.raises(exceptions.HookUnknownChdirException):
        tackle('chdir-error.yaml')


def test_parser_methods_try():
    """Use try which should not have any output"""
    output = tackle('try.yaml')

    assert output == {}


def test_parser_methods_except():
    """Use try which should not have any output"""
    output = tackle('except.yaml')

    assert output['compact'] == 'foo'
    assert output['str'] == 'foo'
    assert output['dic']['stuff'] == '{{stuff}}'
    assert output['dict_render_block'] == {'stuff': '{{stuff}}'}
    assert output['stuff'] == 'things'
    assert output['listed']['hook_call'][1]['stuff'] == 'things'


def test_parser_methods_skip_output(cd):
    """Setting skip_output in a hook definition results in no output."""
    # TODO: Fix me later - consequence of bad memory model
    cd('skip-output')
    output = tackle('skip-output.yaml')

    assert output
