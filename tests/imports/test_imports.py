import os

import pytest

from tackle import exceptions, tackle
from tackle.factory import new_context
from tackle.context import Context, Source, Hooks
from tackle import imports
from tackle.settings import settings


@pytest.fixture()
def hooks():
    return Hooks(private={}, public={})


@pytest.mark.slow
def test_imports_import_hooks_from_file_python(cd, hooks):
    """Check that we can import a python hook."""
    cd("with-init")
    imports.import_hooks_from_file(
        context=Context(source=Source(), hooks=hooks),
        provider_name="foo",
        file_path="hook_2.py",
    )
    assert hooks.public['hook_2']
    imports.import_hooks_from_file(
        context=Context(source=Source(), hooks=hooks),
        provider_name="foo",
        file_path="hook_1.py",
    )
    assert hooks.private['hook_1']


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


def test_imports_exceptions_reserved_field_no_annotation(cd, hooks):
    """
    Check that when we have no annotations to a reserved field, ie is_public = "foo",
     we catch the error with context.
    """
    cd('exception-fixtures')
    with pytest.raises(exceptions.TackleHookImportException):
        imports.import_hooks_from_file(
            context=Context(source=Source()),
            provider_name="foo",
            file_path="reserved_field_no_annotation.py",
        )


# TODO: Fix this test which should fail because we do some light validation on import?
def test_imports_exceptions_reserved_field_wrong_type(cd, hooks):
    """
    Check that when we have the wrong type to a reserved field, ie
     is_public: str = "foo", we catch the error with context.
    """
    cd('exception-fixtures')
    # TODO: Fix this - need model validator (not field) to validate the subclassed
    #  fields are all the same time
    with pytest.raises(exceptions.TackleHookImportException):
        imports.import_hooks_from_file(
            context=new_context(_hooks=hooks),
            provider_name="foo",
            file_path="reserved_field_wrong_type.py",
        )
        pass


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
def test_parser_provider_import_installs_requirements(cd_fixtures, temporary_uninstall):
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


@pytest.mark.slow
def test_imports_requirements_installs_requirements(cd, temporary_uninstall):
    """Validate that if a package is missing, that it will be installed and usable."""
    cd(os.path.join('fixtures', 'test-provider-reqs'))
    temporary_uninstall('art')
    try:
        import art

        assert False
    except ImportError:
        assert True

    o = tackle()
    temporary_uninstall('art')
    assert o['art']
