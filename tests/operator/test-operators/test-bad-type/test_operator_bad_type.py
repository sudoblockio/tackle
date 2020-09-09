# -*- coding: utf-8 -*-

"""Tests dict input objects for `cookiecutter.operator.aws.ec2_meta` module."""

import os
from cookiecutter.main import cookiecutter


def test_missing_operator_fails(monkeypatch, tmpdir):
    """Verify the operator call works successfully."""
    monkeypatch.chdir(os.path.abspath(os.path.dirname(__file__)))

    stuff = None
    context = False
    try:
        stuff = cookiecutter('.', no_input=True, output_dir=str(tmpdir))
    except:  # noqa
        context = True
    assert not stuff
    assert context
