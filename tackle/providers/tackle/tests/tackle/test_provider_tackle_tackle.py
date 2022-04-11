"""Tests dict input objects for `tackle.providers.tackle.hooks.tackle` module."""
from tackle.main import tackle

import pytest
import shutil


@pytest.fixture()
def clean_outputs():
    """Remove the outputs dir."""
    yield
    shutil.rmtree('output')


# def test_provider_system_hook_tackle(change_dir):
# #     # TODO Build example repo
#     context = tackle('tackle.yaml', no_input=True)
#     assert context


def test_provider_tackle_local(change_dir):
    output = tackle('local.yaml', no_input=True)
    assert output['shell']['stuff'] == 'bing'


def test_provider_tackle_local_no_context(change_dir):
    output = tackle('local-no-context.yaml', no_input=True)
    assert output['shell']['foo'] == 'bar'


def test_provider_tackle_local_prior_context(change_dir):
    output = tackle('local-prior-context.yaml', no_input=True)
    assert output['shell']['foo'] == 'bar'


def test_provider_tackle_block_tackle(change_dir):
    output = tackle('block-tackle.yaml', no_input=True)
    assert output
