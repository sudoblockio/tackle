"""Tests dict input objects for `tackle.providers.system.hooks.copy` module."""
import os
import shutil
from tackle.main import tackle
import pytest


@pytest.fixture()
def clean_files():
    """Clean the run."""
    yield
    files = ['thing.yaml', 'thing2.yaml', 'stuff']
    for f in files:
        if os.path.isfile(f):
            os.remove(f)
        if os.path.isdir(f):
            shutil.rmtree(f)


def test_provider_system_hook_file(change_dir, clean_files):
    tackle('tackle.yaml')
    assert 'thing.yaml' in os.listdir()
    assert 'stuff' in os.listdir()
    # If the file has been moved properly there should be only one file
    assert len(os.listdir('stuff')) == 3


def test_provider_system_hook_file_shred(change_dir, clean_files):
    files = ['stuff', 'thing', 'foo']
    for f in files:
        file = open(f, "w")
        file.write(f)
        file.close()

    tackle('shred.yaml')

    for f in files:
        assert not os.path.isfile(f)


@pytest.fixture()
def fix_file_perms():
    """Change back file perms."""
    yield
    if os.name == 'nt':
        pytest.skip("Skipping when run from windows.", allow_module_level=True)
    os.chmod('tackle.yaml', int('0o644', 8))


def test_provider_system_hook_file_chmod(change_dir, fix_file_perms):
    tackle('chmod.yaml')
    assert oct(os.stat('tackle.yaml').st_mode)[-3:] == "600"


def test_provider_files_remove(change_dir, fix_file_perms):
    o = tackle('remove.yaml')
    assert o['if_file']
    assert not o['not_file']
    assert o['if_files']
    assert not o['not_files']


def test_provider_system_hook_file_file(change_dir):
    """Verify file hook can read and write."""
    o = tackle('file.yaml')
    assert os.path.exists('rm.txt')
    os.remove('rm.txt')
    assert 'command' in o['read']
