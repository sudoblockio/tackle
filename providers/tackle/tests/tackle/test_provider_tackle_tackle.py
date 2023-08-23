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
    assert 'things' in output


def test_provider_tackle_remote(change_dir):
    output = tackle('remote.yaml', no_input=True)

    assert output['project_slug'] == 'output'
    assert output['tackle-fixture-unreleased']['this'] == 'that'
    assert output['tackle-fixture-released']['released_hook'] == 'foo'


def test_provider_tackle_kwargs_default(change_dir):
    output = tackle('kwargs-default.yaml', no_input=True)
    assert output['default_kwargs']['stuff'] == 'bing'


def test_provider_tackle_kwargs_default_hook(change_dir):
    """Check that we can run a default hook from a tackle hook."""
    output = tackle('kwargs-default-hook.yaml', no_input=True)
    assert output['compact']['v'] == 'bing'
    assert output['expanded']['v'] == 'bing'


def test_provider_tackle_kwargs_default_hook_args(change_dir):
    """Check that we can run a default hook from a tackle hook with args."""
    output = tackle('kwargs-default-hook-arg.yaml', no_input=True)
    assert output['compact']['v'] == 'bing'
