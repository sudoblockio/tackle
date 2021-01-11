# -*- coding: utf-8 -*-

"""Tests `tackle.providers.art.hooks` module."""
from tackle.main import tackle


def test_provider_art_text2art(change_dir):
    """Verify the hook call works successfully."""
    context = tackle('.', context_file='text2art.yaml', no_input=True)

    assert len(context) > 1


def test_provider_art_tprint(change_dir):
    """Verify the hook call works successfully."""
    context = tackle('.', context_file='tprint.yaml', no_input=True)

    assert len(context) > 1
