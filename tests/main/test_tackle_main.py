# -*- coding: utf-8 -*-

"""Tests dict input objects for `cookiecutter.parser.providers` module."""
from tackle.main import tackle
import pytest
import os

from tackle.utils.paths import rmtree


@pytest.fixture()
def clean_up_output():
    """Clean the outputs dir."""
    yield
    if os.path.isdir('output'):
        rmtree('output')


@pytest.mark.parametrize(
    'template',
    [
        # ('https://github.com/pydanny/cookiecutter-django'),
        # ('https://github.com/tiangolo/full-stack-fastapi-postgresql'),
        ('fixtures/fake-repo-pre-tackle'),
    ],
)
def test_main_tackle_remote(clean_up_output, template, change_dir):
    """Validate that popular cookiecutters work properly."""
    tackle(template, no_input=True, output_dir='output')


def test_main_tackle_generate_simple(change_dir_main_fixtures, clean_up_output):
    """."""
    tackle('fake-repo-pre-tackle', no_input=True, output_dir='output')
    assert os.path.isdir('output/fake-project')
