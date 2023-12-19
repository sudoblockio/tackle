import platform
import sys

import pytest

from tackle import new_context
from tackle.context import Context
from tackle.render import render_variable
from tackle.special_vars import get_linux_distribution


@pytest.fixture()
def special_variables_context() -> Context:
    context = new_context('.')
    context.data.public = {'foo': 1}
    context.data.private = {'foo': 2}
    context.data.existing = {'foo': 3}
    context.data.temporary = {'foo': 4}
    return context


@pytest.mark.parametrize(
    "raw,assertion",
    [
        ('{{cwd}}', lambda x: x.endswith('special_variables')),
        ('{{this}}', lambda x: x == {'foo': 1}),
        ('{{public_data}}', lambda x: x == {'foo': 1}),
        ('{{private_data}}', lambda x: x == {'foo': 2}),
        ('{{existing_data}}', lambda x: x == {'foo': 3}),
        ('{{temporary_data}}', lambda x: x == {'foo': 4}),
        ('{{key_path}}', lambda x: x == []),
        ('{{system}}', lambda x: x == platform.system()),
        ('{{platform}}', lambda x: x == platform.platform()),
        ('{{version}}', lambda x: x == platform.version()),
        ('{{processor}}', lambda x: x == platform.processor()),
        ('{{architecture}}', lambda x: x == platform.architecture()),
        ('{{current_file}}', lambda x: x.endswith('.tackle.yaml')),
        ('{{calling_directory}}', lambda x: x.endswith('special_variables')),
        ('{{current_directory}}', lambda x: x.endswith('special_variables')),
    ],
)
def test_special_variables(special_variables_context, raw, assertion):
    """Verify Jinja2 time extension work correctly."""
    output = render_variable(special_variables_context, raw)

    assert assertion(output)


# @skip_if_not_linux
@pytest.mark.parametrize(
    "raw,assertion",
    [
        ('{{lsb_release}}', lambda x: get_linux_distribution()),
    ],
)
def test_special_variables_linux(special_variables_context, raw, assertion):
    """Verify Jinja2 time extension work correctly."""
    if sys.platform != 'linux':
        pytest.skip("skipping linux-only test")
    output = render_variable(special_variables_context, raw)
    assert assertion(output)
