from tackle.main import tackle
from typing import Any

SPECIAL_VARIABLE_FIXTURES: list[str, str, str]


def test_special_variables(change_dir):
    """Verify Jinja2 time extension work correctly."""
    output = tackle('special-variables.yaml')
    assert len(output) > 8
