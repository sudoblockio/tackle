# -*- coding: utf-8 -*-

"""Tests dict input objects for `tackle.providers.azure.hooks` module."""
from tackle.main import tackle
import pytest
import os

if not os.environ.get('ARM_SUBSCRIPTION_ID') is not None:
    pytest.skip(
        "Skipping Azure tests because ARM_SUBSCRIPTION_ID env var not set.",
        allow_module_level=True,
    )


def test_provider_azure_regions(change_dir):
    """Verify the hook call works successfully."""
    context = tackle('.', context_file='regions.yaml')
    assert len(context['azs']) > 1


def test_provider_azure_vm_meta(change_dir):
    """Verify the hook call works successfully."""
    context = tackle('.', context_file='instance_types.yaml')

    assert len(context['instance_types']) > 1


def test_provider_azure_vm_meta_instance_family(change_dir):
    """Hook returns instance types filtered on family."""
    context = tackle('.', context_file='instance_family.yaml')

    assert len(context['instance_types']) > 1
    assert len(context['instance_types']) < 150
