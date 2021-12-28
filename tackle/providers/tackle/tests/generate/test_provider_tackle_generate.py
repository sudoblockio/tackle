"""Tests dict input objects for `tackle.providers.tackle.generate` module."""
import pytest

from tackle.main import tackle
from jinja2.exceptions import TemplateNotFound

FIXTURES = [
    "file.yaml",
    "plain-src.yaml",
    "render-file.yaml",
    "render-dir-file.yaml",
    "render-dir-file-base.yaml",
]


@pytest.mark.parametrize("fixture", FIXTURES)
def test_provider_system_hook_generate_fixtures(change_dir, fixture):
    """Verify the hook call works properly."""
    output = tackle(fixture)
    assert not output['init']
    assert output['after']


ERRORS = [
    ("missing-file.yaml", TemplateNotFound),
]


@pytest.mark.parametrize("fixture,error", ERRORS)
def test_provider_system_hook_generate_error(change_dir, fixture, error):
    """Verify the hook call works properly."""
    with pytest.raises(error):
        tackle(fixture)
