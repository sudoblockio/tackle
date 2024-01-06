import pytest

from tackle import exceptions, tackle
from tackle.factory import new_context
from tackle.parser import parse_context

LOCAL_FIXTURES = [
    'local-expanded.yaml',
    'special-key-local-str.yaml',
    'special-key-local-dict.yaml',
    'special-key-local-list.yaml',
    'special-key-local-list-str.yaml',
]


@pytest.mark.parametrize("target", LOCAL_FIXTURES)
def test_provider_system_hook_import_local(target):
    """Run the source and check that the hooks imported the demo module."""
    context = new_context(target)

    num_private_providers = len(context.hooks.private.keys())
    num_public_providers = len(context.hooks.public.keys())
    parse_context(context=context)

    assert num_private_providers < len(context.hooks.private.keys())
    assert num_public_providers < len(context.hooks.public.keys())
    # Check that we aren't just importing hooks from base of repo
    assert 'test' not in context.hooks.public
    assert 'thing' in context.hooks.private
    assert 'tackle' not in context.hooks.private


@pytest.mark.slow
@pytest.mark.parametrize(
    "target",
    [
        'special-key-remote-str.yaml',
        'special-key-remote-dict.yaml',
        'special-key-remote-list.yaml',
        'special-key-remote-list-str.yaml',
        'remote-list-dict.yaml',
        'remote-list-str-no-args.yaml',
    ],
)
def test_provider_system_hook_import_remote(target):
    """Run the source and check that the hooks imported the demo module."""
    context = new_context(target)

    num_private_providers = len(context.hooks.private.keys())
    num_public_providers = len(context.hooks.public.keys())
    parse_context(context=context)

    assert num_private_providers < len(context.hooks.private.keys())
    assert num_public_providers < len(context.hooks.public.keys())
    # Check that we aren't just importing hooks from base of repo
    assert 'gen_docs' not in context.hooks.public
    assert 'tackle' not in context.hooks.private


def test_provider_system_hook_import_local_file():
    output = tackle('local-file.yaml')

    assert output['call']['foo'] == 'bar'


def test_provider_system_hook_import_local_assert():
    """Assert local import of hook is valid."""
    o = tackle('local-expanded.yaml')
    assert o['stuff'] == 'thing'


def test_provider_hook_import_raise_when_calling_hook_from_tackle_file():
    """
    Even though a hook called `unexported_hook` exists in tackle file, it should not be
     imported via `import` hook.
    """
    with pytest.raises(exceptions.UnknownHookTypeException):
        tackle('local-with-calling-hook-in-tackle-file.yaml')


@pytest.mark.slow
@pytest.mark.parametrize(
    "input_file,expected_exception",
    [
        ('error-not-found-local.yaml', exceptions.UnknownSourceException),
        (
            'error-not-found-repo.yaml',
            (exceptions.RepositoryNotFound, exceptions.GenericGitException),
        ),
    ],
)
def test_provider_hook_import_raise_unknown_source(input_file, expected_exception):
    """When given a bad source we raise an error."""
    with pytest.raises(expected_exception):
        tackle(input_file)


@pytest.mark.parametrize(
    "file",
    [
        'error-str-both-version-latest.yaml',
        'error-dict-both-version-latest.yaml',
        'error-list-both-version-latest.yaml',
        'error-list-str-both-version-latest.yaml',
        'error-list-str-extra-flag.yaml',
        'error-list-str-extra-kwarg.yaml',
        'error-list-str-unknown-flag.yaml',
    ],
)
def test_provider_hook_import_raise_when_both_version_and_latest(file):
    """
    Even though a hook called `unexported_hook` exists in tackle file, it should not be
     imported via `import` hook.
    """
    with pytest.raises(exceptions.TackleHookImportException):
        tackle(file)
