# -*- coding: utf-8 -*-

"""Tests dict input objects for `cookiecutter.operator.gcp.instance_meta` module."""

import os
from tackle.main import tackle


def test_operator_do_instance_meta(monkeypatch, tmpdir):
    """Verify Jinja2 time extension work correctly."""
    monkeypatch.chdir(os.path.abspath(os.path.dirname(__file__)))

    context = tackle('.', no_input=True, output_dir=str(tmpdir))

    assert len(context['instance_types']) > 1


def test_operator_do_instance_meta_instance_family(monkeypatch, tmpdir):
    """Verify Jinja2 time extension work correctly."""
    monkeypatch.chdir(os.path.abspath(os.path.dirname(__file__)))

    context = tackle(
        '.', context_file='instance_family.yaml', no_input=True, output_dir=str(tmpdir),
    )

    assert len(context['instance_types']) > 1
    assert len(context['instance_types']) < 20
    assert "gd-2vcpu-8gb" not in context['instance_types']
