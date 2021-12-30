"""Tests dict input objects for `tackle.providers.pyinquirer.hooks.select` module."""
from tackle.main import tackle


def test_provider_requests_get(change_dir):
    """Verify the hook call works successfully."""
    output = tackle('get.yaml', no_input=True)
    assert output['simple']['userId'] == 1
    assert output['simple'] == output['compact']


def test_provider_requests_post(change_dir):
    """Verify the hook call works successfully."""
    output = tackle('post.yaml', no_input=True)
    assert output['simple']['name'] == "Rob Cannon"


def test_provider_requests_put(change_dir):
    """Verify the hook call works successfully."""
    output = tackle('put.yaml', no_input=True)
    assert output['simple']['name'] == "Rob Cannon"


def test_provider_requests_patch(change_dir):
    """Verify the hook call works successfully."""
    output = tackle('patch.yaml', no_input=True)
    assert output['simple']['name'] == "Rob Cannon"


def test_provider_requests_delete(change_dir):
    """Verify the hook call works successfully."""
    output = tackle('delete.yaml', no_input=True)
    assert output['simple'] == 204
