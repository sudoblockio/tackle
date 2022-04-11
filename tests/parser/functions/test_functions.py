import pytest
from ruamel.yaml import YAML

from tackle import tackle
from tackle.exceptions import FunctionCallException

FIXTURES = [
    ('call.yaml', 'call-output.yaml'),
    ('return.yaml', 'return-output.yaml'),
]


@pytest.mark.parametrize("fixture,expected_output", FIXTURES)
def test_function_model_extraction(change_curdir_fixtures, fixture, expected_output):
    yaml = YAML()
    with open(expected_output) as f:
        expected_output_dict = yaml.load(f)

    output = tackle(fixture)
    assert output == expected_output_dict


EXCEPTION_FIXTURES = [('return-str-not-found.yaml', FunctionCallException)]


@pytest.mark.parametrize("fixture,exception", EXCEPTION_FIXTURES)
def test_function_raises_exceptions(change_curdir_fixtures, fixture, exception):
    with pytest.raises(exception):
        tackle(fixture)
