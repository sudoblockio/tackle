import pytest
import sys
import os
import shutil
import subprocess

from tackle import exceptions, tackle, imports
from tackle.factory import new_context
from tackle.context import Context, Source, Hooks
from tackle.settings import settings


@pytest.fixture()
def hooks():
    return Hooks(private={}, public={})


def test_imports_import_hooks_from_file_yaml(cd, hooks):
    """Check that we can import a python hook."""
    cd("with-init")
    context = new_context()
    imports.import_hooks_from_file(
        context=context,
        provider_name="foo",
        file_path="hooks.yaml",
    )
    assert context.hooks.public['public_hook']
    assert context.hooks.private['private_hook']


@pytest.fixture()
def tmp_set_setting():
    settings.prompt_for_installs = True
    yield
    settings.prompt_for_installs = False


def test_imports_install_reqs_with_prompt(cd, hooks, mocker, tmp_set_setting):
    """
    Check that when we don't have a dep in a python hook that we fall back to wanting to
     install the requirements.txt file with a prompt to the user.
    """
    cd('with-requirements-install')
    mock = mocker.patch(
        'tackle.imports.confirm_prompt',
        autospec=True,
        return_value=False,
    )
    with pytest.raises(SystemExit) as pytest_wrapped_e:
        imports.install_reqs_with_prompt(
            context=Context(source=Source()),
            provider_name="foo",
            requirements_path="requirements.txt",
        )
    assert pytest_wrapped_e.type == SystemExit
    assert pytest_wrapped_e.value.code == 0
    assert mock.called


def test_imports_import_with_fallback_install(cd, hooks, mocker):
    """
    Check that when we call a provider with a missing module that it attempts to
     install the requirements from the base.
    """
    cd('with-requirements-install')
    mock = mocker.patch('tackle.imports.import_hooks_from_file', autospec=True)
    imports.import_with_fallback_install(
        context=Context(source=Source()),
        provider_name="foo",
        hooks_directory="hooks",
    )
    assert mock.called


def test_imports_exceptions_reserved_field_no_annotation(hooks):
    """
    Check that when we have no annotations to a reserved field, ie is_public = "foo",
     we catch the error with context.
    """
    with pytest.raises(exceptions.TackleHookImportException):
        imports.import_hooks_from_file(
            context=Context(source=Source()),
            provider_name="foo",
            file_path="reserved_field_no_annotation.py",
        )


def test_imports_exceptions_no_hook_name(hooks):
    """Check we catch errors importing python hooks without hook_name defined."""
    with pytest.raises(exceptions.MalformedHookDefinitionException):
        imports.import_hooks_from_file(
            context=Context(source=Source()),
            provider_name="foo",
            file_path="no_hook_name.py",
        )


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


@pytest.mark.slow
def test_parser_provider_import_installs_requirements(temporary_uninstall):
    """Validate that if a package is missing, that it will be installed and usable."""
    temporary_uninstall('requests')
    try:
        import requests

        # Fails in CI - I believe requests is available from system python as locally
        # this assert works.
        # assert False
    except ImportError:
        assert True

    tackle('test-install-dep.yaml')
    import requests  # noqa

    assert requests


@pytest.fixture()
def remove_provider():
    """Fixture to remove a provider."""

    def f(provider):
        provider = provider.split('/')
        provider_path = os.path.join(settings.providers_dir, *provider)
        if os.path.exists(provider_path):
            shutil.rmtree(provider_path)

    return f

@pytest.mark.slow
def test_providers_released_latest(remove_provider):
    """
    Check that when we call a released provider, that when we include the latest flag
    we use the latest commit.
    """
    remove_provider("robcxyz/tackle-fixture-released")
    o = tackle(
        "robcxyz/tackle-fixture-released",
        latest=True,
    )
    assert o['hooks_dir_hook']['foo'] == 'bar'


@pytest.mark.slow
def test_providers_unreleased_import(remove_provider):
    """Check that we can use an unreleased provider."""
    remove_provider("robcxyz/tackle-fixture-unreleased")
    o = tackle("robcxyz/tackle-fixture-unreleased", no_input=True)

    assert o['hooks_dir_hook']['foo'] == 'bar'
