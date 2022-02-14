"""Tests dict input objects for `tackle.providers.pyinquirer.hooks.select` module."""
from tackle.main import tackle


def test_provider_requests_get(change_dir):
    output = tackle('get.yaml', no_input=True)
    assert output['expanded']['userId'] == 1
    assert output['expanded'] == output['compact']


def test_provider_requests_post(change_dir):
    output = tackle('post.yaml', no_input=True)
    assert output['expanded']['stuff'] == "things"


def test_provider_requests_put(change_dir):
    output = tackle('put.yaml', no_input=True)
    assert output['expanded']['stuff'] == "things"


def test_provider_requests_patch(change_dir):
    output = tackle('patch.yaml', no_input=True)
    assert output['expanded']['stuff'] == "things"


def test_provider_requests_delete(change_dir):
    output = tackle('delete.yaml', no_input=True)
    assert output['expanded'] == 204
