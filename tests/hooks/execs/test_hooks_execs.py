import pytest
from ruyaml import YAML

from tackle import tackle

FIXTURES = [
    ('exec-call.yaml', 'exec-call-output.yaml'),
    # When figuring out exactly what public vs private execs look like
    # ('exec-call-public.yaml', 'exec-call-public-output.yaml'),
]


@pytest.mark.parametrize("fixture,expected_output", FIXTURES)
def test_hooks_model_extraction(fixture, expected_output):
    """Check that the input equals output."""
    yaml = YAML()
    with open(expected_output) as f:
        expected_output_dict = yaml.load(f)

    output = tackle(fixture)
    assert output == expected_output_dict


def test_hooks_execs_no_exec():
    """
    Check that when no exec is given that by default the input is returned as is and
     validated.
    """
    output = tackle('no-exec.yaml')

    assert output['no_arg_call']['target'] == 'world'
    assert output['arg_call']['target'] == 'things'


def test_hooks_execs_hook_call_str():
    """When an exec method is a hook call vs def, parse that."""
    output = tackle('hook-call-str.yaml')

    assert output == {'bar': 'baz'}
