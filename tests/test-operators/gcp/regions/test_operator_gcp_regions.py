# -*- coding: utf-8 -*-

"""Tests dict input objects for `cookiecutter.operator.gcp.regions` module."""

import os
from cookiecutter.main import cookiecutter


def test_operator_gcp_regions(monkeypatch, tmpdir):
    """Verify Jinja2 time extension work correctly."""
    monkeypatch.chdir(os.path.abspath(os.path.dirname(__file__)))

    context = cookiecutter('.', no_input=True, output_dir=str(tmpdir))

    assert len(context['azs']) > 1
