"""Tests dict input objects for `tackle.providers.system.hooks.symlink` module."""
import os

import pytest

from tackle.main import tackle


@pytest.fixture()
def clean_up_outputs():
    """Clean up."""
    yield
    os.unlink('dst.yaml')


def test_provider_system_hook_symlink_overwrite(clean_up_outputs):
    output = tackle('tackle.yaml', no_input=True)

    assert output['read'] == {'foo': 'bar'}
    assert output['read_dir'] == {'foo': 'bar'}
    assert output['read_dir2'] == {'foo': 'bar'}
