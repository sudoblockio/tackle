import pytest
import os
from tackle.main import tackle
import subprocess
import sys

from tackle.models import (
    BaseHook,
    LazyImportHook,
    import_with_fallback_install,
    import_native_providers,
)


def test_base_hook_init():
    """Test instantiating a hook."""
    inp = {
        'hook_type': 'foo',
        # 'foo': 'bar',
        'else': 'foo',
        'merge': True,
        'if': 'stuff == things',
    }

    h = BaseHook(**inp)
    # assert h.hook_type == 'foo'
    assert h.if_ == '{{stuff == things}}'
    assert h.merge
    assert isinstance(h.merge, bool)


# def test_hook_dict_match_case(caplog):
#     inp = {
#         'match': 'foo',
#         'case': ['bar', '_'],
#     }
#     h = BaseHook(**inp)
#     if sys.version_info[1] >= 10:
#         assert h.match_ == 'foo'
#
#     if sys.version_info[1] <= 10:
#         assert h.match_ is None
#
#     # TODO: Fix this test
# log_output = caplog.text
# assert 'Must be using Python' in caplog.text
@pytest.fixture()
def temporary_uninstall():
    """Fixture to uninstall a package and install it after the test."""

    def f(package):
        subprocess.check_call(
            [
                sys.executable,
                "-m",
                "pip",
                "uninstall",
                "--quiet",
                "--disable-pip-version-check",
                "-y",
                package,
            ]
        )

    return f


def test_imports_import_native_providers(temporary_uninstall):
    """
    Validate that when we uninstall requests and import native providers that the
    imported hook is a LazyImportHook, which when the hook is used will then trigger
    with a fallback install with the requirements and be imported directly.
    """
    temporary_uninstall('requests')
    pd = {}
    import_native_providers(pd)
    assert isinstance(pd['http_get'], LazyImportHook)
    lazy_hook = pd['http_get']
    import_with_fallback_install(
        provider_hook_dict=pd,
        mod_name=lazy_hook.mod_name,
        path=lazy_hook.hooks_path,
    )
    assert not isinstance(pd['http_get'], BaseHook)
