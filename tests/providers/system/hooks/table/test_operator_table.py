# -*- coding: utf-8 -*-

"""Tests dict input objects for `cookiecutter.operator.aws.ec2_meta` module."""

import os
from cookiecutter.main import cookiecutter


def test_provider_system_hook_terraform(change_dir):
    """Verify the hook call works properly."""
    monkeypatch.chdir(os.path.abspath(os.path.dirname(__file__)))

    context = cookiecutter(
        '.', context_file='table_split.yaml', no_input=True, output_dir=str(tmpdir)
    )

    assert context
