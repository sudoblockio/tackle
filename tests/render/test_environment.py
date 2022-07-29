"""Collection of tests around loading extensions."""
from tackle.main import tackle
from tackle.models import Context


def test_env_should_come_with_default_extensions():
    """Verify default extensions loaded with StrictEnvironment."""
    c = Context()
    assert 'capitalize' in c.env_.filters
    # TODO: Reassess when adding back filters?
    # assert 'json' in c.env_.filters
    # assert 'get' in c.env_.filters


def test_env_should_evaluate_is_defined(change_curdir_fixtures):
    """Verify that the `is defined` works when rendering."""
    o = tackle('is-defined.yaml', no_input=True)
    assert 'defined' in o
    assert 'not_defined' not in o
    assert 'not_defined_again' not in o
    assert 'defined_again' in o
