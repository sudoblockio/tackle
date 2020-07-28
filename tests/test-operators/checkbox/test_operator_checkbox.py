# -*- coding: utf-8 -*-

"""Tests dict input objects for `cookiecutter.operator.checkbox` module."""

import os
from cookiecutter.main import cookiecutter


def test_operator_checkbox(monkeypatch, tmpdir):
    """Verify the operator call works successfully."""
    monkeypatch.chdir(os.path.abspath(os.path.dirname(__file__)))

    # TODO: Need to properly test this with pty. Tests don't cover now
    context_dict_ok = cookiecutter(
        '.', context_file='dict_ok.yaml', no_input=True, output_dir=str(tmpdir)
    )

    assert context_dict_ok

    context_string_ok = cookiecutter(
        '.', context_file='string_ok.yaml', no_input=True, output_dir=str(tmpdir)
    )

    assert context_string_ok

    context_dict_ok = cookiecutter(
        '.', context_file='dict_index.yaml', no_input=True, output_dir=str(tmpdir)
    )

    assert context_dict_ok
