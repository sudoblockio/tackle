import os
from ruamel.yaml import YAML

import pytest
from tackle.main import tackle


@pytest.fixture()
def clean_outputs(change_dir):
    """Remove all the files prefixed with output before and after test."""
    files = [f for f in os.listdir() if f.split('.')[0].startswith('output')]
    for f in files:
        os.remove(f)
    yield
    files = [f for f in os.listdir() if f.split('.')[0].startswith('output')]
    for f in files:
        os.remove(f)


def test_provider_system_hook_yaml_read(change_dir, clean_outputs):
    read = tackle('read.yaml', no_input=True)

    assert read['stuff'] == 'things'


def test_provider_system_hook_yaml_write(change_dir, clean_outputs):
    tackle('write.yaml', no_input=True)
    yaml = YAML()
    with open('output.yaml', 'r') as f:
        written = yaml.load(f)
    assert written == {'stuff': 'things'}


# TODO: When in place yaml hooks are a thing
def test_provider_system_hook_yaml_update(change_dir, clean_outputs):
    tackle('update.yaml', no_input=True)

    yaml = YAML()
    with open('output.yaml', 'r') as f:
        output = yaml.load(f)

    assert output['stuff'] == {'things': {'cats': 'scratch'}}


def test_provider_system_hook_yaml_remove_str(change_dir, clean_outputs):
    tackle('remove_str.yaml', no_input=True)

    yaml = YAML()
    with open('output.yaml', 'r') as f:
        output = yaml.load(f)

    assert output == ['stuff', 'things']


def test_provider_system_hook_yaml_remove_list(change_dir, clean_outputs):
    tackle('remove_list.yaml', no_input=True)

    yaml = YAML()
    with open('output.yaml', 'r') as f:
        output = yaml.load(f)

    assert output == ['stuff', 'things']


def test_provider_system_hook_yaml_filter(change_dir, clean_outputs):
    output = tackle('filter.yaml', no_input=True)

    assert 'stuff' not in output['things']


def test_provider_system_hook_yaml_update_in_place(change_dir, clean_outputs):
    tackle('update_in_place.yaml', no_input=True)

    yaml = YAML()
    with open('output_update_in_place.yaml', 'r') as f:
        output = yaml.load(f)

    assert output['dev']['stuff'] == 'things'


def test_provider_system_hook_yaml_merge_in_place(change_dir, clean_outputs):
    tackle('merge_in_place.yaml', no_input=True)

    yaml = YAML()
    with open('output_merge_in_place.yaml', 'r') as f:
        output = yaml.load(f)

    assert output['dev']['stuff'] == 'things'


def test_provider_system_hook_yaml_append(change_dir, clean_outputs):
    output = tackle('append.yaml', no_input=True)
    assert output['append_dict'] == {'things': ['dogs', 'cats', 'bar', 'baz']}


def test_yaml_yamlify(change_dir, clean_outputs):
    output = tackle('yamlencode.yaml', no_input=True)
    assert isinstance(output['out'], str)
    assert 'stuff: things' in output['out']


def test_yaml_yamldecode(change_dir, clean_outputs):
    output = tackle('yamldecode.yaml', no_input=True)
    assert isinstance(output['out'], dict)
    assert output['out']['stuff'] == 'things'
