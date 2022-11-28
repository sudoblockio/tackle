import pytest
import subprocess
import sys

from tackle.models import (
    BaseContext,
    BaseHook,
    Context,
    JinjaHook,
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


# https://github.com/robcxyz/tackle/issues/47
# def test_imports_import_native_providers(temporary_uninstall):
#     """
#     Validate that when we uninstall requests and import native providers that the
#     imported hook is a LazyImportHook, which when the hook is used will then trigger
#     with a fallback install with the requirements and be imported directly.
#     """
#     temporary_uninstall('requests')
#     pd = ProviderHooks()
#     assert isinstance(pd['http_get'], LazyImportHook)
#     lazy_hook = pd['http_get']
#     pd.import_with_fallback_install(
#         mod_name=lazy_hook.mod_name,
#         path=lazy_hook.hooks_path,
#     )
#     assert issubclass(pd['http_get'], BaseHook)


def test_models_latest():
    """Sanity check for default checkout to latest."""
    c = Context(latest=True)
    assert c.checkout == 'latest'


def test_models_jinja_hook():
    """
    Test that wrapped_exec properly passes references to context vars such as
     public_context between a hook call.
    """
    context = BaseContext()
    context.private_hooks = Context().private_hooks
    c = JinjaHook(context=context, hook=context.private_hooks['set'])
    c.context.public_context = {}
    c.wrapped_exec(path="foo", value=1)
    assert c.context.public_context == {"foo": 1}
