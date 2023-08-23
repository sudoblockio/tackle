import os
from tackle.main import tackle
import pytest
import platform


@pytest.fixture()
def tmp_env_var():
    """Set env var temporarily."""
    os.environ['TMP_VAR_THING'] = 'stuff'
    yield
    vars = ['TMP_VAR_THING', 'TMP_VAR_STUFF']
    for v in vars:
        if v in os.environ:
            del os.environ[v]


def test_provider_env_hook_envs(change_dir, tmp_env_var):
    if platform.system() == 'Windows':
        # Need to support this later
        pytest.skip()

    o = tackle('envs.yaml')
    assert o['get_env'] == o['get_env_arg'] == o['get_env_arg_fallback']
    assert o['set_env'] == o['set_env_arg']
    assert o['get_env_arg_after_set'] == 'things'
    assert os.environ['TMP_VAR_THING']
