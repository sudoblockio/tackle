# # -*- coding: utf-8 -*-
#
# """Tests dict input objects for `tackle.providers.yubikey.hooks.yubikey` module."""
# import pytest
# import os
# from tackle.main import tackle
#
#
# def test_provider_yubikey_hook_read(change_dir):
#     """Verify the hook call works successfully."""
#     o = tackle('.', context_file='read.yaml', no_input=True)
#     assert 'owner' in o['read'].keys()
