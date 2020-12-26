"""Verify correct work of `_copy_without_render` context option."""
import os

import pytest

import tackle.utils.paths
from tackle.main import tackle
from tackle.utils.paths import rmtree


@pytest.fixture
def remove_test_dir():
    """Fixture. Remove the folder that is created by the test."""
    if os.path.exists('test_copy_without_render'):
        rmtree('test_copy_without_render')
    yield
    if os.path.exists('test_copy_without_render'):
        rmtree('test_copy_without_render')


@pytest.mark.usefixtures('clean_system', 'remove_test_dir')
def test_generate_copy_without_render_extensions(change_dir):
    """Verify correct work of `_copy_without_render` context option.

    Some fixtures/files/directories should be rendered during invocation,
    some just copied, without any modification.
    """
    tackle('test-generate-copy-without-render', no_input=True)

    dir_contents = os.listdir('test_copy_without_render')

    assert 'test_copy_without_render-not-rendered' in dir_contents
    assert 'test_copy_without_render-rendered' in dir_contents

    with open('test_copy_without_render/README.txt') as f:
        assert '{{cookiecutter.render_test}}' in f.read()

    with open('test_copy_without_render/README.rst') as f:
        assert 'I have been rendered!' in f.read()

    with open(
        'test_copy_without_render/test_copy_without_render-rendered/README.txt'
    ) as f:
        assert '{{cookiecutter.render_test}}' in f.read()

    with open(
        'test_copy_without_render/test_copy_without_render-rendered/README.rst'
    ) as f:
        assert 'I have been rendered' in f.read()

    with open(
        'test_copy_without_render/'
        'test_copy_without_render-not-rendered/'
        'README.rst'
    ) as f:
        assert '{{cookiecutter.render_test}}' in f.read()

    with open('test_copy_without_render/rendered/not_rendered.yml') as f:
        assert '{{cookiecutter.render_test}}' in f.read()

    with open(
        'test_copy_without_render/' 'test_copy_without_render-rendered/' 'README.md'
    ) as f:
        assert '{{cookiecutter.render_test}}' in f.read()
