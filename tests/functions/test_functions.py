import pytest
from ruamel.yaml import YAML

from tackle import tackle

FIXTURES = [
    # 'extensions.yaml',
    # 'model-function.yaml',
    'function-inline-call.yaml',
]


@pytest.mark.parametrize("fixture", FIXTURES)
def test_function_model_extraction(change_curdir_fixtures, fixture):

    output = tackle(fixture)
    print()


FIXTURES_ARGS = [
    ('model-function.yaml', ['some_function']),
]

@pytest.mark.parametrize("fixture,args", FIXTURES_ARGS)
def test_function_arguments(change_curdir_fixtures, fixture, args):

    output = tackle(fixture, *args)
    assert output


def test_create_function_model(change_curdir_fixtures):
    yaml = YAML()
    with open('model-function.yaml') as f:
        model_fixture = yaml.load(f)

    output = create_function_model('foo', model_fixture['some_function<-'])
    print()
