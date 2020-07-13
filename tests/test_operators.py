"""Tests for `cookiecutter.prompt` module."""

from cookiecutter.operators import *  # noqa
from cookiecutter.operators import BaseOperator


def test_no_duplicate_named_operators():
    """Verify `prompt.prompt_for_config` raises correct error."""
    operator_list = BaseOperator.__subclasses__()
    operator_types = []
    for o in operator_list:
        operator_types = operator_types + [o.type]  # noqa

    left_over_operators = set(operator_types)
    for i in operator_types:
        left_over_operators.remove(i)

    assert len(left_over_operators) == 0
    assert len(operator_types) == len(set(operator_types))
