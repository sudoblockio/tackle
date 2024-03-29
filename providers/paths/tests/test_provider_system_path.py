"""Tests dict input objects for `tackle.providers.system.hooks.path` module."""
import os

from tackle.main import tackle


def test_provider_system_hook_path():
    context = tackle('parent.yaml')

    assert context['path_isdir']

    assert context['path_exists']
    assert os.path.exists(context['find_in_parent_dir'])  # Should be tests/tests...
    assert os.path.exists(context['find_in_parent_file'])
    assert context['find_in_parent_fallback'] == context['find_in_parent_dir']


def test_provider_system_hook_path_child():
    context = tackle('child.yaml')

    assert len(context['find_in_child']) == 2
    assert len(context['find_in_child_starting_dir']) == 1
    assert context['find_in_child_fallback'] == 'fallback.yaml'
    assert context['isfile']


def test_provider_paths_base_dir_name():
    output = tackle('base-dir-name.yaml')

    assert output['base'] == 'tests'
    assert 'paths' in output['dir']


def test_provider_paths_glob():
    output = tackle('glob.yaml')

    assert 'dirs' in output['star']
