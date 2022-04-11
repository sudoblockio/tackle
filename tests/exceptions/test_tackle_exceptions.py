import pytest

from tackle import exceptions, main


def test_should_raise_error_if_repo_does_not_exist(chdir):
    """Tackle invocation with non-exist repository should raise error."""
    chdir('/')
    with pytest.raises(exceptions.UnknownSourceException) as info:
        main.tackle('definitely-not-a-valid-repo-dir')

    assert 'definitely-not-a-valid-repo-dir' in info.value.message


def test_should_raise_error_with_calling_file(change_curdir_fixtures):
    """The correct file with error should come up in error message."""
    with pytest.raises(exceptions.UnknownSourceException) as info:
        main.tackle('calling-tackle.yaml', verbose=True)

    assert 'Error parsing input_file=\'foooooo\'' in info.value.message


FIXTURES = [
    (
        'unknown-variable.yaml',
        exceptions.UnknownTemplateVariableException,
        'fixtures/unknown-variable.yaml',
    ),
    (
        'unknown-variable-call.yaml',
        exceptions.UnknownTemplateVariableException,
        'fixtures/unknown-variable.yaml',
    ),
    (
        'unknown-variable-call-tackle.yaml',
        exceptions.UnknownTemplateVariableException,
        'fixtures/tackle.yaml',
    ),
    ('bad-extension.yaml', exceptions.UnknownTemplateVariableException, 'foobar'),
]


@pytest.mark.parametrize("fixture,exception,msg", FIXTURES)
def test_should_raise_error_fixtures(change_curdir_fixtures, fixture, exception, msg):
    """Assert right exception is raised with helper `msg`."""
    with pytest.raises(exception) as e:
        main.tackle(fixture, verbose=True)

    assert msg in e.value.message
