# -*- coding: utf-8 -*-

"""Tests dict rednering special variables."""
import os
from tackle.main import tackle


def test_special_variables(change_dir):
    """Verify Jinja2 time extension work correctly."""
    output = tackle('test-special-variables', no_input=True)

    assert output['calling_directory'] == os.path.dirname(__file__)
    assert os.path.basename(output['cwd']) == 'test-special-variables'
    assert len(output) > 12


