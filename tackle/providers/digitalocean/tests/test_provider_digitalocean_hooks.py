# -*- coding: utf-8 -*-

"""Tests dict input objects for `tackle.providers.digitalocean.hooks` module."""
import os
import pytest
from tackle.main import tackle
from dopy.manager import DoError


try:
    context_file = os.path.join(
        os.path.abspath(os.path.dirname(__file__)), 'instance_family.yaml'
    )
    tackle('.', context_file=context_file)
except DoError:
    pytest.skip(
        "Skipping DigitalOcean tests because of auth error.", allow_module_level=True
    )


def test_provider_digitalocean_hooks_regions(change_dir):
    """Verify DO azs."""
    output = tackle('.')
    assert len(output['azs']) > 1


def test_provider_digitalocean_hooks_instance_meta(change_dir):
    """Verify Jinja2 time extension work correctly."""
    context = tackle('.', context_file='instance_types.yaml', no_input=True)

    assert len(context['instance_types']) > 1


def test_provider_digitalocean_hooks_instance_meta_instance_family(change_dir):
    """Verify Jinja2 time extension work correctly."""
    context = tackle('.', context_file='instance_family.yaml', no_input=True,)

    assert len(context['instance_types']) > 1
    assert len(context['instance_types']) < 20
    assert "gd-2vcpu-8gb" not in context['instance_types']
