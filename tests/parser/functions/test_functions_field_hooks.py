import os
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
    chdir(os.path.join('fixtures', 'field-hooks'))
    output = tackle(fixture)

    assert output['call']['literal_compact'] == expected_output
    assert output['call']['literal_expanded'] == expected_output
    assert output['call']['field_default_compact'] == expected_output


NON_EXEC_FIXTURES = [
    ('field-hooks-exec.yaml', 'foo'),
    ('field-hooks-exec-method.yaml', 'foo'),
    ('field-hooks-exec-args.yaml', 'bar'),
    ('field-hooks-exec-args-method.yaml', 'bar'),
]


@pytest.mark.parametrize("fixture,expected_output", NON_EXEC_FIXTURES)
def test_function_field_default_with_hooks_exec(chdir, fixture, expected_output):
    """Check that when a declarative hook's default is a hook that it is parsed."""
    chdir(os.path.join('fixtures', 'field-hooks'))
    output = tackle(fixture)

    assert output['call']['literal_compact_exec'] == expected_output
    assert output['call']['literal_expanded_exec'] == expected_output
    assert output['call']['field_default_compact_exec'] == expected_output
