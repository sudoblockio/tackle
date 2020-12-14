# -*- coding: utf-8 -*-

"""Tests dict input objects for `cookiecutter.provider.azure.hooks` module."""
from cookiecutter.main import cookiecutter


def test_operator_azure_regions(change_dir):
    """Verify the operator call works successfully."""
    context = cookiecutter('.', context_file='regions.yaml')
    assert len(context['azs']) > 1


def test_operator_azure_vm_meta(change_dir):
    """Verify the operator call works successfully."""
    context = cookiecutter('.', context_file='instance_types.yaml')

    assert len(context['instance_types']) > 1


def test_operator_azure_vm_meta_instance_family(change_dir):
    """Hook returns instance types filtered on family."""
    context = cookiecutter('.', context_file='instance_family.yaml')

    assert len(context['instance_types']) > 1
    assert len(context['instance_types']) < 150
