# -*- coding: utf-8 -*-

"""Tests dict rednering special variables."""
import os
from tackle.main import tackle


def test_special_variables(change_curdir_fixtures):
    """Verify Jinja2 time extension work correctly."""
    output = tackle('special-variables.yaml')

    assert output['calling_directory'] == os.path.dirname(__file__)
    assert len(output) > 8
