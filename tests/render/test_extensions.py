import pytest

from tackle import tackle


def test_render_extensions_base(change_curdir_fixtures):
    """Render non-hook extensions. Legacy from CC."""
    output = tackle('extensions.yaml')
    assert output['jsonify'].startswith('json\n"{')


def test_render_globals_base(change_curdir_fixtures):
    """Test rendering globals."""
    output = tackle('globals.yaml')
    for i in output['globals_raw']:
        assert i == 'stuff'


# https://github.com/robcxyz/tackle-box/issues/19
def test_render_globals_base_with_overlapping_context(change_curdir_fixtures):
    """
    Verify that when we have a variable in the context, for instance `namespace`, that
     we are able to render it from the context.

     This requires either:
        1. Checking the context if any of these vars exist
            - Ambiguous, could have multiple contexts to check
            - Could be
        2. Checking the renderable string for global refs
            - There are only 6 of them - could be compiled in a regex easily
            - If the global var is not called (ie namespace()), then string replace that
            - Build exception context to render the string replacement from the context

    Option 2 seems to be the cleanest.
    """
    output = tackle('globals.yaml')
    assert output


def test_render_hooks_no_args(change_curdir_fixtures):
    """Verify that we can call hooks without args."""
    output = tackle('hooks.yaml')
    assert 'tmp' in output['file']


def test_render_hooks_with_args(change_curdir_fixtures):
    """Verify that we can call hooks without args."""
    output = tackle('hooks-args.yaml')
    assert output


def test_render_hooks_with_args_too_many(change_curdir_fixtures):
    """Verify exception raised with too many args."""
    with pytest.raises(Exception):
        tackle('hooks-args-too-many-args.yaml')
