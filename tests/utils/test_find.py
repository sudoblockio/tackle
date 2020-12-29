"""Tests for `cookiecutter.find` module."""
import os

import pytest

import tackle.generate


@pytest.fixture(params=['fake-repo-pre', 'fake-repo-tmpl'])
def repo_dir(request):
    """Fixture returning path for `test_find_template` test."""
    return request.param


def test_find_template(repo_dir, change_dir_main_fixtures):
    """Verify correctness of `find.find_template` path detection."""
    template = tackle.generate.find_template(repo_dir=repo_dir)

    test_dir = os.path.join(repo_dir, '{{cookiecutter.repo_name}}')
    assert template == test_dir
