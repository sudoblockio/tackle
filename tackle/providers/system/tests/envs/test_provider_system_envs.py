# -*- coding: utf-8 -*-

"""Tests dict input objects for `tackle.providers.system.hooks.envs` module."""
import os
from tackle.main import tackle
from tackle.exceptions import HookCallException
import pytest


@pytest.fixture()
def tmp_env_var():
    """Set env var temporarily."""
    os.environ['TMP_VAR_THING'] = 'stuff'
    yield
    vars = ['TMP_VAR_THING', 'TMP_VAR_STUFF']
    for v in vars:
        if v in os.environ:
            del os.environ[v]


def test_provider_system_hook_envs(change_dir, tmp_env_var):
    """Verify the hook call works properly."""
    output = tackle('.', context_file='envs.yaml', no_input=True)
    assert output['output'] == 'stuff'
    assert os.environ['TMP_VAR_STUFF']


def test_provider_system_hook_envs_error(change_dir, tmp_env_var):
    """Verify the hook call works properly."""
    with pytest.raises(HookCallException):
        tackle('.', context_file='error.yaml', no_input=True)
