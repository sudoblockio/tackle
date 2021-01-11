# -*- coding: utf-8 -*-

"""Tests dict input objects for `tackle.providers.pyinquirer.hooks.select` module."""
from tackle.main import tackle


def test_provider_requests_get(change_dir):
    """Verify the hook call works successfully."""
    output = tackle('.', context_file='get.yaml', no_input=True)
    assert output['simple']['userId'] == 1


def test_provider_requests_post(change_dir):
    """Verify the hook call works successfully."""
    output = tackle('.', context_file='post.yaml', no_input=True)
    assert output['simple']['name'] == "Rob Cannon"


def test_provider_requests_put(change_dir):
    """Verify the hook call works successfully."""
    output = tackle('.', context_file='put.yaml', no_input=True)
    assert output['simple']['name'] == "Rob Cannon"


def test_provider_requests_patch(change_dir):
    """Verify the hook call works successfully."""
    output = tackle('.', context_file='patch.yaml', no_input=True)
    assert output['simple']['name'] == "Rob Cannon"


def test_provider_requests_delete(change_dir):
    """Verify the hook call works successfully."""
    output = tackle('.', context_file='delete.yaml', no_input=True)
    assert output['simple'] == 204
