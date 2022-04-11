import pytest
from pydantic import ValidationError

from tackle import tackle
from tackle.exceptions import UnknownTemplateVariableException


def test_render_globals_base(change_curdir_fixtures):
    """
    Verify that when we have a variable in the context, for instance `namespace`, that
     we are able to render it from the context.
    """
    output = tackle('globals.yaml')
    for i in output['globals_raw']:
        assert i == 'stuff'


def test_render_hooks_with_args(change_curdir_fixtures):
    """Verify that we can call hooks without args."""
    output = tackle('hooks-args.yaml')
    assert output['get'] == 'things'
    assert output['get_sep'] == 'things'
    assert 'tmp' in output['nested']
    assert output['nested_test']['and'] == 'things'


def test_render_hooks_with_args_too_many(change_curdir_fixtures):
    """Verify exception raised with too many args."""
    with pytest.raises(Exception):
        tackle('hooks-args-too-many-args.yaml')


def test_render_hooks_missing_args(change_curdir_fixtures):
    """Verify exception raised when hook is missing / has wrong args."""
    with pytest.raises(ValidationError):
        tackle('hooks-missing-args.yaml')


def test_render_hooks_missing_ambiguous(change_curdir_fixtures):
    """Handle dealing with unknown variables the same as hooks."""
    with pytest.raises(UnknownTemplateVariableException):
        tackle('hooks-ambiguous.yaml')
