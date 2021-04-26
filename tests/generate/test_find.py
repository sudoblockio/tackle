"""Tests for `cookiecutter.find` module."""
import os

import pytest
import tackle.generate


@pytest.fixture(params=['fake-repo-pre', 'fake-repo-tmpl'])
def repo_dir_cookiecutter(request):
    """Fixture returning path for `test_find_template` test."""
    return request.param


def test_find_template_cookiecutter(repo_dir_cookiecutter, change_dir_main_fixtures):
    """Verify correctness of `find.find_template` path detection."""
    template = tackle.generate.find_template(repo_dir=repo_dir_cookiecutter)
    test_dir = os.path.join(repo_dir_cookiecutter, '{{cookiecutter.repo_name}}')
    assert template == test_dir


TEMPLATES = [
    ('fake-repo-tmpl-tackle', '{{repo_name}}'),
    ('fake-repo-pre-tackle-spaces', '{{ repo_name }}'),
    ('fake-repo-pre-tackle', '{{repo_name}}-that'),
]


@pytest.mark.parametrize("repo_dir,expected_result", TEMPLATES)
def test_find_template_tackle(repo_dir, expected_result, change_dir_main_fixtures):
    """Verify correctness of `find.find_template` path detection."""
    template = tackle.generate.find_template(repo_dir=repo_dir)
    test_dir = os.path.join(repo_dir, expected_result)
    assert template == test_dir
