# -*- coding: utf-8 -*-

"""Tests dict input objects for `tackle.providers.gcp.hooks` module."""
import os
import pytest
from tackle.main import tackle
from tackle.utils import timeout, TimeoutError


@timeout(3)
def run_provider_gcp_regions():
    """Verify gcp zones."""
    return tackle(
        os.path.abspath(os.path.dirname(__file__)), context_file='regions.yaml'
    )


try:
    run_provider_gcp_regions()
except (TypeError, TimeoutError):
    # TODO: Validate that this is the right skip test
    pytest.skip("Skipping GCP tests.", allow_module_level=True)


def test_provider_gcp_zones(change_dir):
    """Verify gcp zones."""
    context = run_provider_gcp_regions()

    assert len(context['azs']) > 1


def test_provider_gcp_azs_region(change_dir):
    """Verify gcp get azs of region."""
    context = tackle('.', context_file='azs_region.yaml')

    assert len(context) > 1


def test_provider_gcp_azs_regions(change_dir):
    """Verify gcp get azs of multiple regions."""
    context = tackle('.', context_file='azs_regions.yaml')

    assert len(context) > 1
    assert len(context['azs']['us-east1']) > 1


def test_provider_gcp_instance_meta(change_dir):
    """Verify gcp instance meta data."""
    context = tackle('.', context_file='instance_meta.yaml')

    assert len(context['instance_types']) > 1


def test_provider_gcp_instance_meta_instance_family(change_dir):
    """Verify gcp instance family."""
    context = tackle('.', context_file='instance_family.yaml')

    assert len(context['instance_types']) > 1
    assert len(context['instance_types']) < 75
    assert "n2d-standard-2" not in context['instance_types']
