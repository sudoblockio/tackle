"""Test the regex qualifier for inding generate."""
import re
import pytest
from tackle.generate import TEMPLATE_DIR_REGEX

MATCHES = [
    ('{{project}}', True),
    ('{{project_slug}}', True),
    ('{{cookiecutter.project-slug}}', True),
    ('{{ cookiecutter.project-slug}}', True),
    ('{{ cookiecutter.project-slug }}', True),
    ('{{cookiecutter.project-slug}}-this', True),
    ('{{ cookiecutter.project-slug }}that', True),
    ('that{{cookiecutter.project-slug}}', True),
    ('this-{{cookiecutter.project-slug}}', True),
    ('{cookiecutter.project-slug}', False),
    ('cookiecutter.project-slug}}', False),
    ('{ cookiecutter.project-slug }}', False),
    ('{{ cookiecutter.project-slug ', False),
]


@pytest.mark.parametrize("match,should_match", MATCHES)
def test_generate_regex(match, should_match):
    """Test the template finder regex."""
    ouput = re.match(TEMPLATE_DIR_REGEX, match)
    if should_match:
        assert ouput
    else:
        assert not ouput
