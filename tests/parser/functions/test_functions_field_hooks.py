import pytest

from tackle import tackle

NON_EXEC_FIXTURES = [
    ('field-hooks.yaml', 'foo'),
    ('field-hooks-method.yaml', 'foo'),
    ('field-hooks-args.yaml', 'bar'),
    ('field-hooks-args-method.yaml', 'bar'),
]


@pytest.mark.parametrize("fixture,expected_output", NON_EXEC_FIXTURES)
def test_function_field_default_with_hooks(chdir, fixture, expected_output):
    """Check that when a declarative hook's default is a hook that it is parsed."""
    chdir('field-hooks-fixtures')
    output = tackle(fixture)

    assert output['call']['literal_compact'] == expected_output
    assert output['call']['literal_expanded'] == expected_output
    assert output['call']['field_default_compact'] == expected_output


EXEC_FIXTURES = [
    ('field-hooks-exec.yaml', 'foo'),
    ('field-hooks-exec-method.yaml', 'foo'),
    ('field-hooks-exec-args.yaml', 'bar'),
    ('field-hooks-exec-args-method.yaml', 'bar'),
]


@pytest.mark.parametrize("fixture,expected_output", EXEC_FIXTURES)
def test_function_field_default_with_hooks_exec(chdir, fixture, expected_output):
    """Check that when a declarative hook's default is a hook that it is parsed."""
    chdir('field-hooks-fixtures')
    output = tackle(fixture)

    assert output['call']['literal_compact_exec'] == expected_output
    assert output['call']['literal_expanded_exec'] == expected_output
    assert output['call']['field_default_compact_exec'] == expected_output


def test_function_field_default_with_hooks_extends(chdir):
    """
    Check that extending a hook works when using a hooks directory with hook field
     default.
    """
    chdir('field-hooks-fixtures')
    output = tackle('extends.yaml')

    assert output['call']['literal_compact'] == 'foo'
    assert output['call']['literal_expanded'] == 'foo'
    assert output['call']['field_default_compact'] == 'foo'


def test_function_field_default_passed_context(chdir):
    """
    Check that when we have hooks with hooks in the default field that the context can
     be passed between the hooks for rendering.
    """
    chdir('field-hooks-fixtures')
    output = tackle('passed-context.yaml')

    assert output['f']['foo'] == 'things'
