"""Collection of tests around loading extensions."""
import pytest

from tackle.render.environment import StrictEnvironment
from tackle.exceptions import UnknownExtension
from tackle.main import tackle
import os


def test_env_should_raise_for_unknown_extension():
    """Test should raise if extension not installed in system."""
    context = {'cookiecutter': {'_extensions': ['foobar']}}

    with pytest.raises(UnknownExtension) as err:
        StrictEnvironment(context=context, keep_trailing_newline=True)

    assert 'Unable to load extension: ' in str(err.value)


def test_env_should_come_with_default_extensions():
    """Verify default extensions loaded with StrictEnvironment."""
    env = StrictEnvironment(keep_trailing_newline=True)
    assert 'jinja2_time.jinja2_time.TimeExtension' in env.extensions
    assert 'tackle.render.extensions.JsonifyExtension' in env.extensions
    assert 'tackle.render.extensions.RandomStringExtension' in env.extensions
    assert 'tackle.render.extensions.SlugifyExtension' in env.extensions


def test_env_should_evaluate_is_defined(change_dir_main_fixtures):
    """Verify that the `is defined` works when rendering."""
    o = tackle(context_file=os.path.join('test-tackle-files', 'is_defined.yaml'), no_input=True)
    assert 'defined' in o
    assert 'not_defined' not in o
    assert 'not_defined_again' not in o
    assert 'defined_again' in o
