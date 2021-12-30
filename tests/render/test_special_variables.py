"""Tests dict rendering special variables."""
from tackle.main import tackle


def test_special_variables(change_curdir_fixtures):
    """Verify Jinja2 time extension work correctly."""
    output = tackle('special-variables.yaml')
    assert len(output) > 8
