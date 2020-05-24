# -*- coding: utf-8 -*-

"""Tests operator base for `cookiecutter.operator` module."""
import pytest

from cookiecutter.operator import Operators

def test_operator_types():
    """Verify `prompt_for_config` call `read_user_variable` on dict request."""

    o = Operators()
    assert len(o.types) > 1
    assert len(o.types) > len(o.operators)

    





