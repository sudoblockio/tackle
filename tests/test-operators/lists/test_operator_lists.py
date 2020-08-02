# -*- coding: utf-8 -*-

"""Tests dict input objects for `cookiecutter.operator.lists` module."""
import os
from cookiecutter.main import cookiecutter


def test_operator_lists(monkeypatch, tmpdir):
    """Verify the operator call works successfully."""
    monkeypatch.chdir(os.path.abspath(os.path.dirname(__file__)))

    output = cookiecutter('.', no_input=True, output_dir=str(tmpdir))

    assert 'donkey' in output['appended_list']
    assert 'donkey' in output['appended_lists']
    assert 'chickens' in output['appended_lists']
