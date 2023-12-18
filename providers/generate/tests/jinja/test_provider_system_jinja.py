import os

import pytest
from ruyaml import YAML

from tackle.main import tackle


@pytest.fixture()
def clean_things():
    """Remove all things.py."""
    if os.path.exists('things.py'):
        os.remove('things.py')
    yield
    if os.path.exists('things.py'):
        os.remove('things.py')


def test_provider_system_hook_jinja(clean_things):
    context = tackle()
    assert context['foo'] == 'bar'
    yaml = YAML()
    with open('things.py') as f:
        output = yaml.load(f)
    assert output == "x = 'bar'"


def test_provider_system_hook_jinja_existing_context(clean_things):
    context = tackle('existing-context.yaml')
    assert context['foo'] == 'bar'
    yaml = YAML()
    with open('things.py') as f:
        output = yaml.load(f)
    assert output == "x = 'bar'"
