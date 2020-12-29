"""Collection of tests around common path and url shorthands."""
import pytest

from tackle.models import DEFAULT_ABBREVIATIONS
from tackle.repository import expand_abbreviations


@pytest.mark.parametrize(
    ('template', 'abbreviations', 'expected_result'),
    [
        ('foo', {'foo': 'bar'}, 'bar'),
        ('baz', {'foo': 'bar'}, 'baz'),
        ('xx:a', {'xx': '<{0}>'}, '<a>'),
        ('gh:a', {'gh': '<{0}>'}, '<a>'),
        ('xx:a', {'xx': '<>'}, '<>'),
        (
            'gh:pydanny/cookiecutter-django',
            DEFAULT_ABBREVIATIONS,
            'https://github.com/pydanny/cookiecutter-django.git',
        ),
        (
            'gl:pydanny/cookiecutter-django',
            DEFAULT_ABBREVIATIONS,
            'https://gitlab.com/pydanny/cookiecutter-django.git',
        ),
        (
            'bb:pydanny/cookiecutter-django',
            DEFAULT_ABBREVIATIONS,
            'https://bitbucket.org/pydanny/cookiecutter-django',
        ),
    ],
    ids=(
        'Simple expansion',
        'Skip expansion (expansion not an abbreviation)',
        'Expansion prefix',
        'expansion_override_builtin',
        'expansion_prefix_ignores_suffix',
        'Correct expansion for builtin abbreviations (github)',
        'Correct expansion for builtin abbreviations (gitlab)',
        'Correct expansion for builtin abbreviations (bitbucket)',
    ),
)
def test_abbreviation_expansion(template, abbreviations, expected_result):
    """Verify abbreviation unpacking."""
    expanded = expand_abbreviations(template, abbreviations)
    assert expanded == expected_result


def test_abbreviation_expansion_prefix_not_0_in_braces():
    """Verify abbreviation unpacking raises error on incorrect index."""
    with pytest.raises(IndexError):
        expand_abbreviations('xx:a', {'xx': '{1}'})
