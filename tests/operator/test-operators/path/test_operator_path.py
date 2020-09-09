# -*- coding: utf-8 -*-

"""Tests dict input objects for `cookiecutter.operator.block` module."""
import os
from cookiecutter.main import cookiecutter


def test_operator_path(monkeypatch, tmpdir):
    """Verify the operator call works successfully."""
    monkeypatch.chdir(os.path.abspath(os.path.dirname(__file__)))

    context = cookiecutter('.', no_input=True, output_dir=str(tmpdir))

    assert context['path_isdir']

    assert context['path_exists']
    assert os.path.exists(context['find_in_parent_dir'])  # Should be tests/tests...
    assert os.path.exists(context['find_in_parent_file'])
    assert context['find_in_parent_fallback'] == context['find_in_parent_dir']
