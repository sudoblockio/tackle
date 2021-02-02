# -*- coding: utf-8 -*-

"""Tests dict input objects for `tackle.providers.terraform.hooks.terraform` module."""

import os
from tackle.main import tackle
import pytest
from tackle.utils.paths import rmtree


# TODO: Need to be able test pyinquirer
def test_provider_terraform(change_dir):
    """Verify the hook call works successfully."""
    context = tackle(no_input=True)

    assert not context['cloudflare_enable']


def test_provider_terraform_remote(change_dir):
    """Verify the hook call works successfully."""
    context = tackle("https://github.com/insight-w3f/terraform-polkadot-k8s-config", no_input=True)
    assert context


@pytest.fixture()
def clean_up_tf():
    yield
    output_files = ["terraform0.13.6", "testing-path"]
    for o in output_files:
        if os.path.isfile(o):
            os.remove(o)
        if os.path.isdir(o):
            rmtree(o)


def test_provider_terraform_install(change_dir, clean_up_tf):
    """Verify the hook call works successfully."""
    context = tackle(no_input=True, context_file='install.yaml')

    assert '0.12.29' not in context['version_13']
    assert len(context['version']) > 30
    assert "You can update" in context['check_basic']
    assert "You can update" in context['check_path']


def test_terraform_plan(change_dir):
    o = tackle(context_file='cmds.yaml')

def test_provider_terraform_terragrunt_install(change_dir, clean_up_tf):
    """Verify the hook call works successfully."""
    output = tackle(no_input=True, context_file='install.yaml')

    assert output
