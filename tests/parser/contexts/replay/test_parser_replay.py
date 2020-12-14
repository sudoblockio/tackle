# -*- coding: utf-8 -*-

"""Tests dict input objects for `cookiecutter.operator.lists` module."""
import os
from cookiecutter.main import cookiecutter


def test_parser_replay(monkeypatch, tmpdir):
    """Verify the hook call works successfully."""
    monkeypatch.chdir(os.path.abspath(os.path.dirname(__file__)))

    o = cookiecutter('.', no_input=True, output_dir=str(tmpdir), replay=True,)

    assert 'foo' in o
