import pytest
from ruamel.yaml import YAML

from tackle.functions import create_function_model

FIXTURES = [
    # 'extensions.yaml',
    'model-function.yaml',
]


@pytest.mark.parametrize("fixture", FIXTURES)
def test_create_function_model(change_curdir_fixtures, fixture):
    yaml = YAML()
    with open(fixture) as f:
        model_fixture = yaml.load(f)

    output = create_function_model('foo', model_fixture)
    x = output()
    print()
