# -*- coding: utf-8 -*-

"""Tests dict input objects for `cookiecutter.prompt` module."""
import os

from cookiecutter.main import cookiecutter


def test_operator_command(monkeypatch, tmpdir):
    """Verify the operator call works successfully."""
    monkeypatch.chdir(os.path.abspath(os.path.dirname(__file__)))

    output = cookiecutter('.', no_input=True, output_dir=str(tmpdir))

    assert len(output['string_input']) == 3
    assert len(output['string_input_sorted']) == 2
    assert len(output['list_input']['dirs/dir1']) == 2
