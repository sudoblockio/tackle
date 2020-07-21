# -*- coding: utf-8 -*-

"""Tests dict input objects for `cookiecutter.operator.aws.ec2_meta` module."""

import os
from cookiecutter.main import cookiecutter


def test_operator_terraform(monkeypatch, tmpdir):
    """Verify the operator call works successfully."""
    monkeypatch.chdir(os.path.abspath(os.path.dirname(__file__)))

    context = cookiecutter(
        '.', context_file='table_split.yaml', no_input=True, output_dir=str(tmpdir)
    )

    assert context
