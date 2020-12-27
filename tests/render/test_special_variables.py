# -*- coding: utf-8 -*-

"""Tests dict rednering special variables."""
import os
from tackle.main import tackle


def test_special_variables(change_dir, tmpdir):
    """Verify Jinja2 time extension work correctly."""
    # monkeypatch.chdir(os.path.abspath(os.path.dirname(__file__)))

    output = tackle('test-special-variables', no_input=True, output_dir=str(tmpdir))

    assert output['calling_directory'] == os.path.dirname(__file__)
