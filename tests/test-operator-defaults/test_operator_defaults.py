# -*- coding: utf-8 -*-

"""Tests dict input objects for `cookiecutter.operator.aws.azs` module."""

import os
from cookiecutter.main import cookiecutter


def test_operato_defaults(monkeypatch, tmpdir):
    """Verify Jinja2 time extension work correctly."""
    monkeypatch.chdir(os.path.abspath(os.path.dirname(__file__)))

    output = cookiecutter(
        '.', no_input=True, output_dir=str(tmpdir), config_file='config.yaml'
    )

    assert output['list'] == 'cats'
