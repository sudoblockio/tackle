"""
test_cookiecutter_invocation.

Tests to make sure that cookiecutter can be called from the cli without
using the entry point set up for the package.
"""

import os
import subprocess
import sys

import shutil
import pytest


from cookiecutter import utils


@pytest.fixture
def project_dir():
    """Return test project folder name and remove it after the test."""
    yield 'fake-project-templated'

    if os.path.isdir('fake-project-templated'):
        utils.rmtree('fake-project-templated')


@pytest.mark.usefixtures('clean_system')
def test_should_invoke_main(monkeypatch, project_dir):
    """Should create a project and exit with 0 code on cli invocation."""
    monkeypatch.setenv('PYTHONPATH', '.')
    test_dir = os.path.join(os.path.abspath(os.path.dirname(__file__)), '..')
    monkeypatch.chdir(test_dir)

    exit_code = subprocess.check_call(
        [sys.executable, '-m', 'cookiecutter.cli', 'tests/fake-repo-tmpl', '--no-input']
    )
    assert exit_code == 0
    assert os.path.isdir(project_dir)


@pytest.mark.usefixtures('clean_system')
def test_should_invoke_main_nuki(monkeypatch, project_dir):
    """Should create a project and exit with 0 code on cli invocation."""
    monkeypatch.setenv('PYTHONPATH', '.')
    test_dir = os.path.join(os.path.abspath(os.path.dirname(__file__)))
    monkeypatch.chdir(test_dir)

    exit_code = subprocess.check_call(
        [sys.executable, '-m', 'cookiecutter.cli', 'fake-repo-tmpl-nuki', '--no-input',]
    )

    assert exit_code == 0
    assert os.path.isdir(project_dir)


@pytest.mark.usefixtures('clean_system')
def test_should_invoke_main_nuki_nukis(monkeypatch, project_dir):
    """Should create a project and exit with 0 code on cli invocation."""
    monkeypatch.setenv('PYTHONPATH', '.')
    test_dir = os.path.join(
        os.path.abspath(os.path.dirname(__file__)), 'fake-repo-tmpl-nukis'
    )
    monkeypatch.chdir(test_dir)

    output_dirs = ['fake-nuki-templated', 'fake-nuki2-templated']
    for o in output_dirs:
        if os.path.isdir(o):
            shutil.rmtree(o)

    exit_code = subprocess.check_call(
        [sys.executable, '-m', 'cookiecutter.cli', '.', '--no-input',]
    )

    assert exit_code == 0
    assert os.path.isdir(project_dir)

    for o in output_dirs:
        if os.path.isdir(o):
            shutil.rmtree(o)
