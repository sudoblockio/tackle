# -*- coding: utf-8 -*-

"""Tests dict input objects for `cookiecutter.operator.gcp.instance_meta` module."""

import os
from cookiecutter.main import cookiecutter


def test_operator_gcp_instance_meta(monkeypatch, tmpdir):
    """Verify Jinja2 time extension work correctly."""
    monkeypatch.chdir(os.path.abspath(os.path.dirname(__file__)))

    context = cookiecutter('.', no_input=True, output_dir=str(tmpdir))

    assert len(context['instance_types']) > 1


def test_operator_gcp_instance_meta_instance_family(monkeypatch, tmpdir):
    """Verify Jinja2 time extension work correctly."""
    monkeypatch.chdir(os.path.abspath(os.path.dirname(__file__)))

    context = cookiecutter(
        '.', context_file='instance_family.yaml', no_input=True, output_dir=str(tmpdir),
    )

    assert len(context['instance_types']) > 1
    assert len(context['instance_types']) < 75
    assert "n2d-standard-2" not in context['instance_types']
