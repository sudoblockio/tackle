"""Tests for `cookiecutter.find` module."""
import os

import pytest
from tackle.models import Context
import tackle.generate
from _collections import OrderedDict


@pytest.fixture(params=['fake-repo-pre', 'fake-repo-tmpl'])
def repo_dir_cookiecutter(request):
    """Fixture returning path for `test_find_template` test."""
    return request.param


def test_find_template_cookiecutter(repo_dir_cookiecutter, change_dir_main_fixtures):
    """Verify correctness of `find.find_template` path detection."""
    c = Context(tackle_gen='cookiecutter', context_key='cookiecutter')
    template = tackle.generate.find_template(repo_dir=repo_dir_cookiecutter, context=c)

    test_dir = os.path.join(repo_dir_cookiecutter, '{{cookiecutter.repo_name}}')
    assert template == test_dir


@pytest.fixture(params=['fake-repo-pre-tackle', 'fake-repo-tmpl-tackle'])
def repo_dir_tackle(request):
    """Fixture returning path for `test_find_template` test."""
    return request.param


def test_find_template_tackle(repo_dir_tackle, change_dir_main_fixtures):
    """Verify correctness of `find.find_template` path detection."""
    c = Context(tackle_gen='tackle', output_dict=OrderedDict({'repo_name': 'stuff'}))
    template = tackle.generate.find_template(repo_dir=repo_dir_tackle, context=c)

    test_dir = os.path.join(repo_dir_tackle, '{{repo_name}}')
    assert template == test_dir
