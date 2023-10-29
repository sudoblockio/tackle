from tackle.main import tackle

import pytest
import shutil


@pytest.fixture()
def clean_outputs():
    """Remove the outputs dir."""
    yield
    shutil.rmtree('output')


# def test_provider_system_hook_tackle():
# #     # TODO Build example repo
#     context = tackle()
#     assert context


def test_provider_tackle_local():
    output = tackle('local.yaml', no_input=True)
    assert output['shell']['stuff'] == 'bing'
    assert output['shell']['read_stuff']['stuff'] == 'things'
    assert output['additional_context']['read_stuff']['stuff'] == 'things'

def test_provider_tackle_local_no_context():
    output = tackle('local-no-context.yaml')
    assert output['shell']['foo'] == 'bar'


def test_provider_tackle_local_prior_context():
    output = tackle('local-prior-context.yaml', no_input=True)
    assert output['shell']['foo'] == 'bar'


def test_provider_tackle_block_tackle():
    output = tackle('block-tackle.yaml', no_input=True)
    assert 'things' in output


def test_provider_tackle_remote():
    output = tackle('remote.yaml', no_input=True)

    assert output['project_slug'] == 'output'
    assert output['tackle-fixture-unreleased']['this'] == 'that'
    assert output['tackle-fixture-released']['released_hook'] == 'foo'


def test_provider_tackle_kwargs_default():
    output = tackle('kwargs-default.yaml', no_input=True)
    assert output['default_kwargs']['stuff'] == 'bing'


def test_provider_tackle_kwargs_default_hook():
    """Check that we can run a default hook from a tackle hook."""
    output = tackle('kwargs-default-hook.yaml', no_input=True)
    assert output['compact']['v'] == 'bing'
    assert output['expanded']['v'] == 'bing'


def test_provider_tackle_kwargs_default_hook_args():
    """Check that we can run a default hook from a tackle hook with args."""
    output = tackle('kwargs-default-hook-arg.yaml', no_input=True)
    assert output['compact']['v'] == 'bing'


def test_provider_tackle_a_dir_with_tackle_file():
    """Check that we can run a default hook from a tackle hook with args."""
    # TODO: Make tighter to show abs paths / be consistent
    #  https://github.com/sudoblockio/tackle/issues/175
    output = tackle('a-dir-with-tackle-file.yaml', no_input=True)
    assert output['call']['calling_directory'].endswith('tackle')
    assert output['call']['current_directory'].endswith('a-dir-with-tackle-file')
    assert output['call']['current_file'].endswith('tackle.yaml')
    assert output['call']['calling_file'].endswith('a-dir-with-tackle-file.yaml')
