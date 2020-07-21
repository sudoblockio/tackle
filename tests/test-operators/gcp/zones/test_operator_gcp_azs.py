# -*- coding: utf-8 -*-

"""Tests dict input objects for `cookiecutter.operator.gcp.azs` module."""

import os
from cookiecutter.main import cookiecutter


def test_operator_gcp_azs(monkeypatch, tmpdir):
    """Verify Jinja2 time extension work correctly."""
    monkeypatch.chdir(os.path.abspath(os.path.dirname(__file__)))

    context = cookiecutter(
        '.', context_file='region.yaml', no_input=True, output_dir=str(tmpdir)
    )

    assert len(context) > 1

    context = cookiecutter(
        '.', context_file='regions.yaml', no_input=True, output_dir=str(tmpdir)
    )

    assert len(context) > 1
    assert len(context['azs']['us-east1']) > 1
