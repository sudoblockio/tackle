# -*- coding: utf-8 -*-

"""Tests dict input objects for `cookiecutter.operator.list` module."""

import os
from tackle.main import tackle


def test_operator_select(monkeypatch):
    """Verify the operator call works successfully."""
    monkeypatch.chdir(os.path.abspath(os.path.dirname(__file__)))

    # TODO: Need to properly test this with pty. Tests don't cover now
    output = tackle('.', context_file='dict_ok.yaml', no_input=True)

    assert output

    output = tackle('.', context_file='string_index.yaml', no_input=True)

    assert output

    output = tackle('.', context_file='dict_index.yaml', no_input=True)

    assert output

    output = tackle('.', context_file='list_ok.yaml', no_input=True)
    assert output
