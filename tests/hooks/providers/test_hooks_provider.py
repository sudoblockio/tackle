"""
Tests associated with calling hooks from provider (ie importing hooks from `hooks` dir).
Note: This tests a lot of logic from parser.py but is generally focused on how providers
 are called.
"""
import os

import pytest

from tackle import tackle
from tackle.cli import main

FIXTURES: list[tuple[str, list]] = [
    # exec_dir,args
    ('inline', []),
    (os.path.join('inline', 'a-dir'), []),
    ('default-hook', []),
    (os.path.join('default-hook', 'a-dir'), []),
    ('exec-hook', ['bar']),
    (os.path.join('exec-hook', 'a-dir'), ['bar']),
    ('method', ['foo', 'bar']),
    (os.path.join('method', 'a-dir'), ['foo', 'bar']),
    ('only-hooks-dir', ['foo', 'bar']),
    (os.path.join('only-hooks-dir', 'a-dir'), ['foo', 'bar']),
]


@pytest.mark.parametrize("exec_dir,args", FIXTURES)
def test_hooks_provider_import_hook_from_hooks_dir(exec_dir, args):
    """Assert that we can call a dcl hook from local hooks dir and an embedded dir."""
    os.chdir(exec_dir)
    output = tackle(*args)

    assert output['call_compact']['compact_out'] == 'a-default'
    assert output['call_compact']['full_out'] == 'a-default'
    assert output['call_compact_kwarg']['compact_out'] == 'foo'
    assert output['call_compact_kwarg_rendered']['rendered_by_default_out'] == 'things'
    assert output['call_compact_arg']['full_out'] == 'foo'

    assert output['jinja_extension_default']['compact_out'] == 'a-default'
    assert output['jinja_extension_default']['full_out'] == 'a-default'
    assert output['jinja_extension_arg']['full_out'] == 'foo'
    assert output['jinja_extension_kwarg']['compact_out'] == 'foo'
    assert output['jinja_extension_kwarg']['full_out'] == 'a-default'


def test_hooks_import_func_from_hooks_dir_method_main():
    """Check running a method in a hook via main."""
    os.chdir(os.path.join('method', 'a-dir'))
    main(['a_funky'])
