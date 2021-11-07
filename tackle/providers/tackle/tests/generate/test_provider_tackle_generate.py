# -*- coding: utf-8 -*-

"""Tests dict input objects for `tackle.providers.tackle.generate` module."""
import pytest
import os

from tackle.main import tackle
from tackle.utils.paths import rmtree


@pytest.fixture()
def clean_up_files():
    def clean_up_files(files: list):
        for f in files:
            rmtree(f)

    yield clean_up_files


def test_provider_system_hook_generate(change_dir, clean_up_files):
    """Verify the hook call works properly."""
    output = tackle(no_input=True)

    assert os.path.exists("things")

    clean_up_files(["things"])
    assert not output['t']
