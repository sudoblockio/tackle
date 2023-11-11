import pytest

from tackle import tackle


NON_EXEC_FIXTURES = [
    ('fields.yaml', 'foo'),
    ('method.yaml', 'foo'),
    ('args.yaml', 'bar'),
    ('args-method.yaml', 'bar'),
    ('exec.yaml', 'foo'),
    ('method-exec.yaml', 'foo'),
    ('field-hooks-exec-args.yaml', 'bar'),
    ('field-hooks-exec-args-method.yaml', 'bar'),
]


@pytest.mark.parametrize("fixture,expected_output", NON_EXEC_FIXTURES)
def test_hooks_field_default_with_hooks(fixture, expected_output):
    """Check that when a declarative hook's default is a hook that it is parsed."""
    output = tackle(fixture)

    for k, v in output['call'].items():
        assert v == expected_output


# def test_hooks_field_default_passed_context():
#     """
#     Check that when we have hooks with hooks in the default field that the context can
#      be passed between the hooks for rendering.
#     """
#     # TODO: This is no longer supported
#     output = tackle('passed-context.yaml')
#
#     assert output['f']['foo'] == 'things'
