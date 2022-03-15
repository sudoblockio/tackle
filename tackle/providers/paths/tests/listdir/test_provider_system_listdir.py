"""Tests dict input objects for `tackle.providers.system.hooks.listdir` module."""
from tackle.main import tackle


def test_provider_system_hook_listdir(change_dir):
    output = tackle('.', no_input=True)

    assert len(output['string_input']) == 3
    assert len(output['string_input_sorted']) == 2
    assert len(output['list_input']) == 2
