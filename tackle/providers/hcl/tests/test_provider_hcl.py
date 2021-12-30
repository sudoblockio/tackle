"""Tests dict input objects for `tackle.providers.hcl.hooks.hcl` module."""
from tackle.main import tackle
import json


def test_provider_hcl_hook_read(change_dir):
    """Verify the hook call works successfully."""
    o = tackle('read.yaml')

    with open('example.json') as f:
        expected_output = json.load(f)

    assert o['read'] == expected_output
