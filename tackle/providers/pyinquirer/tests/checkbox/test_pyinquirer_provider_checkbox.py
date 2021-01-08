# -*- coding: utf-8 -*-

"""Tests dict input objects for `tackle.providers.pyinquirer.hooks.checkbox` module."""
from tackle.main import tackle


# TODO: Need to properly test this with pty. Tests don't cover now
def test_provider_checkbox_dict_ok(change_dir):
    """Verify the hook call works successfully."""
    context_dict_ok = tackle('.', context_file='dict_ok.yaml', no_input=True)
    assert context_dict_ok


def test_provider_checkbox_dict_index(change_dir):
    """Verify the hook call works successfully."""
    context_string_ok = tackle('.', context_file='dict_index.yaml', no_input=True)

    assert context_string_ok


def test_provider_checkbox_string_ok(change_dir):
    """Verify the hook call works successfully."""
    context_dict_ok = tackle('.', context_file='string_ok.yaml', no_input=True)

    assert context_dict_ok
