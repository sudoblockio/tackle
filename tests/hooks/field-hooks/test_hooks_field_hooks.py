from typing import Type

import pytest

from tackle import exceptions, tackle


@pytest.mark.parametrize(
    "fixture,expected_output",
    [
        # ('fields.yaml', 'foo'),
        # ('method.yaml', 'foo'),
        # ('args.yaml', 'bar'),
        # ('args-method.yaml', 'bar'),
        # ('exec.yaml', 'foo'),
        ('method-compact.yaml', 'bar'),
        # ('method-exec.yaml', 'foo'),
        # ('field-hooks-exec-args.yaml', 'bar'),
        # ('field-hooks-exec-args-method.yaml', 'bar'),
        # ('multi-line.yaml', 'bar'),
    ],
)
def test_hooks_field_hooks_parameterized(fixture, expected_output):
    """Check that when a declarative hook's default is a hook that it is parsed."""
    output = tackle(fixture)

    for k, v in output['call'].items():
        assert v == expected_output


ERROR_FIXTURES: list[tuple[str, Type[Exception]]] = [
    ('error-special-keys.yaml', exceptions.HookParseException),
    ('error-raise.yaml', exceptions.HookCallException),
]


@pytest.mark.parametrize("fixture,expected_error", ERROR_FIXTURES)
def test_hooks_field_hooks_parameterized_errors(fixture, expected_error):
    """Check errors from field hooks."""
    with pytest.raises(expected_error):
        tackle(fixture)


# def test_hooks_field_default_passed_context():
#     """
#     Check that when we have hooks with hooks in the default field that the context can
#      be passed between the hooks for rendering.
#     """
#     # TODO: This is no longer supported
#     output = tackle('passed-context.yaml')
#
#     assert output['f']['foo'] == 'things'
