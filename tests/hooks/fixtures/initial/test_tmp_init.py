# -*- coding: utf-8 -*-

"""Tests dict input objects for `cookiecutter.operator.lists` module."""
import os
from tackle.main import tackle


def test_tmp_init(monkeypatch, tmpdir):
    """Verify the hook call works successfully."""
    monkeypatch.chdir(os.path.abspath(os.path.dirname(__file__)))

    o = tackle('.', no_input=True, output_dir=str(tmpdir))

    assert 'foo' in o
