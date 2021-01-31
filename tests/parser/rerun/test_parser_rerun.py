# -*- coding: utf-8 -*-

"""Tests dict input objects for `cookiecutter.operator.lists` module."""
import os
import yaml
import pytest
from tackle.main import tackle
from tackle.exceptions import UnknownHookTypeException


# TODO: Fix this logic
# @pytest.mark.parametrize("clean_output", ["tackle.record.yaml"], indirect=True)
# def test_parser_rerun(change_dir, clean_output):
#     """Verify the hook call works successfully."""
#     o = tackle('.', no_input=True, rerun=True)
#
#     assert 'foo' in o
#
#     # without no_output means the run is using the override
#     o = tackle('.', rerun=clean_output)
#
#     assert o['foo'] == ['bar', 'bax', 'bin']


RERUN_FILE = '.rerun.rerun.yml'

@pytest.fixture()
def clean_rerun():
    yield
    if os.path.isfile(RERUN_FILE):
        os.remove(RERUN_FILE)


def test_parser_rerun_broken_recover(change_dir, clean_rerun):
    """Verify the hook call works successfully."""
    with pytest.raises(UnknownHookTypeException):
        tackle(no_input=True, rerun=True, context_file='tackle-broken.yaml')

    with open(RERUN_FILE) as f:
        rerun = yaml.load(f)

    assert rerun['foo'] == 'bar'
