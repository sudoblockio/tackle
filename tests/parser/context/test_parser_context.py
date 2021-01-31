# -*- coding: utf-8 -*-

"""Tests dict input objects for `cookiecutter.operator.lists` module."""
from tackle.main import tackle
import os


def test_parser_contexts_overwrite_inputs(tmpdir, change_dir):
    """Verify the hook call works successfully."""
    overwrite_inputs = {'stuff': 'dingdongs'}

    o = tackle(
        '.',
        no_input=True,
        output_dir=str(tmpdir),
        overwrite_inputs=overwrite_inputs,
        context_file='tackle.yaml',
    )
    assert o['stuff'] == 'dingdongs'


def test_parser_contexts_overwrite_inputs_file(change_dir):
    """Verify the hook call works successfully."""
    overwrite_inputs = 'overwrite.yaml'

    o = tackle(
        no_input=True,
        overwrite_inputs=overwrite_inputs,
    )
    assert o['stuff'] == 'dingdongs'

    # Also confirm abs path in dir.
    o = tackle(
        no_input=True,
        overwrite_inputs=os.path.join(os.path.abspath(
            os.path.dirname(__file__)), overwrite_inputs)
    )
    assert o['stuff'] == 'dingdongs'
