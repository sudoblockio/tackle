# -*- coding: utf-8 -*-

"""Tests dict input objects for `cookiecutter.operator.checkbox` module."""

import os
from cookiecutter.main import cookiecutter


def test_operator_method_when(monkeypatch, tmpdir):
    """Verify the operator call works successfully."""
    monkeypatch.chdir(os.path.abspath(os.path.dirname(__file__)))

    output = cookiecutter(
        '.', context_file='when.yaml', no_input=True, output_dir=str(tmpdir)
    )

    assert 'is_false' not in output.keys()
    assert 'is_true' in output.keys()
    assert 'list_true' in output.keys()
    assert 'list_false' not in output.keys()
