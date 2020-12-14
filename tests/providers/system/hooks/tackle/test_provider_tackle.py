# -*- coding: utf-8 -*-

"""Tests dict input objects for `cookiecutter.prompt` module."""
import os

from tackle.main import tackle


def test_provider_system_hook_command(change_dir, tmpdir):
    """Verify the hook call works properly."""
    # TODO Build example repo
    context = tackle(
        '.', context_file='nuki.yaml', no_input=True, output_dir=str(tmpdir)
    )
    print(context)
    assert context


def test_provider_tackle_local(change_dir, tmpdir):
    """Verify the hook call works properly."""
    output = tackle(
        '.', context_file='local.yaml', no_input=True, output_dir=str(tmpdir)
    )
    assert output['shell']['foo'] == 'bing'


def test_provider_tackle_remote(change_dir, tmpdir):
    """Verify the hook call works properly."""
    output = tackle(
        '.', context_file='remote.yaml', no_input=True, output_dir=str(tmpdir)
    )
    assert output['shell']['foo'] == 'bing'
