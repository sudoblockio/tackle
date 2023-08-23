"""Tests dict input objects for `tackle.providers.system.hooks.symlink` module."""
from tackle.main import tackle
import pytest
import os


@pytest.fixture()
def clean_up_outputs():
    """Clean up."""
    yield
    os.unlink('dst.yaml')


def test_provider_system_hook_symlink_overwrite(change_dir, clean_up_outputs):
    output = tackle('tackle.yaml', no_input=True)

    assert output['read'] == {'foo': 'bar'}
    assert output['read_dir'] == {'foo': 'bar'}
    assert output['read_dir2'] == {'foo': 'bar'}
