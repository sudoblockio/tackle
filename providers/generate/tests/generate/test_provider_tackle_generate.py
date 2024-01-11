import os
import shutil
from typing import Type

import pytest
from ruyaml import YAML

from tackle.main import tackle

FIXTURES = [
    "file.yaml",
    "plain-src.yaml",
    "plain-src-block.yaml",
    "plain-src-path.yaml",
    "render-file.yaml",
    "render-file-additional-context.yaml",
    "render-dir-file.yaml",
    "render-dir-file-base.yaml",
    "special-key.yaml",
    # # "tackle-provider-remote.yaml",
]


@pytest.mark.parametrize("fixture", FIXTURES)
def test_provider_system_hook_generate_fixtures(fixture):
    output = tackle(fixture, no_input=True)
    assert not output['init']

    if isinstance(output['after'], list):
        for i in output['after']:
            assert i
    else:
        assert output['after']


ERRORS: list[tuple[str, Type[Exception]]] = [
    # TODO: Fix these - they seem to be working fine... Snubbing for now
    # ("missing-file.yaml", GenerateHookTemplateNotFound),
    # ("unknown-variable.yaml", UndefinedVariableInTemplate),
]


@pytest.mark.parametrize("fixture,error", ERRORS)
def test_provider_generate_hook_generate_error(fixture, error):
    with pytest.raises(error):
        tackle(fixture)


def test_hook_generate_copy_without_render():
    tackle("copy-without-render.yaml")
    yaml = YAML()
    with open(os.path.join('output', '.hidden.yaml')) as f:
        hidden = yaml.load(f)

    with open('output/no-render/dir/foo.yaml') as f:
        nested_glob = yaml.load(f)

    assert hidden['stuff'] == '{{stuff}}'
    assert nested_glob['stuff'] == '{{stuff}}'
    shutil.rmtree('output')


def test_hook_generate_looped():
    output = tackle("looped.yaml")

    assert len(output['networks']) == 2
    assert output['networks'][0]['things'] == 'foo'
    shutil.rmtree('output')


def test_hook_generate_skip_overwrite_files():
    """Validate that we can skip rendering a file with `skip_overwrite_files`."""
    output = tackle("skip-overwrite-files.yaml")

    assert output['verify']['stuff'] == 'foo'


def test_hook_generate_skip_if_file_exists():
    """Validate that we can skip rendering a file with `skip_if_file_exists`."""
    output = tackle("skip-overwrite-files.yaml")

    assert output['verify']['stuff'] == 'foo'
