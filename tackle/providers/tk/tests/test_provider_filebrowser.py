# -*- coding: utf-8 -*-

"""Tests dict input objects for `tackle.providers.tk.hooks.filebrowser` module."""
from tackle.main import tackle


def test_provider_tk_askopenfilename(change_dir):
    """Verify the hook call works successfully."""
    o = tackle('.', context_file='askopenfilename.yaml', no_input=True)
    assert o
