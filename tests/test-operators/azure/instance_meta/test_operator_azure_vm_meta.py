# -*- coding: utf-8 -*-

"""Tests dict input objects for `cookiecutter.operator.azure.vm_meta` module."""

import os
from cookiecutter.main import cookiecutter


def test_operator_azure_vm_meta(monkeypatch, tmpdir):
    """Verify the operator call works successfully."""
    monkeypatch.chdir(os.path.abspath(os.path.dirname(__file__)))

    context = cookiecutter('.', no_input=True, output_dir=str(tmpdir))

    assert len(context['instance_types']) > 1


def test_operator_azure_vm_meta_instance_family(monkeypatch, tmpdir):
    """Verify the operator call works successfully."""
    monkeypatch.chdir(os.path.abspath(os.path.dirname(__file__)))

    context = cookiecutter(
        '.', context_file='instance_family.yaml', no_input=True, output_dir=str(tmpdir),
    )

    assert len(context['instance_types']) > 1
    assert len(context['instance_types']) < 150
