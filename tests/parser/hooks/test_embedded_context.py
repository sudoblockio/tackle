# -*- coding: utf-8 -*-

"""Tests dict input objects for `cookiecutter.operator.aws.azs` module."""

import os
import yaml
import pytest
from tackle.main import tackle

INNER_YAML = os.path.join('embed-context', 'stuffs', 'things', 'before.yaml')


@pytest.fixture()
def clean_up_embed(request):
    """Clean up the outputs of the test."""
    if os.path.exists('after.yaml'):
        os.remove('after.yaml')
    if os.path.exists(INNER_YAML):
        os.remove(INNER_YAML)
    yield
    if os.path.exists('after.yaml'):
        os.remove('after.yaml')
    if os.path.exists(INNER_YAML):
        os.remove(INNER_YAML)


def test_embedded_context(change_curdir_fixtures, clean_up_embed):
    """Verify a tackle called from a tackle works properly by switching directory."""
    context = tackle('embed-context', no_input=True)

    assert context['inner_tackle']['stuff'] == 'Indeed'
    with open(INNER_YAML) as f:
        embedded_yaml = yaml.load(f)

    assert embedded_yaml['foo'] == 'bar'
    assert embedded_yaml['stuff'] == 'Indeed'
    assert embedded_yaml['things'] == 'yes please'
