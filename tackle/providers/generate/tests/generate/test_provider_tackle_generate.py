import pytest
from ruamel.yaml import YAML

import shutil
import os

from tackle.main import tackle
from tackle.providers.generate.hooks.exceptions import (
    UndefinedVariableInTemplate,
    GenerateHookTemplateNotFound,
)

FIXTURES = [
    "file.yaml",
    "plain-src.yaml",
    "plain-src-block.yaml",
    "plain-src-path.yaml",
    "render-file.yaml",
    "render-file-additional-context.yaml",
    "render-dir-file.yaml",
    "render-dir-file-base.yaml",
    # "tackle-provider-remote.yaml",
]


@pytest.mark.parametrize("fixture", FIXTURES)
def test_provider_system_hook_generate_fixtures(change_dir, fixture):
    output = tackle(fixture, no_input=True)
    assert not output['init']

    if isinstance(output['after'], list):
        for i in output['after']:
            assert i
    else:
        assert output['after']


ERRORS = [
    ("missing-file.yaml", GenerateHookTemplateNotFound),
    ("unknown-variable.yaml", UndefinedVariableInTemplate),
]


@pytest.mark.parametrize("fixture,error", ERRORS)
def test_provider_system_hook_generate_error(change_dir, fixture, error):
    with pytest.raises(error):
        tackle(fixture)


def test_hook_generate_copy_without_render(change_dir):
    tackle("copy-without-render.yaml")
    yaml = YAML()
    with open(os.path.join('output', '.hidden.yaml')) as f:
        hidden = yaml.load(f)

    with open('output/no-render/dir/foo.yaml') as f:
        nested_glob = yaml.load(f)

    assert hidden['stuff'] == '{{stuff}}'
    assert nested_glob['stuff'] == '{{stuff}}'
    shutil.rmtree('output')


def test_hook_generate_looped(change_dir):
    output = tackle("looped.yaml")

    assert len(output['networks']) == 2
    assert output['networks'][0]['things'] == 'foo'
    shutil.rmtree('output')


def test_hook_generate_skip_overwrite_files(change_dir):
    """Validate that we can skip rendering a file with `skip_overwrite_files`."""
    output = tackle("skip-overwrite-files.yaml")

    assert output['verify']['stuff'] == 'foo'


def test_hook_generate_skip_if_file_exists(change_dir):
    """Validate that we can skip rendering a file with `skip_if_file_exists`."""
    output = tackle("skip-overwrite-files.yaml")

    assert output['verify']['stuff'] == 'foo'
