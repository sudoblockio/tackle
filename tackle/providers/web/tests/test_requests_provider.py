"""Tests dict input objects for `tackle.providers.pyinquirer.hooks.select` module."""
from tackle.main import tackle


def test_provider_requests_get(change_dir):
    output = tackle('get.yaml', no_input=True)
    assert output['compact']['url'] == output['expanded']['url']


def test_provider_requests_post(change_dir):
    output = tackle('post.yaml', no_input=True)
    assert output['expanded']['json']['stuff'] == "things"
    assert output['expanded']['json'] == output['compact']['json']


def test_provider_requests_put(change_dir):
    output = tackle('put.yaml', no_input=True)
    assert output['expanded']['json']['stuff'] == "things"


def test_provider_requests_patch(change_dir):
    output = tackle('patch.yaml', no_input=True)
    assert output['expanded']['json']['stuff'] == "things"


def test_provider_requests_delete(change_dir):
    output = tackle('delete.yaml', no_input=True)
    assert output['expanded'] == 200
